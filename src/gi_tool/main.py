import click
import requests
import sys

# Define the base URL for the gitignore.io API
API_URL = "https://www.toptal.com/developers/gitignore/api/"

@click.command()
@click.argument('templates', nargs=-1)
def generate(templates):
    """
    Generates a .gitignore file by fetching templates from gitignore.io.
    """
    if not templates:
        click.echo("Please provide at least one template name (e.g., python, node).", err=True)
        sys.exit(1)

    try:
        # Join the template names with a comma for the API request
        url = f"{API_URL}{','.join(templates)}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Print the generated .gitignore content to standard output
        click.echo(response.text)

    except requests.exceptions.RequestException as e:
        click.echo(f"Error fetching templates: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    generate()