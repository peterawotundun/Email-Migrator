import imaplib
import email
import re
from email.policy import default

# --- CONFIGURATION ---
SRC_HOST = "imappro.zoho.com"
DST_HOST = "162.255.116.111" # Using IP directly to fix connection error

def migrate_mailbox():
    print("=== Simple Email Migration Tool (Zoho -> cPanel) ===")
    
    # --- STEP 1: SOURCE VALIDATION ---
    print("\n--- 1. Source Connection (Zoho) ---")
    src_email = input("Enter Source Email (Zoho): ").strip()
    src_pass = input(f"Enter ZOHO Password for {src_email}: ").strip()
    
    print("Connecting to Source...")
    try:
        if "zohopublic" in SRC_HOST: 
             src_imap = imaplib.IMAP4_SSL(SRC_HOST)
        else:
             src_imap = imaplib.IMAP4_SSL(SRC_HOST)
        
        src_imap.login(src_email, src_pass)
        print("✅ Connected to Source (Zoho) successfully!")
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Failed to connect to Zoho: {e}")
        if "[AUTHENTICATIONFAILED]" in error_msg:
             print(f"\n  👉 ZOHO TIP: Even if your password is correct, checking 'TFA' (Two Factor Auth) is crucial.")
             print(f"     1. Log into Zoho Mail as {src_email}.")
             print(f"     2. Go to Settings -> Sessions -> App Passwords (or Account Security).")
             print(f"     3. If TFA is ON, you MUST create and use an App Password here, not the login password.")
        return

    # --- STEP 2: DESTINATION VALIDATION ---
    print("\n--- 2. Destination Connection (cPanel) ---")
    dst_email = input(f"Enter Destination Email (cPanel) [Press Enter if same as {src_email}]: ").strip()
    if not dst_email:
        dst_email = src_email
        
    dst_pass = input(f"Enter CPANEL Password for {dst_email}: ").strip()
    
    print("Connecting to Destination...")
    try:
        dst_imap = imaplib.IMAP4_SSL(DST_HOST)
        dst_imap.login(dst_email, dst_pass)
        print("✅ Connected to Destination (cPanel) successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to cPanel: {e}")
        return

    # --- STEP 3: MIGRATION ---
    print("\n--- 3. Starting Migration ---")
    print("Fetching folder list...")
    status, folders = src_imap.list()
    
    for folder_info in folders:
        # Regex to parse IMAP folder line: (Flags) "Delimiter" Name
        if not folder_info: continue
        
        decoded_info = folder_info.decode()
        match = re.search(r'\((.*?)\) "(.*?)" (.+)', decoded_info)
        
        if match:
            folder_name = match.group(3).strip()
            if folder_name.startswith('"') and folder_name.endswith('"'):
                folder_name = folder_name[1:-1]
        else:
            folder_name = decoded_info.split()[-1].strip().replace('"', '')

        if folder_name == "/": continue
            
        print(f"\n>> Migrating Folder: {folder_name}")
        
        try:
            # Select Source
            src_imap.select(f'"{folder_name}"', readonly=True)
            
            # Create/Select Destination
            try:
                dst_imap.create(f'"{folder_name}"')
            except:
                pass # Folder probably exists, which is fine
            dst_imap.select(f'"{folder_name}"')
            
            # Search for all emails
            typ, data = src_imap.search(None, 'ALL')
            msg_ids = data[0].split()
            print(f"   Found {len(msg_ids)} emails.")
            
            count = 0
            for uid in msg_ids:
                # Fetch email content
                typ, msg_data = src_imap.fetch(uid, '(RFC822 FLAGS)')
                try:
                    raw_email = msg_data[0][1]
                    # Simple append without flags to ensure compatibility
                    dst_imap.append(f'"{folder_name}"', None, None, raw_email)
                    count += 1
                    if count % 10 == 0:
                        print(f"     Synced {count}/{len(msg_ids)}...", end='\r')
                except Exception as e:
                    pass
            
            print(f"     Done. Synced {count} emails.")
            
        except Exception as e:
            print(f"   Error processing folder {folder_name}: {e}")

    # Logout
    try: src_imap.logout()
    except: pass
    try: dst_imap.logout()
    except: pass
    print("\n\n=== Migration Complete! ===")

if __name__ == "__main__":
    migrate_mailbox()
