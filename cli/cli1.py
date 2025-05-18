import os
import shutil
import time
import tempfile
import threading
import requests
import zipfile
import argparse
from urllib.parse import urlparse, unquote
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from model import check_steghide
from plyer import notification

# Constants
PASS_PHRASE = "secret123"
DOWNLOADS_DIR = os.path.expanduser(r"C:\Users\Samarthsuhas\Downloads")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".ico"}

# === Part 1: Helpers for dfile and dzip ===
def sanitize_filename(url):
    path = urlparse(url).path
    filename = os.path.basename(path)
    filename = unquote(filename).split('?')[0]
    return filename if filename else "downloaded_file"

def notify_user(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=5  # notification stays for 10 seconds
    )

def download_file_to_sandbox(url, passphrase=PASS_PHRASE):
    sandbox_dir = tempfile.mkdtemp(prefix="sandbox_")
    print(f"[+] Sandbox created at: {sandbox_dir}")

    try:
        filename = sanitize_filename(url) + ".jpg"
        file_path = os.path.join(sandbox_dir, filename)

        print(f"[+] Downloading {filename} ...")
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            print(f"[+] File contained: {file_path}")
        else:
            print(f"[-] Failed to download file. Status code: {response.status_code}")
            return None

        result = check_steghide(file_path, passphrase)
        time.sleep(1)

        if result:
            print("[!] Warning: The image is most likely to contain steganography.")
            choice = input("[?] Do you want to continue the download? (y/n): ").strip().lower()
            if choice == 'y':
                destination_path = os.path.join(DOWNLOADS_DIR, filename)
                shutil.move(file_path, destination_path)
                print(f"[+] File moved to: {destination_path}")
            else:
                os.remove(file_path)
                print("[-] Download Aborted")
        else:
            print("[+] File passed stego checks")

        return file_path

    finally:
        print(f"[?] Deleting sandbox {sandbox_dir}")
        shutil.rmtree(sandbox_dir)
        print(f"[+] Sandbox removed.")
        if os.path.exists("output_file"):
            os.remove("output_file")

def download_and_process_zip(url, passphrase=PASS_PHRASE):
    sandbox_dir = tempfile.mkdtemp(prefix="sandbox_zip_")
    print(f"[+] Sandbox directory created at: {sandbox_dir}")

    try:
        zip_filename = sanitize_filename(url)
        if not zip_filename.endswith(".zip"):
            zip_filename += ".zip"

        zip_path = os.path.join(sandbox_dir, zip_filename)

        print(f"[+] Downloading ZIP from {url} ...")
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with open(zip_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            print(f"[✓] ZIP downloaded: {zip_path}")
        else:
            print(f"[-] Failed to download ZIP. Status code: {response.status_code}")
            return

        # Extract ZIP inside sandbox
        extract_dir = os.path.join(sandbox_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"[+] ZIP extracted to: {extract_dir}")

        for root, _, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"[+] Processing: {file}")
                result = check_steghide(file_path, passphrase)

                if result:
                    print(f"[!] Warning: {file} may contain steganography.")
                    choice = input(f"[?] Do you want to keep {file}? (y/n): ").strip().lower()
                    if choice != 'y':
                        os.remove(file_path)
                        print(f"[-] {file} deleted.")
                        continue

                destination_path = os.path.join(DOWNLOADS_DIR, file)
                shutil.move(file_path, destination_path)
                print(f"[+] File moved to: {destination_path}")
                if os.path.exists("output_file"):
                    os.remove("output_file")

    finally:
        print(f"[?] Cleaning up sandbox {sandbox_dir}")
        shutil.rmtree(sandbox_dir)
        print(f"[+] Sandbox removed.")

# === Part 2: Monitor Action (proxy.py logic) ===
recent_files = set()

def remove_from_recent(file):
    time.sleep(10)
    recent_files.discard(file)

class DownloadInterceptor(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in IMAGE_EXTENSIONS:
            return

        if filename in recent_files:
            return

        print(f"[!] Image download attempted.")
        time.sleep(3)

        sandbox_dir = tempfile.mkdtemp(prefix="sandbox_")
        sandbox_path = os.path.join(sandbox_dir, filename)

        try:
            shutil.move(event.src_path, sandbox_path)
            print(f"[+] File contained in sandbox.")

            result = check_steghide(sandbox_path, PASS_PHRASE)

            if result:
                print("[!] Warning: Possible steganography detected.")
                notify_user("Steganography Detected","Confirm Download")
                choice = input("[?] Continue download? (y/n): ").strip().lower()
                if choice != 'y':
                    os.remove(sandbox_path)
                    print("[-] Download aborted.")
                    return
            else:
                print("[+] File passed stego checks.")

            final_dest = os.path.join(DOWNLOADS_DIR, filename)
            shutil.move(sandbox_path, final_dest)
            print(f"[+] File moved to: {final_dest}")

            recent_files.add(filename)
            threading.Thread(target=remove_from_recent, args=(filename,), daemon=True).start()

        except Exception as e:
            print(f"[-] Error during processing: {e}")
        finally:
            shutil.rmtree(sandbox_dir)
            print(f"[+] Sandbox deleted.\n")
            if os.path.exists("output_file"):
                os.remove("output_file")

def monitor_action():
    print("[*] Watching for new image downloads...")
    handler = DownloadInterceptor()
    observer = Observer()
    observer.schedule(handler, DOWNLOADS_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# === Part 3: CLI Entry Point ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Option Downloader & Monitor CLI")
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    # dfile
    parser_dfile = subparsers.add_parser('dfile', help='Download a single image file')
    parser_dfile.add_argument('url', type=str, help='URL of the image')

    # dzip
    parser_dzip = subparsers.add_parser('dzip', help='Download a ZIP archive and scan it')
    parser_dzip.add_argument('url', type=str, help='URL of the ZIP file')

    # monitor
    subparsers.add_parser('monitor', help='Start watchdog-based monitoring on Downloads folder')

    args = parser.parse_args()

    if args.command == 'dfile':
        download_file_to_sandbox(args.url)
    elif args.command == 'dzip':
        download_and_process_zip(args.url)
    elif args.command == 'monitor':
        monitor_action()
    else:
        parser.print_help()




