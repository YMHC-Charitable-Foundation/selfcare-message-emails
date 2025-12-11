# Daily Message of Support

This repository contains a Python script that sends a daily email with a supportive message, self-care activities, and a featured resource. It is designed to run automatically using GitHub Actions.

## Setup Instructions

To get this running on your own GitHub repository, you need to configure the necessary **Secrets** and **Variables**.

### Option 1: Using Repository Secrets (Recommended for Simplicity)
This is the easiest way to get it working.

1.  Go to your GitHub Repository.
2.  Click on **Settings** > **Secrets and variables** > **Actions**.
3.  Under **Repository secrets**, click **New repository secret**. Add the following:
    *   `EMAIL_HOST`: Your SMTP server (e.g., `smtp.gmail.com`).
    *   `EMAIL_PORT`: Your SMTP port (e.g., `587`).
    *   `EMAIL_USER`: Your email address.
    *   `EMAIL_PASSWORD`: Your email password or App Password.
    *   `RECIPIENT_EMAIL`: The email address (or comma-separated list) to receive the message.
4.  **Important**: If you decide to use Repository secrets, you should edit `.github/workflows/daily_email.yml` and **remove** (or comment out) the line:
    ```yaml
    environment: selfcare-message-emails
    ```
    And ensure `RECIPIENT_EMAIL` is referenced as `${{ secrets.RECIPIENT_EMAIL }}` in the workflow file if it is a secret, or `${{ vars.RECIPIENT_EMAIL }}` if it is a variable.

### Option 2: Using Environments (Current Configuration)
If you prefer using an "Environment" (which allows for things like approval protection):

1.  Go to **Settings** > **Environments**.
2.  Create an environment named exactly: `selfcare-message-emails`.
3.  Inside this environment, add the **Environment secrets**:
    *   `EMAIL_HOST`
    *   `EMAIL_PORT`
    *   `EMAIL_USER`
    *   `EMAIL_PASSWORD`
4.  Inside this environment, add the **Environment variables**:
    *   `RECIPIENT_EMAIL` (Note: Variables are visible in plain text).

## Troubleshooting

-   **"Error: Missing environment variables"**: The script could not find one of the required values. Check the Action logs to see exactly which one is missing.
-   **Workflow Succeeded but no email?**: Check if the script printed an error but didn't fail the build (we fixed this recently).
-   **Authentication Errors**: If using Gmail, you likely need to create an **App Password** instead of using your main password.

## Local Development
1.  Create a `.env` file based on `.env.example`.
2.  Run `pip install -r requirements.txt`.
3.  Run `python daily_email.py`.
