import re
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict

def get_file_size(file_path):
    """Get file size in bytes"""
    return os.path.getsize(file_path)

def group_fonts_by_size(directory):
    """Group font files by their size to identify variants"""
    size_groups = defaultdict(list)
    for filename in os.listdir(directory):
        if filename.endswith('.woff2'):
            file_path = os.path.join(directory, filename)
            size = get_file_size(file_path)
            size_groups[size].append(filename)
    return size_groups

def normalize_font_name(original_name, font_type):
    """Create a normalized name for the font file"""
    # Extract weight and style from the original name if possible
    # Otherwise use the font_type parameter
    return f"font-{font_type}.woff2"

def download_file(url, local_path):
    """Download a file from URL to local path"""
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {url} -> {local_path}")
        return True
    else:
        print(f"Failed to download: {url}")
        return False

def extract_urls_from_css(content):
    """Extract URLs from CSS content, including those in url() functions"""
    # Pattern to match URLs in url() functions, handling both quoted and unquoted URLs
    # Only match URLs from framerusercontent.com
    url_pattern = r'url\([\'"]?(https://framerusercontent\.com/[^\'"()]+)[\'"]?\)'
    return re.findall(url_pattern, content)

def update_html_references(html_path):
    """Update HTML file to reference local files"""
    with open(html_path, 'r') as f:
        content = f.read()
    
    # Find all URLs, including those in @font-face declarations
    urls = extract_urls_from_css(content)
    
    # Group downloaded fonts by size
    assets_dir = os.path.join('assets')
    font_groups = group_fonts_by_size(assets_dir)
    
    # Create a mapping of original filenames to normalized names
    font_mapping = {}
    for size, files in font_groups.items():
        if len(files) > 1:  # Only group if there are multiple files of the same size
            for i, filename in enumerate(files):
                font_type = f"variant-{i+1}"
                font_mapping[filename] = normalize_font_name(filename, font_type)
    
    for url in urls:
        parsed_url = urlparse(url)
        path = parsed_url.path
        original_filename = os.path.basename(path)
        
        # Determine local path based on URL pattern
        if '/images/' in path:
            local_path = os.path.join('site/images', os.path.basename(path))
        elif '/assets/' in path:
            # Use normalized name if available, otherwise use original
            normalized_name = font_mapping.get(original_filename, original_filename)
            local_path = os.path.join('site/assets', normalized_name)
        else:
            normalized_name = font_mapping.get(original_filename, original_filename)
            local_path = os.path.join('site/assets', normalized_name)
        
        # Download the file
        if download_file(url, local_path):
            # Update the reference in HTML, handling both quoted and unquoted URLs
            content = content.replace(f'url({url})', f'url({local_path})')
            content = content.replace(f'url("{url}")', f'url("{local_path}")')
            content = content.replace(f"url('{url}')", f"url('{local_path}')")
    
    # Write updated HTML
    with open(html_path, 'w') as f:
        f.write(content)
    print("HTML file updated with local references")

if __name__ == "__main__":
    update_html_references('index.html') 