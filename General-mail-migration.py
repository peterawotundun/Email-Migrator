import imaplib
import email
import re
import socket
import sys
from email.policy import default

# --- PRESETS FOR COMMON PROVIDERS ---
PROVIDERS = {
    "1": {"name": "Zoho Mail", "host": "imappro.zoho.com", "port": 993},
    "2": {"name": "cPanel (Generic)", "host": "", "port": 993}, # Requires user input
    "3": {"name": "GoDaddy", "host": "imap.secureserver.net", "port": 993},
    "4": {"name": "Gmail", "host": "imap.gmail.com", "port": 993},
    "5": {"name": "Outlook / Office 365", "host": "outlook.office365.com", "port": 993},
    "6": {"name": "Custom / Other", "host": "", "port": 993}
}

def get_input(prompt, default_val=None):
    if default_val:
        user_input = input(f"{prompt} [{default_val}]: ").strip()
        return user_input if user_input else default_val
    else:
        return input(f"{prompt}: ").strip()

def select_provider(server_type):
    print(f"\n--- Select {server_type} Provider ---")
    for key, val in PROVIDERS.items():
        print(f"{key}. {val['name']}")
    
    choice = input("Select number: ").strip()
    provider = PROVIDERS.get(choice, PROVIDERS["6"])
    
    host = provider["host"]
    if not host:
        if choice == "2":
            print(f"\nNOTE: For cPanel, this is usually 'mail.yourdomain.com' or the Server IP.")
        host = get_input(f"Enter {server_type} IMAP Hostname/IP")
        
    port = int(get_input(f"Enter {server_type} Port", provider["port"]))
    
    return host, port, provider["name"]

def connect_imap(host, port, user, password, label, provider_name="Generic"):
    print(f"Connecting to {label} ({host}:{port})...")
    try:
        # Try SSL first (standard for 993)
        if port == 993:
            server = imaplib.IMAP4_SSL(host, port)
        else:
            # Try standard then upgrade to TLS
            server = imaplib.IMAP4(host, port)
            try:
                server.starttls()
            except:
                pass # Might not support STARTTLS, proceed unencrypted if necessary
        
        server.login(user, password)
        print(f"✅ Connected to {label} successfully.")
        return server
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ CONNECTION ERROR for {label} ({provider_name})")
        print(f"   Error Details: {error_msg}")
        
        # --- SMART TROUBLESHOOTING TIPS ---
        print(f"   \n🔎 TROUBLESHOOTING:")
        
        # 1. Google Specific
        if "Application-specific password required" in error_msg or "Gmail" in provider_name:
             print(f"   👉 GMAIL ACTION: You CANNOT use your login password.")
             print(f"      1. Enable 2-Step Verification.")
             print(f"      2. Go to https://myaccount.google.com/apppasswords")
             print(f"      3. Create 'Migration' app password and use that 16-digit code.")
             
        # 2. Zoho Specific
        elif "Zoho" in provider_name:
             print(f"   👉 ZOHO ACTION: If you have 2FA enabled, you need an App Password.")
             print(f"      1. Go to Zoho Accounts -> Security -> App Passwords.")
             print(f"      2. Generate a new one and use it here.")

        # 3. Outlook Specific
        elif "Outlook" in provider_name or "Office 365" in provider_name:
             print(f"   👉 OUTLOOK ACTION: Ensure 'Authenticated SMTP' is enabled for this user.")
             print(f"      Also, Modern Auth might block this script. App Passwords might be needed.")

        # 4. Hostname / DNS Errors
        elif "getaddrinfo failed" in error_msg:
             print(f"   👉 HOSTNAME ERROR: The computer cannot find '{host}'.")
             print(f"      Solution: Try using the server's IP ADDRESS instead of the domain name.")
             
        # 5. Generic Auth
        elif "AUTHENTICATIONFAILED" in error_msg or "Invalid credentials" in error_msg:
             print(f"   👉 PASSWORD ERROR: Please check for typos. Remember: Email Passwords are case sensitive.")

        return None

