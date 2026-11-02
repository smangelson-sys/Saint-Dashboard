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
    key_file = io.StringIO(key_str)
    try:
        pkey = paramiko.RSAKey.from_private_key(key_file)
        print("Loaded RSA key from env var")
    except Exception as e1:
        print(f"RSA failed: {e1}, trying Ed25519...")
        key_file = io.StringIO(key_str)
        try:
            pkey = paramiko.Ed25519Key.from_private_key(key_file)
            print("Loaded Ed25519 key from env var")
        except Exception as e2:
            print(f"Ed25519 failed: {e2}, trying ECDSAKey...")
            key_file = io.StringIO(key_str)
            try:
                pkey = paramiko.ECDSAKey.from_private_key(key_file)
                print("Loaded ECDSA key from env var")
            except Exception as e3:
                print(f"All key types failed from env var. RSA: {e1}, Ed25519: {e2}, ECDSA: {e3}")
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
