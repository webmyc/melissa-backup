#!/usr/bin/env python3
"""
Generate individual HTML files for each page
"""

import json
import os
from urllib.parse import urlparse

def url_to_filename(url):
    """Convert URL to filename"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    if not path:
        path = 'index'
    # Replace special characters with underscores
    filename = path.replace('/', '_').replace('-', '_')
    return f"{filename}.html"

def generate_html_pages():
    """Generate individual HTML files for each page"""
    
    # Read the scraped results
    with open('scraper_results.json', 'r') as f:
        results = json.load(f)
    
    for page in results:
        # Skip the root URL to avoid overwriting index.html
        if page['url'] == 'https://melissa.respira.live/':
            continue
            
        filename = url_to_filename(page['url'])
        # Use the full HTML content directly
        html_content = page['html_content']
        
        # Write the HTML file
        with open(filename, 'w') as f:
            f.write(html_content)
        
        print(f"📝 Created {filename}")

if __name__ == "__main__":
    generate_html_pages()
