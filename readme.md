# gitignore CLI

A simple command-line tool to automatically generate `.gitignore` files using templates from [gitignore.io](https://www.toptal.com/developers/gitignore/).

## Installation

Requires Python 3.9+.

### 1. Clone the repository
```bash
git clone https://github.com/ric-monteiro/gitignore-cli.git
```

### 2. Navigate to the folder
```bash
cd gitignore-cli
```

### 3. Install in editable mode
```bash
pip install -e .
```

## Usage

After installation, the `ign` command will be available in your terminal.

### Generate a .gitignore for a Node.js and React project
```bash
ign node react visualstudiocode -o .gitignore
```

`-o/--output` always writes UTF-8 with LF line endings and refuses to overwrite an existing file. Use `--force` to replace it, or `--append` to add templates to it:

```bash
ign go -o .gitignore --append
```

Template names can also be comma-separated (`ign node,react`), and printing to standard output still works (`ign python > .gitignore`).

> **Windows / PowerShell 5:** prefer `-o` over `>`. PowerShell 5 redirects output as UTF-16, which Git cannot read, so the resulting `.gitignore` is silently ignored.

### Find templates
```bash
ign --list          # all available templates
ign --list java     # templates whose name contains "java"
```

### Other options
```
-h, --help     Show help
-V, --version  Show version
```

## Development

```bash
pip install -e ".[test]"
pytest
```

## License

This project is under the MIT License.
