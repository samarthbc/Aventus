import subprocess

image_file = "kittenz123.jpg"  # Image with hidden data
output_file = "extracted_file"    # Output file after extraction
password = "secret123"            # Password used in embedding

cmd = ["steghide", "extract", "-sf", image_file, "-p", password, "-xf", output_file]
result = subprocess.run(cmd, capture_output=True, text=True)

print(result.stdout if result.returncode == 0 else result.stderr)
