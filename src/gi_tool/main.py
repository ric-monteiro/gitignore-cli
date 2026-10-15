import re

import click
import requests

from gi_tool import __version__

# Define the base URL for the gitignore.io API
API_URL = "https://www.toptal.com/developers/gitignore/api/"

# Seconds to wait for the API before giving up
TIMEOUT = 15

# Every template name on gitignore.io matches this (e.g. "python", "c++", "1c-bitrix").
# Validating input keeps arbitrary path/query characters out of the request URL.
TEMPLATE_RE = re.compile(r"^[a-z0-9][a-z0-9+._-]*$")

# gitignore.io reports unknown templates inside the response body
ERROR_RE = re.compile(r"^#!! ERROR: (\S+) is undefined\..*!!#$", re.MULTILINE)


def fetch(path):
    """GET a path under the API and return the response body as text."""
    try:
        response = requests.get(
            API_URL + path,
            timeout=TIMEOUT,
            headers={"User-Agent": f"gitignore-generator-cli/{__version__}"},
        )
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"Could not reach gitignore.io: {e}")

    response.encoding = "utf-8"
    text = response.text

    unknown = ERROR_RE.findall(text)
    if unknown:
        raise click.ClickException(
            f"Unknown template(s): {', '.join(unknown)}. "
            "Run 'ign --list' to see the available templates."
        )
    if not response.ok:
        raise click.ClickException(
            f"gitignore.io returned HTTP {response.status_code} {response.reason}"
        )
    return text


def normalize(templates):
    """Lowercase, split comma-separated names, drop duplicates and validate."""
    names = []
    for arg in templates:
        for name in arg.lower().split(","):
            name = name.strip()
            if not name or name in names:
                continue
            if not TEMPLATE_RE.match(name):
                raise click.BadParameter(f"invalid template name: {name!r}", param_hint="TEMPLATES")
            names.append(name)
    return names


def write_output(path, content, append, force):
    """Write content to path as UTF-8 with LF line endings."""
    try:
        if append:
            with open(path, "a+", encoding="utf-8", newline="\n") as f:
                # Separate from existing content that doesn't end with a newline
                f.seek(0)
                existing = f.read()
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write(content)
        else:
            # "x" refuses to clobber an existing file unless --force was given
            with open(path, "w" if force else "x", encoding="utf-8", newline="\n") as f:
                f.write(content)
    except FileExistsError:
        raise click.ClickException(f"{path} already exists. Use --force to overwrite or --append to add to it.")
    except OSError as e:
        raise click.ClickException(f"Could not write {path}: {e.strerror}")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("templates", nargs=-1)
@click.option("-l", "--list", "list_templates", is_flag=True,
              help="List available templates, optionally filtered by TEMPLATES.")
@click.option("-o", "--output", type=click.Path(dir_okay=False, writable=True),
              help="Write to a file (UTF-8) instead of standard output.")
@click.option("-a", "--append", is_flag=True, help="Append to the --output file.")
@click.option("-f", "--force", is_flag=True, help="Overwrite the --output file if it exists.")
@click.version_option(__version__, "-V", "--version", prog_name="ign")
def generate(templates, list_templates, output, append, force):
    """
    Generates a .gitignore file by fetching templates from gitignore.io.

    \b
    Examples:
      ign python venv visualstudiocode -o .gitignore
      ign node,react >> .gitignore
      ign --list java
    """
    if list_templates:
        available = fetch("list?format=lines").split()
        filters = [t.lower() for t in templates]
        for name in available:
            if not filters or any(f in name for f in filters):
                click.echo(name)
        return

    if (append or force) and not output:
        raise click.UsageError("--append and --force require --output.")
    if append and force:
        raise click.UsageError("--append and --force are mutually exclusive.")

    names = normalize(templates)
    if not names:
        raise click.UsageError("Please provide at least one template name (e.g., python, node).")

    # Join the template names with a comma for the API request
    content = fetch(",".join(names))

    if output:
        write_output(output, content, append, force)
        click.echo(f"Wrote {', '.join(names)} template(s) to {output}", err=True)
    else:
        # Print the generated .gitignore content to standard output
        click.echo(content, nl=False)


if __name__ == "__main__":
    generate()
