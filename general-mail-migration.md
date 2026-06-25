# Universal Email Migration Tool

A powerful, terminal-based Python tool to migrate emails between ANY two IMAP-supported email providers.

## Features
- **Universal Support**: Works with Zoho, cPanel, Gmail, Outlook, GoDaddy, and custom configurations.
- **Interactive Menu**: Select common providers from a numbered list without needing to memorize names.
- **Auto-Discovery**: Pre-fills standard ports (993 for SSL) but allows manual override.
- **Smart Parsing**: Advanced folder name detection compatible with different server response formats.
- **Visual Progress**: Real-time counter and percentage display for large migrations.

## Supported Providers (Presets)
1.  **Zoho Mail** (`imappro.zoho.com`)
2.  **cPanel** (Generic - user provides `mail.domain.com` or IP)
3.  **GoDaddy** (`imap.secureserver.net`)
4.  **Gmail** (`imap.gmail.com`) - *Requires App Password*
5.  **Outlook / Office 365** (`outlook.office365.com`)
6.  **Custom** (Any IMAP server)

## How to Use

1.  **Open Terminal / PowerShell**
    Navigate to this folder:
    ```powershell
    cd "C:\Users\Peter Awotundun\Koolbuy\keys\Email Migration"
    ```

2.  **Run the Script**
    ```powershell
    python General-mail-migration.py
    ```

3.  **Follow the On-Screen Steps**:
    *   **Select Source Provider**: Choose where emails are coming FROM (e.g., Type `1` for Zoho).
    *   **Enter Credentials**: Email and Password for the source account.
    *   **Select Destination Provider**: Choose where emails are going TO (e.g., Type `2` for cPanel).
        *   *Note for cPanel:* If DNS is not fully propagated, use the Server IP address (e.g., `162.255.116.111`) as the Hostname.
    *   **Enter Credentials**: Email and Password for the destination account.

4.  **Watch it Fly**:
    The script will connect to both counters, list every folder, and transfer emails one by one with a progress bar.

## Troubleshooting Common Issues

### "Authentication Failed" or "Login Failed"
*   **Gmail**: You cannot use your normal password. You MUST enable 2-Factor Auth and generate an **App Password**.
*   **Zoho**: If 2FA is on, use an App Password.
*   **Outlook**: Modern Auth might block legacy scripts. Ensure SMTP/IMAP Auth is enabled in Admin Center.

### "Getaddrinfo failed"
*   This means the Hostname is wrong or DNS is failing.
*   **Solution**: Choose "Custom" or "cPanel" and enter the direct **IP Address** of the server instead of the domain name.

### "Certificate Verify Failed"
*   The script defaults to SSL (Port 993). Ensure your server has a valid SSL certificate.