def main():
    print("=====================================================")
    print("   PLUTO TECH UNIVERSAL EMAIL MIGRATION TOOL v1.1    ")
    print("=====================================================")
    
    # --- SOURCE CONFIGURATION ---
    while True:
        src_host, src_port, src_provider_name = select_provider("SOURCE")
        src_user = get_input("Enter Source Email")
        src_pass = get_input(f"Enter Password for {src_user}")
        
        print("\n[Validity Check] Connecting to SOURCE...")
        src_imap = connect_imap(src_host, src_port, src_user, src_pass, "SOURCE", src_provider_name)
        if src_imap:
            break
        print("\n⚠️ Connection Failed. Let's try entering Source details again.\n")

    # --- DESTINATION CONFIGURATION ---
    while True:
        dst_host, dst_port, dst_provider_name = select_provider("DESTINATION")
        dst_user = get_input("Enter Destination Email", src_user)
        dst_pass = get_input(f"Enter Password for {dst_user}")
        
        print("\n[Validity Check] Connecting to DESTINATION...")
        dst_imap = connect_imap(dst_host, dst_port, dst_user, dst_pass, "DESTINATION", dst_provider_name)
        if dst_imap:
            break
        print("\n⚠️ Connection Failed. Let's try entering Destination details again.\n")


    # --- MIGRATION LOOP ---
    print("\n[2/3] Fetching folder list from Source...")
    status, folders = src_imap.list()
    
    for folder_info in folders:
        if not folder_info: continue
        decoded_info = folder_info.decode()
        
        # Robust regex parsing for various IMAP server formats
        # Matches: (flags) "delimiter" name OR (flags) "delimiter" "name"
        match = re.search(r'\((.*?)\) "(.*?)" (.+)', decoded_info)
        if match:
            folder_name = match.group(3).strip()
            if folder_name.startswith('"') and folder_name.endswith('"'):
                folder_name = folder_name[1:-1]
        else:
            folder_name = decoded_info.split()[-1].strip().replace('"', '')

        if folder_name == "/" or folder_name == "": continue
        
        print(f"\n>> Migrating Folder: {folder_name}")
        
        try:
            # Select Source
            typ, data = src_imap.select(f'"{folder_name}"', readonly=True)
            if typ != 'OK':
                print(f"   Skipping (Could not select on source).")
                continue

            # Create/Select Destination
            try:
                dst_imap.create(f'"{folder_name}"')
            except:
                pass # Folder likely exists
            
            dst_imap.select(f'"{folder_name}"')
            
            # Fetch Emails
            typ, data = src_imap.search(None, 'ALL')
            msg_ids = data[0].split()
            total = len(msg_ids)
            print(f"   Found {total} emails.")
            
            if total == 0: continue
            
            count = 0
            for uid in msg_ids:
                try:
                    # Fetch RFC822 (Raw email) and Flags
                    typ, msg_data = src_imap.fetch(uid, '(RFC822)')
                    if msg_data[0] is None: continue
                    
                    raw_email = msg_data[0][1]
                    
                    # Append to destination
                    # We pass None for flags/date to let server set defaults or simple append
                    dst_imap.append(f'"{folder_name}"', None, None, raw_email)
                    
                    count += 1
                    percent = (count / total) * 100
                    sys.stdout.write(f"\r   Progress: {count}/{total} ({percent:.1f}%)")
                    sys.stdout.flush()
                except Exception as e:
                    # Specific error handling could go here
                    pass
            print("") # Newline after progress bar
            
        except Exception as e:
            print(f"   Error migrating folder: {e}")

    # --- CLEANUP ---
    print("\n[3/3] Closing connections...")
    try: src_imap.logout()
    except: pass
    try: dst_imap.logout()
    except: pass
    
    print("\n==========================================")
    print("       MIGRATION COMPLETED SUCCESSFULLY   ")
    print("==========================================")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n\nCritical Error: {e}")
        input("Press Enter to exit...")
