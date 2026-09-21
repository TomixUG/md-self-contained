import re
import os
import sys
import base64
import mimetypes
import urllib.parse

def find_vault_root(start_dir):
    """Find the root of the Obsidian vault by looking for the .obsidian folder."""
    current = start_dir
    while current and current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, '.obsidian')):
            return current
        current = os.path.dirname(current)
    # If no .obsidian folder is found, fallback to the start_dir
    return start_dir

def build_file_index(root_dir):
    """Build a dictionary of filename -> full path for quick lookups."""
    index = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for f in filenames:
            # If multiple files have the same name, we keep the first one found.
            # Obsidian usually complains about duplicates anyway.
            if f not in index:
                index[f] = os.path.join(dirpath, f)
    return index

def embed_images_in_markdown(md_content, base_dir='.'):
    vault_root = find_vault_root(base_dir)
    file_index = build_file_index(vault_root)

    # Match standard markdown images: ![alt](path)
    md_image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    # Match Obsidian wiki links for images: ![[path]] or ![[path|alt]]
    obsidian_image_pattern = re.compile(r'!\[\[(.*?)\]\]')

    def generate_base64_markdown(filepath, alt_text):
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = 'image/png' # fallback
            
        with open(filepath, 'rb') as f:
            encoded_string = base64.b64encode(f.read()).decode('utf-8')
            
        return f"![{alt_text}](data:{mime_type};base64,{encoded_string})"

    def resolve_file(image_path):
        """Try to find the file locally or in the vault index."""
        # 1. Check exact relative/absolute path
        full_path = os.path.join(base_dir, image_path)
        if os.path.exists(full_path):
            return full_path
            
        # 2. Check just the filename in the vault index
        filename = os.path.basename(image_path)
        if filename in file_index:
            return file_index[filename]
            
        return None

    def replace_standard(match):
        alt_text = match.group(1)
        image_path = match.group(2).strip()
        
        # Don't try to embed if it's already a URL or base64
        if image_path.startswith('http://') or image_path.startswith('https://') or image_path.startswith('data:'):
            return match.group(0)

        # Handle URL encoded spaces if any
        image_path = urllib.parse.unquote(image_path)
        full_path = resolve_file(image_path)
        
        if not full_path:
            print(f"Warning: image not found: '{image_path}' for {match.group(0)}", file=sys.stderr)
            return match.group(0)
            
        return generate_base64_markdown(full_path, alt_text)

    def replace_obsidian(match):
        content = match.group(1)
        parts = content.split('|')
        image_path = parts[0].strip()
        alt_text = parts[1] if len(parts) > 1 else image_path
        
        full_path = resolve_file(image_path)
        
        if not full_path:
            print(f"Warning: image not found: '{image_path}' for {match.group(0)}", file=sys.stderr)
            return match.group(0)
            
        return generate_base64_markdown(full_path, alt_text)

    # Apply replacements
    content = obsidian_image_pattern.sub(replace_obsidian, md_content)
    content = md_image_pattern.sub(replace_standard, content)
    
    return content

import argparse

def main():
    parser = argparse.ArgumentParser(description="Embed images into markdown as base64.")
    parser.add_argument("markdown_file", help="The markdown file to process.")
    parser.add_argument("-o", "--output-folder", help="Specify an output folder for the embedded markdown file.")
    args = parser.parse_args()
    
    input_file = args.markdown_file
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
        
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    base_dir = os.path.dirname(os.path.abspath(input_file))
    result = embed_images_in_markdown(content, base_dir)
    
    basename = os.path.basename(input_file)
    if basename.lower().endswith('.md'):
        out_name = basename[:-3] + '.embedded.md'
    else:
        out_name = basename + '.embedded.md'
        
    if args.output_folder:
        if not os.path.exists(args.output_folder):
            os.makedirs(args.output_folder)
        output_file = os.path.join(args.output_folder, out_name)
    else:
        # Default to the same directory as the input file, or current if it's just a filename
        input_dir = os.path.dirname(input_file)
        if not input_dir:
            input_dir = '.'
        output_file = os.path.join(input_dir, out_name)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
        
    print(f"Successfully created: {output_file}")

if __name__ == '__main__':
    main()
