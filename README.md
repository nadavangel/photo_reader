# Split To Wells

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/nadavangel/photo_reader/actions/workflows/tests.yml/badge.svg)](https://github.com/nadavangel/photo_reader/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/nadavangel/photo_reader/graph/badge.svg)](https://codecov.io/gh/nadavangel/photo_reader)

A modern, high-performance Python application for splitting microscope images (Spinning-Disc, Eva, etc.) into individual well folders. Featuring a completely redesigned GUI and high-speed parallel processing.

## 🚀 Key Features

- **Modern GUI:** Built with `CustomTkinter` for a sleek, modern look with Dark/Light mode support.
- **Parallel Processing:** Multi-threaded file operations for rapid splitting of large datasets.
- **Real-time Status:** Integrated console in the GUI providing live feedback on the splitting process.
- **Flexible Mapping:** Support for custom well-to-material name mapping.
- **Cross-Platform:** Runs seamlessly on Windows, macOS, and Linux.
- **CLI Power:** Full-featured command-line interface for automation and headless environments.

## 📦 Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nadavangel/photo_reader.git
   cd photo_reader
   ```

2. **Sync dependencies:**
   ```bash
   uv sync
   ```

## 🖥️ Usage

### Graphical User Interface (GUI)
Launch the modern interface:
```bash
uv run python window.py
```
*   **Source Folder:** Select where your microscope images are stored.
*   **Destination Folder:** Choose where the organized output should go.
*   **Execution Settings:** Configure output naming, file prefixes, and thread count.
*   **Material Mapping:** Optionally provide a list of well positions and names (Tab-separated).

### Command Line Interface (CLI)
Run for quick operations or scripting:
```bash
uv run python split_to_wells.py [OPTIONS]
```
**Common Options:**
- `-f, --folder PATH` - Source folder path.
- `-d, --dest PATH` - Destination folder path.
- `-n, --name TEXT` - Output name/prefix.
- `-t, --threads INT` - Number of threads (default: 1).
- `-v, --verbose` - Enable debug logging.

## 🛠️ Development

Install pre-commit hooks to maintain code quality:
```bash
uv run pre-commit install
```

Run tests with coverage:
```bash
uv run pytest
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
