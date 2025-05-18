import os
import shutil
import time
import tempfile
import threading
from model import check_steghide
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set paths
downloads_dir = os.path.expanduser(r"C:\Users\Samarthsuhas\Downloads")
passphrase = "secret123"

# Set to track recently handled files
recent_files = set()

# Allowed image extensions
image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".ico"}

def remove_from_recent(file):
    time.sleep(10)  # Wait before allowing the same file to be reprocessed
    recent_files.discard(file)

class DownloadInterceptor(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            ext = os.path.splitext(filename)[1].lower()

            # Only process if it's an image
            if ext not in image_extensions:
                return

            # Prevent re-processing of same file
            if filename in recent_files:
                return

            src_path = event.src_path
            print(f"[+] New image detected: {src_path}")

            time.sleep(3)

            # Create sandbox
            sandbox_dir = tempfile.mkdtemp(prefix="sandbox_")
            print(f"[+] Sandbox created")
            sandbox_path = os.path.join(sandbox_dir, filename)

            try:
                shutil.move(src_path, sandbox_path)
                print(f"[+] File contained in the sandbox")
            except Exception as e:
                print(f"[-] Failed to move file to sandbox: {e}")
                shutil.rmtree(sandbox_dir)
                return

            try:
                result = check_steghide(sandbox_path, passphrase)

                if result:
                    print("[!] Warning: The image is most likely to contain steganography.")
                    choice = input("[?] Do you want to continue the download? (y/n): ").strip().lower()

                    if choice != 'y':
                        os.remove(sandbox_path)
                        print("[-] Download aborted and file deleted.")
                        return
                else:
                    print("[+] File passed stego checks.")

                # Move back to downloads
                final_dest = os.path.join(downloads_dir, filename)
                shutil.move(sandbox_path, final_dest)
                print(f"[+] File moved to: {final_dest}")

                # Add to recent_files to prevent reprocessing
                recent_files.add(filename)
                threading.Thread(target=remove_from_recent, args=(filename,), daemon=True).start()

            finally:
                shutil.rmtree(sandbox_dir)
                print(f"[+] Sandbox deleted.")
                print()
                if os.path.exists("output_file"):
                    os.remove("output_file")

if __name__ == "__main__":
    print("[*] Watching for new image downloads...")
    event_handler = DownloadInterceptor()
    observer = Observer()
    observer.schedule(event_handler, downloads_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
