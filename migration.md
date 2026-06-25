# Email Migration Guide

This guide explains how to use the `email_migration.py` script to migrate email accounts from Zoho to cPanel (Koolboks).

## Prerequisites
- You must have **Python** installed on your Windows computer.
- You must have the **password for the source email (Zoho)**.
- You must have the **password for the destination email (cPanel)**.

## How to Run the Migration

1.  **Open PowerShell** or Command Prompt.
2.  **Navigate to the folder**:
    ```powershell
    cd "C:\Users\Peter Awotundun\Koolbuy\keys\Email Migration"
    ```
3.  **Run the script**:
    ```powershell
    python email_migration.py
    ```

4.  **Follow the Prompts**:
    -   **Source Email (Zoho):** Enter the email address you are migrating (e.g., `user@koolboks.com`).
    -   **Zoho Password:** Enter the password for that email account on Zoho.
    -   **Destination Email (cPanel):** If it's the exact same email address, just press **Enter**. If it's different, type the new email address.
    -   **cPanel Password:** Enter the password for the email account on the new cPanel server.

5.  **Wait for Completion**:
    -   The script will connect to both servers.
    -   It will list and migrate all folders (Inbox, Sent, Drafts, etc.).
    -   It will show you the progress for each folder.
    -   Wait until you see `=== Migration Complete! ===`.

## Troubleshooting

-   **Connection Error (`getaddrinfo failed`)**: This usually means a DNS issue. The script is currently hardcoded to use the IP `162.255.116.111` for the destination to avoid this. If the IP changes, update the `DST_HOST` variable in the script.
-   **Authentication Failed**: Double-check that you are using the *email account password*, not your cPanel/hosting login password.
