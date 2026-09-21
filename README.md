# Markdown Image Embedder

A simple Python script to convert Markdown image references into embedded Base64 data URIs. This is especially useful for making self-contained markdown documents that you can share without worrying about missing local images.

## Features

- Supports **standard Markdown** images: `![alt](path/to/image.png)`
- Supports **Obsidian Wiki Links**: `![[image.png]]` or `![[image.png|Alt text]]`
- Automatically searches for your `.obsidian` vault root to resolve attachments from anywhere in the vault (like `images/` or `attachments/` folders).
- Preserves spaces in filenames and handles URL encoding safely.
- Generates a new file with the `.embedded.md` extension, leaving your original file intact.

## Usage

Run the script from your terminal and pass your markdown file as an argument:

```bash
python embed_images.py /path/to/your/file.md
```

The script will generate a new file in the same directory called `file.embedded.md`.

## Testing

A suite of unit tests is included to verify that image references and the Obsidian vault directory crawler work correctly. 

Run the tests using standard `unittest`:

```bash
python -m unittest test_embed_images.py
```
