import os
import re
import requests
import mimetypes
import hashlib
from urllib.parse import urlparse, unquote
from pathlib import Path
import json

class FramerAssetManager:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.public_dir = os.path.join(root_dir, 'public')
        self.asset_mappings = {}  # Original URL to local path mapping
        self.processed_urls = set()  # Keep track of processed URLs
        
        # Create directory structure
        self.dirs = {
            'fonts': os.path.join(self.public_dir, 'assets', 'fonts'),
            'icons': os.path.join(self.public_dir, 'assets', 'icons'),
            'images': os.path.join(self.public_dir, 'assets', 'images'),
            'scripts': os.path.join(self.public_dir, 'assets', 'scripts'),
            'styles': os.path.join(self.public_dir, 'assets', 'styles'),
            'misc': os.path.join(self.public_dir, 'assets', 'misc')
        }
        
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)

    def get_file_type_dir(self, url, content_type=None):
        """Determine appropriate directory based on file type"""
        ext = Path(urlparse(url).path).suffix.lower()
        
        if ext in ['.woff', '.woff2', '.ttf', '.otf', '.eot']:
            return self.dirs['fonts']
        elif ext in ['.ico', '.png', '.jpg', '.jpeg', '.gif', '.svg'] or 'icon' in url.lower():
            return self.dirs['icons']
        elif ext in ['.js', '.mjs']:
            return self.dirs['scripts']
        elif ext in ['.css']:
            return self.dirs['styles']
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            return self.dirs['images']
        else:
            return self.dirs['misc']

    def generate_filename(self, url, content_type=None):
        """Generate a meaningful filename based on the URL and content type"""
        parsed_url = urlparse(url)
        original_name = os.path.basename(unquote(parsed_url.path))
        
        # Extract meaningful parts from the path
        path_parts = parsed_url.path.lower().split('/')
        meaningful_parts = [p for p in path_parts if p and not p.startswith('.') and len(p) > 1]
        
        # Generate base name
        if 'font' in url.lower() or any(ext in original_name.lower() for ext in ['.woff', '.woff2', '.ttf']):
            # Handle font files specially
            font_parts = [p for p in meaningful_parts if p not in ['assets', 'fonts']]
            base_name = '-'.join(font_parts)
        else:
            # For other files, use last meaningful part
            base_name = meaningful_parts[-1] if meaningful_parts else 'asset'

        # Keep the original extension if it exists, otherwise infer from content type
        ext = os.path.splitext(original_name)[1]
        if not ext and content_type:
            ext = mimetypes.guess_extension(content_type) or ''

        # Add a short hash to ensure uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
        
        return f"{base_name}-{url_hash}{ext}"

    def download_asset(self, url):
        """Download an asset and return its local path"""
        if url in self.processed_urls:
            return self.asset_mappings.get(url)

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type')
            target_dir = self.get_file_type_dir(url, content_type)
            filename = self.generate_filename(url, content_type)
            local_path = os.path.join(target_dir, filename)
            
            # Download the file
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Store the mapping
            relative_path = os.path.join('/assets', os.path.relpath(local_path, self.dirs['misc']).replace('\\', '/'))
            self.asset_mappings[url] = relative_path
            self.processed_urls.add(url)
            
            print(f"Downloaded: {url} -> {relative_path}")
            return relative_path
            
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return None

    def find_framer_urls(self, content):
        """Find all Framer URLs in content"""
        # Pattern for finding URLs in various contexts (quotes, parentheses, etc.)
        patterns = [
            r'https?://framerusercontent\.com/[^"\'\s)]+',
            r'https?://framer\.com/[^"\'\s)]+',
        ]
        
        urls = set()
        for pattern in patterns:
            urls.update(re.findall(pattern, content))
        return urls

    def process_file(self, file_path):
        """Process a single file for Framer URLs"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            urls = self.find_framer_urls(content)
            replacements = {}

            for url in urls:
                local_path = self.download_asset(url)
                if local_path:
                    replacements[url] = local_path

            if replacements:
                # Replace URLs in content
                new_content = content
                for url, local_path in replacements.items():
                    new_content = new_content.replace(url, local_path)

                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

    def process_directory(self):
        """Process all files in the directory"""
        for root, _, files in os.walk(self.root_dir):
            if 'node_modules' in root or '.git' in root:
                continue
                
            for file in files:
                if file.endswith(('.html', '.css', '.js', '.mjs', '.json')):
                    file_path = os.path.join(root, file)
                    print(f"Processing: {file_path}")
                    self.process_file(file_path)

        # Save asset mappings for reference
        mapping_file = os.path.join(self.public_dir, 'assets', 'framer-asset-mappings.json')
        with open(mapping_file, 'w') as f:
            json.dump(self.asset_mappings, f, indent=2)

def main():
    root_dir = os.getcwd()  # Or specify your project root
    manager = FramerAssetManager(root_dir)
    manager.process_directory()

if __name__ == "__main__":
    main()