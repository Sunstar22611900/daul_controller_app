
import os

filepath = r"d:\07python\gemini-daul-controller\GEMINI.md"

try:
    with open(filepath, 'rb') as f:
        content_bytes = f.read()

    # Try decoding as UTF-8
    try:
        content_str = content_bytes.decode('utf-8')
        print("File is valid UTF-8.")
        print("Last 500 chars:")
        print(content_str[-500:])
    except UnicodeDecodeError as e:
        print(f"File is NOT valid UTF-8. Error: {e}")
        # Decode ignoring errors to see content
        content_str = content_bytes.decode('utf-8', errors='replace')
        print("Last 500 chars (with replacement):")
        print(content_str[-500:])

except Exception as e:
    print(f"Error: {e}")
