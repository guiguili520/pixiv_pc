# GEMINI.md

This file provides a comprehensive overview of the Pixiv Illustration Crawler project, intended to be used as instructional context for Gemini.

## Project Overview

This is a Python-based command-line tool for downloading illustrations from the art community Pixiv. It allows users to search for illustrations by keyword or fetch popular illustrations from Pixiv's rankings (daily, weekly, monthly).

The project is structured into a `src` directory containing the core logic, a `main.py` entrypoint, and a `config.yaml` for user-defined settings.

**Key Technologies:**
*   Python 3
*   Libraries: `requests` (for HTTP requests), `BeautifulSoup4` (for HTML parsing), `PyYAML` (for configuration), `tqdm` (for progress bars).

**Architecture:**
*   `main.py`: The main entry point of the application. It uses `argparse` to handle command-line arguments and orchestrates the crawling process.
*   `config.yaml`: A user-configurable file for settings like download directories, request timeouts, and proxy settings.
*   `src/config/config.py`: A module to load and manage the settings from `config.yaml`.
*   `src/crawler/pixiv_api.py`: A module that encapsulates the logic for interacting with Pixiv's internal API, including searching and fetching rankings.
*   `src/crawler/downloader.py`: A module responsible for downloading the actual illustration files.
*   `src/utils/logger.py`: A utility for logging application events.

## Building and Running

### 1. Installation

It is recommended to use a virtual environment.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Application

The main script is `main.py`. The application is controlled via command-line arguments.

**Common Commands:**

*   **Search for illustrations by keyword:**
    ```bash
    python main.py search "your keyword"
    ```

*   **Fetch illustrations from the monthly ranking:**
    ```bash
    python main.py ranking --mode monthly
    ```

*   **Generate the default configuration file:**
    ```bash
    python main.py config --generate
    ```

### 3. Testing

There are no dedicated test files in the project. Functionality can be verified by running the commands listed above.

## Development Conventions

*   **Code Style:** The code generally follows PEP 8 conventions for Python.
*   **Modularity:** The project is organized into modules with distinct responsibilities (configuration, API interaction, downloading, utilities).
*   **Configuration:** Application settings are externalized to `config.yaml`, which is a good practice.
*   **Error Handling:** The application includes `try...except` blocks to handle potential errors during execution and provides informative log messages.
*   **Logging:** A dedicated logging module is used to provide detailed logs, which are saved to the `logs/` directory.
