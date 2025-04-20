# Photo Tagger with Ollama LLaVA

Automatically generate image descriptions and embed them as metadata using a local Ollama LLaVA model.

## Features
- Scans a folder for images (JPEG, PNG)
- Sends each image to a local Ollama LLaVA (llava:7b) model for captioning
- Embeds the generated caption as EXIF metadata (JPEG) or tEXt chunk (PNG)
- Command-line interface

## Requirements
- Python 3.8+
- [Ollama](https://ollama.com/) running locally with the `llava:7b` model pulled and available
- The following Python packages (see `requirements.txt`):
  - requests
  - Pillow
  - piexif

## Installation
1. **Clone or download this repository**

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure Ollama and the LLaVA model are running:**
   - Install Ollama: https://ollama.com/download
   - Start Ollama, then pull the model:
     ```bash
     ollama pull llava:7b
     ollama run llava:7b
     ```
   - The API should be available at `http://localhost:11434`

## Usage

Run the script to process a folder of images:

```bash
python describe_images.py /path/to/your/image/folder
```
Or, if using a virtual environment:
```bash
venv/bin/python describe_images.py /path/to/your/image/folder
```

- All `.jpg`, `.jpeg`, and `.png` files in the folder (and subfolders) will be processed.
- Captions will be embedded as EXIF (for JPEGs) or as a tEXt chunk (for PNGs).
- The script prints/logs the file and generated caption for each image.

## Notes
- For best results, ensure the Ollama LLaVA model is running before starting the script.
- Captions are stored in the EXIF `ImageDescription` tag for JPEGs. Some image viewers/editors may show this as "Description" or "Caption".
- For PNGs, the caption is stored as a tEXt chunk with the key `Description` (not all viewers support this).

## Troubleshooting
- **400 Bad Request**: Make sure the Ollama API is running and the model name matches (`llava:7b`).
- **ModuleNotFoundError**: Ensure dependencies are installed in your (virtual) environment.
- **Permission errors**: Make sure you have write access to the images/folder.

## License
MIT License
