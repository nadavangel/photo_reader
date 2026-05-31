# Split To Wells

A Python application for splitting microscope images from Spinning-Disc and Eva microscope outputs into individual well folders. Supports both command-line and graphical user interfaces.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Runtime Requirements](#runtime-requirements)
- [Usage](#usage)
  - [GUI Mode](#gui-mode)
  - [CLI Mode](#cli-mode)
- [Building Standalone Executables](#building-standalone-executables)
- [Platform-Specific Notes](#platform-specific-notes)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- Split microscope images into individual well folders
- Support for material/well name mapping
- File prefix customization
- Optional subdirectory creation
- Both GUI and CLI interfaces
- Cross-platform support (Windows, macOS, Linux)
- Comprehensive logging with debug mode

## Installation

### Prerequisites

- Python 3.7 or higher
- tkinter (usually included with Python)

### Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/nadavangel/photo_reader.git
cd photo_reader
```

2. No additional dependencies are required! The application uses only Python standard library packages.

### Optional: Create a Virtual Environment

It's recommended to use a virtual environment:

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

## Runtime Requirements

### Core Requirements
- Python 3.7+
- tkinter (usually included with Python)

### Platform-Specific Installation

#### macOS
If you don't have tkinter installed:
```bash
# Using Homebrew:
brew install python-tk@3.11  # Replace 3.11 with your Python version

# Or using conda:
conda install tk
```

#### Windows
tkinter is included with the standard Python installer. No additional installation needed.

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install python3-tk
```

#### Linux (Fedora/RHEL)
```bash
sudo dnf install python3-tkinter
```

## Usage

### GUI Mode

Launch the graphical user interface:

```bash
python window.py
```

**GUI Features:**
- Browse and select source folder (plate/Spinning disc images)
- Browse and select destination folder for output
- Enter a name/prefix for output files
- Optionally provide material info with well names
- Toggle subdirectory creation
- Set file prefix for output files
- Progress bar during processing
- Automatic configuration persistence (stored in `.config.ini`)
- Debug logging to file (SplitToWells.log)

**Keyboard Shortcuts:**
- `Ctrl+A` - Select all (works in text fields)
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Ctrl+X` - Cut

### CLI Mode

Run the command-line interface with various options:

```bash
python splitToWells.py [OPTIONS]
```

**Options:**

- `-f, --folder PATH` - Source folder (plate/Spinning disc)
- `-d, --dest PATH` - Destination folder for output
- `-n, --name TEXT` - Name/prefix for the output files
- `-m, --material TEXT` - Material info with well names (tab-separated: position<TAB>name)
- `-p, --file-prefix TEXT` - File prefix for output files
- `--no-subdir` - Do not create subdirectories for each position
- `-v, --verbose` - Enable debug logging output

**CLI Examples:**

Basic usage (interactive stdin prompts):
```bash
python splitToWells.py
```
The application will prompt you to enter paths and settings via stdin.

With all parameters specified:
```bash
python splitToWells.py -f "/path/to/source" -d "/path/to/dest" -n "experiment_01" -p "img_"
```

With material information:
```bash
python splitToWells.py -f "/path/to/source" -d "/path/to/dest" -m "A1	control" --verbose
```

Without creating subdirectories:
```bash
python splitToWells.py -f "/path/to/source" -d "/path/to/dest" --no-subdir -n "flat_output"
```

**CLI and GUI Feature Parity:**

Both the CLI and GUI provide equivalent functionality:

| Feature | CLI | GUI |
|---------|-----|-----|
| Source folder selection | `-f, --folder` or stdin prompt | Browse button |
| Destination folder | `-d, --dest` or stdin prompt | Browse button |
| Output name/prefix | `-n, --name` | Name field |
| Material/well mapping | `-m, --material` | Material info text area |
| File prefix | `-p, --file-prefix` | File prefix field |
| Subdirectory creation | `--no-subdir` (disable) | Create subdir checkbox (enabled by default) |
| Debug logging | `-v, --verbose` (stdout) | SplitToWells.log file (created automatically) |
| Interactive mode | Full stdin prompts | N/A |

**CLI Interactive Mode:**

When running `python splitToWells.py` without options, the CLI will prompt you for input via stdin:

```
Please select source (plate/Spinning disc) folder:
Please select destination folder:
```

Simply provide the paths when prompted.

## Building Standalone Executables

### Prerequisites

Install build dependencies:

```bash
pip install -r requirements-build.txt
```

### Build Instructions

#### Using PyInstaller Spec File (Recommended)

```bash
pyinstaller splitToWells.spec
```

#### Manual PyInstaller Command

```bash
pyinstaller --clean -F -i="microscope.ico" --name splitToWells window.py
```

The executable will be created in the `dist/` folder.

### Creating a Release

1. Build the executable (see above)
2. Create a new release on GitHub
3. Upload the executable from the `dist/` folder
4. Tag the release with version information

## Platform-Specific Notes

### macOS

**Installation:**
- Ensure Python 3.7+ is installed
- Install tkinter if needed: `brew install python-tk@3.11`

**Running the Application:**
```bash
python window.py      # GUI mode
python splitToWells.py  # CLI mode
```

**Building Executables:**
The PyInstaller build process works the same as on other platforms:
```bash
pip install -r requirements-build.txt
pyinstaller splitToWells.spec
```

**Troubleshooting macOS:**
- If tkinter is not found, try installing via Homebrew or conda
- Ensure you're using the correct Python version (check with `python --version`)

### Windows

**Installation:**
- Standard Python installer includes tkinter
- No additional installation needed

**Running the Application:**
```bash
python window.py      # GUI mode
python splitToWells.py  # CLI mode
```

**Building Executables:**
```bash
pip install -r requirements-build.txt
pyinstaller splitToWells.spec
```

The executable will be in `dist\splitToWells.exe`

### Linux

**Installation:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter
```

**Running the Application:**
```bash
python3 window.py      # GUI mode
python3 splitToWells.py  # CLI mode
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** on GitHub
2. **Create a feature branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and test them thoroughly
4. **Commit with clear messages**:
   ```bash
   git commit -m "Add descriptive commit message"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** with a clear description of your changes

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/photo_reader.git
cd photo_reader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pre-commit

# Install pre-commit hooks
pre-commit install
```

### Code Style

- Follow PEP 8 conventions
- Use meaningful variable and function names
- Add comments for complex logic
- Test your changes before submitting a PR

## Troubleshooting

### Common Issues

#### tkinter not found
**Problem:** `ModuleNotFoundError: No module named 'tkinter'`

**Solution:**
- **macOS:** `brew install python-tk@3.11` (replace 3.11 with your Python version)
- **Ubuntu/Debian:** `sudo apt-get install python3-tk`
- **Fedora/RHEL:** `sudo dnf install python3-tkinter`
- **Windows:** Reinstall Python and ensure tkinter is selected

#### No source/destination folder selected
**Problem:** Application exits or shows error "No source folder was selected"

**Solution:**
- In GUI mode: Use the Browse buttons to select folders
- In CLI mode: Provide `-f` and `-d` arguments, or respond to stdin interactive prompts
- Ensure the folders exist and have read/write permissions

#### File permission errors
**Problem:** "Permission denied" when writing to destination folder

**Solution:**
- Ensure the destination folder exists
- Check that you have write permissions to the destination folder
- Try running as administrator (Windows) or with sudo (macOS/Linux) if appropriate

#### Material info parsing errors
**Problem:** Error parsing material info

**Solution:**
- Ensure material info is tab-separated (use actual tab character, not spaces)
- Format: `position<TAB>name` per line
- Example: `A1<TAB>control` (replace `<TAB>` with actual tab)

#### Progress bar freezes (GUI)
**Problem:** GUI appears frozen during processing

**Solution:**
- This is normal! The application is processing. Wait for completion.
- Processing time depends on the number and size of images
- The "Done" dialog will appear when processing is complete

#### Slow performance
**Problem:** Processing takes a long time

**Solution:**
- This is normal for large image sets
- Processing time depends on:
  - Number of images
  - Image size
  - Disk I/O speed
  - System resources
- Consider running on a machine with an SSD for faster I/O

### Debug Mode

Enable verbose logging to troubleshoot issues:

```bash
# CLI mode with debug logging:
python splitToWells.py -v

# GUI mode debug logging:
# Debug logs are automatically saved to SplitToWells.log in the current directory
```

Check the log file `SplitToWells.log` (created in the application directory) for detailed error information. In GUI mode, this file is created and updated every time you run the application. In CLI mode, use the `-v` flag to enable verbose output to stdout.

## License

This project is licensed under the terms specified in the LICENSE file.
