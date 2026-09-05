# prices-stats

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**prices-stats** is a minimalistic, cross-platform desktop application designed to calculate minimum, maximum, and median prices for custom product lists, with seamless Excel reporting capabilities.

---

## Features

* **Minimalist & Native UI:** Clean graphical interface adapted to your system's native theme.
* **Full Keyboard Navigation:** Engineered for maximum efficiency: navigate, input data, and manage items entirely without a mouse.
* **Formatted Excel Export:** Export product data and auto-styled statistical summaries (min, max, median) into `.xlsx` spreadsheets with a single click.
* **High Scalability:** Add as many products as your hardware resources allow.
* **Cross-Platform:** Available as standalone pre-compiled binaries for Windows and Linux.

---

## Download & Installation

The easiest way to use **prices-stats** is to download the pre-compiled binary for your operating system from the **[Latest Release](https://github.com/AmonRadii/prices-stats/releases/latest)** page.

### Linux

* **Debian / Ubuntu (.deb package):**

  Download the `.deb` file from Releases and install it via terminal:

    ```bash
     sudo dpkg -i prices-stats_1.0.0_amd64.deb
    ```

* **Standalone Binary:**

    Download the executable file, grant execution permissions, and run:

    ```bash
     chmod +x prices-stats
     ./prices-stats
    ``` 

### Windows

* **Executable (.exe):**

    Download `prices-stats.exe` from the Releases section and double-click to run. No installation required.

### Running from Source

If you prefer to run the application directly from source code, ensure you have Python installed.

### Dependencies

* **Python:** >= 3.11
* **PySide6:** >= 6.11.1
* **openpyxl:** >= 3.1.5

### Setup with uv (Recommended)

1. Clone the repository and navigate into it:

    ```bash
     git clone [https://github.com/AmonRadii/prices-stats.git](https://github.com/AmonRadii/prices-stats.git)
     cd prices-stats
    ```

2. Run the application:

    ```bash
     uv run src/main.py
    ```

### Setup with pip

1. Clone the repository and navigate into it:

    ```bash
     git clone [https://github.com/AmonRadii/prices-stats.git](https://github.com/AmonRadii/prices-stats.git)
     cd prices-stats
    ```

2. Create and activate a virtual environment:

    ```bash
     python3 -m venv .venv
     source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
     pip install openpyxl "pyside6-essentials>=6.11.1"
    ```

4. Launch the app:

    ```bash
     python src/main.py
    ```

---

## Keyboard Shortcuts

* **Up / Down / Left / Right:** Navigate between input fields, buttons, and the item list.
* **Enter / Return:** Add item / move to price field..
* **Delete:** Remove selected product from the list.
* **Ctrl + S:** Quick-save report to Excel.
* **Escape:** Close application.

---

## License

MIT License.