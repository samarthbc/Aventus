import os
import tempfile
import requests
import shutil
import argparse
from urllib.parse import urlparse, unquote
from model import check_steghide
import zipfile
import time

def sanitize_filename(url):
    path = urlparse(url).path
    filename = os.path.basename(path)
    filename = unquote(filename).split('?')[0]
    if not filename:
        filename = "downloaded_file"
    return filename

def download_file_to_sandbox(url, passphrase="secret123"):
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

def download_and_process_zip(url, passphrase="secret123"):
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

        # Process each extracted file
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

                # Move file to Downloads
                downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                os.makedirs(downloads_dir, exist_ok=True)
                destination_path = os.path.join(downloads_dir, file)
                shutil.move(file_path, destination_path)
                print(f"[+] File moved to: {destination_path}")

                if os.path.exists("output_file"):
                    os.remove("output_file")

    finally:
        print(f"[?] Cleaning up sandbox {sandbox_dir}")
        shutil.rmtree(sandbox_dir)
        print(f"[+] Sandbox {sandbox_dir} removed.")

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Multi-Option Downloader & Monitor CLI")

        subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

        # dfile option
        parser_dfile = subparsers.add_parser('dfile', help='Download a single file (specify url)')
        parser_dfile.add_argument('url', type=str, help='URL of the file to download')

        # dzip option
        parser_dzip = subparsers.add_parser('dzip', help='Download a zip archive (specify url)')
        parser_dzip.add_argument('url', type=str, help='URL of the ZIP to download')

        # monitor option
        parser_monitor = subparsers.add_parser('monitor', help='Set up a download pipeline')

        args = parser.parse_args()

        if args.command == 'dfile':
            download_file_to_sandbox(args.url)
        elif args.command == 'dzip':
            download_and_process_zip(args.url)
        # elif args.command == 'monitor':
        #     monitor_action()
        else:
            parser.print_help()

