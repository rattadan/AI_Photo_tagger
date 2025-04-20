import os
import sys
import requests
from PIL import Image
import piexif
from io import BytesIO
import base64
import json

SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png']
OLLAMA_API_URL = 'http://localhost:11434/api/generate'
LLAVA_MODEL = 'llava:7b'


def get_image_caption(image_path):
    """
    Sends the image to the local Ollama LLaVA model and returns the generated caption.
    Uses base64 encoding and JSON payload as required by Ollama's vision API.
    """
    return get_ollama_response(image_path, 'Describe this image in one sentence.')

def get_image_tags(image_path):
    """
    Sends the image to the local Ollama LLaVA model and returns a comma-separated list of tags.
    """
    tags = get_ollama_response(image_path, 'List 5 relevant keywords for this image, comma-separated, no explanation, just the words.')
    if tags:
        # Clean up tags: split, strip, rejoin
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        return ', '.join(tag_list)
    return None

def get_ollama_response(image_path, prompt):
    """
    Helper function to send an image and prompt to Ollama and return the response as a string.
    Handles streaming JSON lines.
    """
    with open(image_path, 'rb') as img_file:
        image_bytes = img_file.read()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        payload = {
            'model': LLAVA_MODEL,
            'prompt': prompt,
            'images': [image_b64]
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(OLLAMA_API_URL, data=json.dumps(payload), headers=headers, timeout=60, stream=True)
            response.raise_for_status()
            result = ''
            for line in response.iter_lines():
                if line:
                    try:
                        obj = json.loads(line.decode('utf-8'))
                        part = obj.get('response') or obj.get('message')
                        if part:
                            result += part
                    except Exception as je:
                        print(f"[ERROR] Could not parse JSON from Ollama: {je}")
            return result.strip() if result else None
        except Exception as e:
            print(f"[ERROR] Failed to get Ollama response for {image_path}: {e}")
            return None


def add_caption_and_tags_to_jpeg(image_path, caption, tags):
    """
    Adds the caption to the EXIF ImageDescription tag and tags to XPKeywords for a JPEG image.
    """
    try:
        img = Image.open(image_path)
        exif_dict = piexif.load(img.info.get('exif', b''))
        exif_dict['0th'][piexif.ImageIFD.ImageDescription] = caption.encode('utf-8')
        if tags:
            # XPKeywords (ID 40094) expects UTF-16LE encoded bytes with null terminator
            exif_dict['0th'][40094] = tags.encode('utf-16le') + b'\x00\x00'
        exif_bytes = piexif.dump(exif_dict)
        img.save(image_path, exif=exif_bytes)
        print(f"[OK] Caption and tags added to {image_path}")
    except Exception as e:
        print(f"[ERROR] Could not write EXIF to {image_path}: {e}")


def add_caption_and_tags_to_png(image_path, caption, tags):
    """
    Adds the caption and tags to a PNG image as tEXt chunks (not EXIF, but readable by some tools).
    """
    try:
        from PIL import PngImagePlugin
        img = Image.open(image_path)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text('Description', caption)
        if tags:
            pnginfo.add_text('Keywords', tags)
        img.save(image_path, pnginfo=pnginfo)
        print(f"[OK] Caption and tags added to {image_path}")
    except Exception as e:
        print(f"[ERROR] Could not write caption/tags to PNG {image_path}: {e}")


def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                fpath = os.path.join(root, fname)
                print(f"[INFO] Processing {fpath}")
                caption = get_image_caption(fpath)
                tags = get_image_tags(fpath)
                if caption:
                    if ext in ['.jpg', '.jpeg']:
                        add_caption_and_tags_to_jpeg(fpath, caption, tags)
                    elif ext == '.png':
                        add_caption_and_tags_to_png(fpath, caption, tags)
                    print(f"[CAPTION] {fname}: {caption}")
                    if tags:
                        print(f"[TAGS] {fname}: {tags}")
                else:
                    print(f"[WARN] No caption for {fpath}")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <folder_path>")
        sys.exit(1)
    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print(f"[ERROR] {folder_path} is not a valid directory.")
        sys.exit(1)
    process_folder(folder_path)

if __name__ == "__main__":
    main()
