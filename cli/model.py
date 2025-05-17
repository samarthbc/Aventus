import subprocess
import sys
import os

steg_path = r"E:\steghide\steghide.exe"

def check_steghide(file_path, passphrase=''):
    if not os.path.isfile(file_path):
        print(f"[!] File '{file_path}' not found.")
        return
    
    print(f"[.] Processing the file...")

    # steghide info command
    try:
        # command = ['steghide', 'info', file_path]
        command = ["steghide", "extract", "-sf", file_path, "-p", passphrase, "-xf", "output_file"]
        
        # print(command)
        result = subprocess.run(command, capture_output=True, text=True)

        if(result.returncode == 0):
            # print(result.stdout if result.returncode == 0 else result.stderr)
            return True
        else:
            return False
    
    except Exception as e:
        print(f"[!] Exception occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_steg.py <image_file> [passphrase]")
    else:
        file_path = sys.argv[1]
        passphrase = sys.argv[2] if len(sys.argv) > 2 else ''
        check_steghide(file_path, passphrase)
