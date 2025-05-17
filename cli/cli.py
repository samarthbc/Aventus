import os
import tempfile
import requests
import shutil
import argparse
from urllib.parse import urlparse, unquote
from model import check_steghide

def sanitize_filename(url):
    path = urlparse(url).path
    filename = os.path.basename(path)
    filename = unquote(filename).split('?')[0]
    if not filename:
        filename = "downloaded_file"
    return filename

def download_file_to_sandbox(url, passphrase):
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

        if result:
            print("[!] Warning: The image is most likely to contain steganography.")
            choice = input("[?] Do you want to continue the download? (y/n): ").strip().lower()

            if choice == 'y':
                downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                if not os.path.exists(downloads_dir):
                    os.makedirs(downloads_dir)
                destination_path = os.path.join(downloads_dir, filename)
                shutil.move(file_path, destination_path)
                print(f"[+] File moved to: {destination_path}")
            else:
                os.remove(file_path)
                print(f"[-] Download Aborted")
        else:
            print("[+] File passed stego checks")

        return file_path

    finally:
        print(f"[?] Deleting sandbox {sandbox_dir}")
        shutil.rmtree(sandbox_dir)
        print(f"[+] Sandbox {sandbox_dir} removed.")
        if os.path.exists("output_file"):
            os.remove("output_file")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images while keeping safety in mind")
    parser.add_argument("--url", required=True, help="URL of the file to download and scan")
    # parser.add_argument("--passphrase", default="secret123", help="Passphrase to check hidden data (default: secret123)")

    args = parser.parse_args()
    download_file_to_sandbox(args.url, "secret123")
