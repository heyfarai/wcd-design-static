import re
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def download_file(url, local_path):
    """Download a file from URL to local path"""
    # Skip .woff2 files
    if local_path.endswith('.woff2'):
        print(f"Skipping .woff2 file: {url}")
        return True
        
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
    
    print("Processing HTML file...")
    
    # Try a simpler regex pattern
    urls = re.findall(r'framerusercontent\.com/[^"\'\s>]+', content)
    print(f"\nFound {len(urls)} URLs:")
    for url in urls:
        print(f"https://{url}")
    
    # Process the URLs
    for url in urls:
        full_url = f"https://{url}"
        parsed_url = urlparse(full_url)
        path = parsed_url.path
        
        # Determine local path based on URL pattern
        if '/images/' in path:
            local_path = os.path.join('site', 'images', os.path.basename(path))
        elif '/assets/' in path:
            local_path = os.path.join('site', 'assets', os.path.basename(path))
        else:
            local_path = os.path.join('site', 'assets', os.path.basename(path))
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download the file (or skip if it's a .woff2)
        if download_file(full_url, local_path):
            # Update the reference in HTML
            content = content.replace(full_url, local_path)
    
    # Write updated HTML
    with open(html_path, 'w') as f:
        f.write(content)
    print("HTML file updated with local references")

if __name__ == "__main__":
    update_html_references('site/index.html') 