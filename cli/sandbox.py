import os
import tempfile
import requests
import shutil
from urllib.parse import urlparse, unquote
from model import check_steghide


def sanitize_filename(url):
    path = urlparse(url).path
    filename = os.path.basename(path)
    filename = unquote(filename).split('?')[0]
    if not filename:
        filename = "downloaded_file"
    return filename

def download_file_to_sandbox(url):
    sandbox_dir = tempfile.mkdtemp(prefix="sandbox_")
    print(f"[+] Sandbox created at: {sandbox_dir}")

    try:
        content_disp = response.headers.get('content-disposition')
        if content_disp:
            import re
            fname_match = re.findall('filename="(.+)"', content_disp)
            if fname_match:
                filename = fname_match[0]
            else:
                filename = sanitize_filename(url)
        else:
            filename = sanitize_filename(url)

        filename = sanitize_filename(url)
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
        
        result = check_steghide(file_path, "secret123")
        
        if result:
            print("[!] Warning: The image is most likely to contain steganography.")
            choice = input("[?] Do you want to keep it and move to Downloads? (y/n): ").strip().lower()

            if choice == 'y':
                downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                if not os.path.exists(downloads_dir):
                    os.makedirs(downloads_dir)
                destination_path = os.path.join(downloads_dir, filename)
                shutil.move(file_path, destination_path)
                print(f"[+] File moved to: {destination_path}")
            else:
                os.remove(file_path)
                print(f"[-] Suspicious file deleted: {file_path}")
        else:
            print("[+] No steganography detected.")

        return file_path

    finally:
        print(f"[?] Deleting sandbox {sandbox_dir}")
        shutil.rmtree(sandbox_dir)
        print(f"[+] Sandbox {sandbox_dir} removed.")
        os.remove("output_file")

if __name__ == "__main__":
    url = input("Enter the URL of the file to download: ").strip()
    download_file_to_sandbox(url)
