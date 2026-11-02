"""
Download Toast SFTP daily exports.
Runs in GitHub Actions with environment variables for config.
Downloads the last 7 days of exports (Toast keeps files for 7 days).
"""
import paramiko, os, json, io
from datetime import datetime, timedelta

SFTP_HOST = os.environ.get('SFTP_HOST', 's-9b0f88558b264dfda.server.transfer.us-east-1.amazonaws.com')
SFTP_USER = os.environ.get('SFTP_USER', 'SaintDataExportUser')
SFTP_KEY_DATA = os.environ.get('SFTP_KEY_DATA', '')  # Key content from env var
SFTP_KEY_FILE = os.path.expanduser(os.environ.get('SFTP_KEY', '~/.ssh/toast_key'))
EXPORT_ID = os.environ.get('EXPORT_ID', '321496')
DATA_DIR = 'data/exports'

os.makedirs(DATA_DIR, exist_ok=True)

# Load tracking file to skip already-downloaded dates
tracking_file = 'data/downloaded_dates.json'
downloaded = set()
if os.path.exists(tracking_file):
    with open(tracking_file) as f:
        downloaded = set(json.load(f))

print(f"Connecting to {SFTP_HOST} as {SFTP_USER}...")

# Load SSH key - prefer env var (avoids file corruption), fall back to file
pkey = None
if SFTP_KEY_DATA:
    print("Loading SSH key from environment variable...")
    key_str = SFTP_KEY_DATA.strip()
    print(f"Key length: {len(key_str)}, starts with: {key_str[:30]}...")

    # GitHub Actions may strip newlines from secrets passed as env vars
    # Reconstruct proper OPENSSH key format if newlines are missing
    if '\n' not in key_str and '-----BEGIN' in key_str:
        print("Key has no newlines - reconstructing format...")
        # Extract the header, base64 body, and footer
        key_str = key_str.replace('-----BEGIN OPENSSH PRIVATE KEY-----', '')
        key_str = key_str.replace('-----END OPENSSH PRIVATE KEY-----', '')
        body = key_str.strip()
        # Re-wrap base64 body at 70 chars per line
        lines = [body[i:i+70] for i in range(0, len(body), 70)]
        key_str = '-----BEGIN OPENSSH PRIVATE KEY-----\n' + '\n'.join(lines) + '\n-----END OPENSSH PRIVATE KEY-----\n'
        print(f"Reconstructed key: {len(key_str)} bytes, {key_str.count(chr(10))} newlines")

    # Use cryptography library to parse OPENSSH format and convert to PEM
    from cryptography.hazmat.primitives import serialization
    key_bytes = key_str.encode('utf-8')
    try:
        private_key = serialization.load_ssh_private_key(key_bytes, password=None)
        pem_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        pem_str = pem_bytes.decode('utf-8')
        print(f"Converted key to PEM format ({len(pem_str)} bytes)")
        pkey = paramiko.RSAKey.from_private_key(io.StringIO(pem_str))
        print("Loaded RSA key from env var (via PEM conversion)")
    except Exception as e:
        print(f"Key loading failed: {e}")
        raise

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

if pkey:
    client.connect(SFTP_HOST, username=SFTP_USER, pkey=pkey)
else:
    print(f"Loading SSH key from file: {SFTP_KEY_FILE}")
    client.connect(SFTP_HOST, username=SFTP_USER, key_filename=SFTP_KEY_FILE)

sftp = client.open_sftp()

# Navigate to restaurant export directory
try:
    sftp.chdir(EXPORT_ID)
except:
    # Try listing root to find the right directory
    print("Available directories:", sftp.listdir('.'))
    sftp.chdir(EXPORT_ID)

# List available date directories
dates = []
for entry in sftp.listdir('.'):
    try:
        sftp.stat(entry)
        if len(entry) == 8 and entry.isdigit():
            dates.append(entry)
    except:
        pass

dates.sort()
print(f"Available dates on server: {dates}")

new_dates = [d for d in dates if d not in downloaded]
print(f"New dates to download: {new_dates}")

for date_dir in new_dates:
    local_dir = os.path.join(DATA_DIR, date_dir)
    os.makedirs(local_dir, exist_ok=True)
    
    sftp.chdir(f'/{EXPORT_ID}/{date_dir}')
    files = sftp.listdir('.')
    print(f"  {date_dir}: {len(files)} files")
    
    for fname in files:
        remote_path = fname
        local_path = os.path.join(local_dir, fname)
        try:
            sftp.get(remote_path, local_path)
        except Exception as e:
            print(f"    Error downloading {fname}: {e}")
    
    downloaded.add(date_dir)

sftp.close()
client.close()

# Save tracking
with open(tracking_file, 'w') as f:
    json.dump(sorted(downloaded), f)

print(f"Done. Total dates in archive: {len(downloaded)}")
