import re
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

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

def update_html_references(html_path):
    """Update HTML file to reference local files"""
    with open(html_path, 'r') as f:
        content = f.read()
    
    # Find all framerusercontent.com URLs
    urls = re.findall(r'https://framerusercontent\.com/[^"\']+', content)
    
    for url in urls:
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Determine local path based on URL pattern
        if '/images/' in path:
            local_path = os.path.join('images', os.path.basename(path))
        elif '/assets/' in path:
            local_path = os.path.join('assets', os.path.basename(path))
        else:
            local_path = os.path.join('assets', os.path.basename(path))
        
        # Download the file
        if download_file(url, local_path):
            # Update the reference in HTML
            content = content.replace(url, local_path)
    
    # Write updated HTML
    with open(html_path, 'w') as f:
        f.write(content)
    print("HTML file updated with local references")

if __name__ == "__main__":
    update_html_references('index.html') 