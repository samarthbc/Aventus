import subprocess
import os

steghide_path = r"E:\steghide\steghide.exe"

# Configuration
cover_image = "cuteKitten.jpg"            # The innocent-looking image
file_to_hide = "malicious_payload.py" # The malicious file you want to embed
output_image = "kittenz123.jpg"    # The output image with embedded file
password = "secret123"                # Password for embedding

def embed_file():
    if not os.path.exists(cover_image):
        print(f"[!] Cover image '{cover_image}' not found.")
        return
    if not os.path.exists(file_to_hide):
        print(f"[!] File to hide '{file_to_hide}' not found.")
        return

    cmd = [
        steghide_path, "embed",
        "-cf", cover_image,    # cover file (innocent image)
        "-ef", file_to_hide,   # embedded file (malicious payload)
        "-p", password,        # password for extraction later
        "-sf", output_image    # output stego-image file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"[+] Successfully embedded '{file_to_hide}' into '{output_image}' with password '{password}'.")
    else:
        print(f"[-] Failed to embed file:\n{result.stderr}")

if __name__ == "__main__":
    embed_file()
