import os
import urllib.request

# Define the base output directory
# Path corresponds to: algorithm/assets/datasets
BASE_DIR = os.path.join("assets", "datasets")

def get_target_directory(fmt):
    """
    Returns the correct directory path based on the file format
    and the project structure provided.
    """
    fmt = fmt.lower()
    if fmt in ['jpg', 'jpeg']:
        # JPGs go into the 'normal' subdirectory as per structure
        return os.path.join(BASE_DIR, "jpg", "normal")
    elif fmt == 'png':
        return os.path.join(BASE_DIR, "png", "normal")
    elif fmt == 'svg':
        return os.path.join(BASE_DIR, "svg", "normal")
    else:
        # Fallback for other formats
        return os.path.join(BASE_DIR, fmt)

def download_sample_images(formats=None):
    """
    Downloads sample images from the web for the specified formats given as arguments.

    Args:
        formats (list): List of file extensions to download (e.g., ['jpg', 'svg']).
    """
    if formats is None:
        formats = ['png']

    # Dictionary of reliable public domain/CC URLs for testing
    sources = {
        "jpg": [
            ("cat.jpg", "https://upload.wikimedia.org/wikipedia/commons/a/a3/June_odd-eyed-cat.jpg"),
            ("flower.jpg", "https://upload.wikimedia.org/wikipedia/commons/e/e0/JPEG_example_JPG_RIP_100.jpg")
        ],
        "jpeg": [ # Alias for jpg
            ("cat.jpg", "https://upload.wikimedia.org/wikipedia/commons/a/a3/June_odd-eyed-cat.jpg")
        ],
        "png": [
            ("dice.png", "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"),
            ("test_cmyk.png", "https://upload.wikimedia.org/wikipedia/commons/6/6a/PNG_Test.png")
        ],
        "svg": [
            ("tiger.svg", "https://upload.wikimedia.org/wikipedia/commons/f/fd/Ghostscript_Tiger.svg"),
            ("python_logo.svg", "https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg")
        ]
    }

    print(f"Starting download process to: {os.path.abspath(BASE_DIR)}")

    for fmt in formats:
        key = fmt.lower()

        # Check if we have sources for this format
        if key not in sources:
            print(f"[!] No download sources defined for format: {fmt}")
            continue

        # Determine path (e.g., assets/datasets/jpg/normal)
        target_dir = get_target_directory(key)
        os.makedirs(target_dir, exist_ok=True)

        print(f"\nProcessing {fmt.upper()} -> {target_dir}")

        for filename, url in sources[key]:
            output_path = os.path.join(target_dir, filename)
            try:
                print(f"  Downloading: {filename}...")

                # Download using urllib (standard library, no pip install needed)
                # Adding a User-Agent to avoid being blocked by some servers
                req = urllib.request.Request(
                    url,
                    data=None,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )

                with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
                    out_file.write(response.read())

                print(f"  Success: {output_path}")
            except Exception as e:
                print(f"  Failed to download {url}. Error: {e}")

if __name__ == "__main__":
    # Example usage: passing the formats as arguments via list
    download_sample_images(formats=['jpg', 'png', 'svg'])
