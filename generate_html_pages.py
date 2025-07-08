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
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page['title']}</title>
</head>
<body>
    <h1>{page['title']}</h1>
    <p><i>URL: {page['url']}</i></p>
    <div>
        {page['content']}
    </div>
</body>
</html>'''
        
        # Write the HTML file
        with open(filename, 'w') as f:
            f.write(html_content)
        
        print(f"📝 Created {filename}")

if __name__ == "__main__":
    generate_html_pages()
