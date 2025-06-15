# gitignore CLI

A simple command-line tool to automatically generate `.gitignore` files using templates from [gitignore.io](https://www.toptal.com/developers/gitignore/).

## Installation

To install and use this tool locally:

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

After installation, the `ign` command will be globally available in your terminal.


### Example: generate a .gitignore for a Node.js and React project
```bash
ign node react visualstudiocode > .gitignore
```

## License

This project is under the MIT License.
