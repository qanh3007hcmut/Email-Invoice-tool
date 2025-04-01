# Email-Invoice-tool
 
## Description

This project automates the process of fetching and classifying emails containing invoices. It organizes invoices by month and company, extracts relevant data, and saves the processed files to designated directories.

## Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3.  Create a `.env` file in the root directory and populate it with your email credentials:

    ```
    EMAIL_ACCOUNT="your_email@example.com"
    APP_PASSWORD="your_app_password"
    ```

    **Note:**  It's crucial to use an "App Password" instead of your regular email password for security reasons.  You can generate an App Password in your Google Account settings (or the settings for your email provider).

## Usage

The `run.py` script is the main entry point for the project. It takes the month as a command-line argument.

```bash
python run.py <month> [--clean]
``` 
#### Arguments
- `<month>`: The month for which to fetch emails (1-12).
- `--clean`: (Optional) Clears the cache before fetching emails.