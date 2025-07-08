#!/usr/bin/env python3
"""
Generate index.html with scraped pages data
"""

import json
import datetime
from urllib.parse import urlparse
import os
import re

def url_to_filename(url):
    """Convert URL to filename"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    if not path:
        path = 'index'
    # Replace special characters with underscores
    filename = path.replace('/', '_').replace('-', '_')
    return f"{filename}.html"

def extract_title_from_html(html_content):
    """Extract title from HTML content"""
    # Use regex to find the title tag
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        # Remove extra whitespace and newlines
        title = re.sub(r'\s+', ' ', title)
        return title
    return "Untitled Page"

def generate_index():
    """Generate index.html with scraped pages data"""
    
    # Read the scraped results
    with open('scraper_results.json', 'r') as f:
        results = json.load(f)
    
    # Read the template
    with open('index.html', 'r') as f:
        template = f.read()
    
    # Generate page cards HTML
    page_cards = []
    for page in results:
        filename = url_to_filename(page['url'])
        # Extract title from HTML content
        title = extract_title_from_html(page['html_content'])
        page_card = f'''                <div class="page-card">
                    <div class="page-info">
                        <div class="page-title">{title}</div>
                        <div class="page-url">{page['url']}</div>
                    </div>
                    <a href="{filename}" class="page-link" target="_blank">View Page</a>
                </div>'''
        page_cards.append(page_card)
    
    # Replace template placeholders
    pages_html = '\n'.join(page_cards)
    
    # Replace the template section
    template = template.replace(
        '                <!-- BEGIN: Scraped Pages -->\n                {{#each pages}}\n                <div class="page-card">\n                    <div class="page-info">\n                        <div class="page-title">{{title}}</div>\n                        <div class="page-url">{{url}}</div>\n                    </div>\n                    <a href="{{url}}.html" class="page-link" target="_blank">View Page</a>\n                </div>\n                {{/each}}\n                <!-- END: Scraped Pages -->',
        pages_html
    )
    
    # Update the timestamp
    current_time = datetime.datetime.now().isoformat()
    template = template.replace('2025-07-08T21:37:58.946Z', current_time)
    
    # Write the final index.html
    with open('index.html', 'w') as f:
        f.write(template)
    
    print(f"✅ Generated index.html with {len(results)} pages")
    print(f"📊 Statistics:")
    print(f"   - Total pages scraped: {len(results)}")
    print(f"   - Last updated: {current_time}")
    
    # List the pages
    print(f"\n📄 Pages included:")
    for i, page in enumerate(results, 1):
        title = extract_title_from_html(page['html_content'])
        print(f"   {i:2d}. {title} ({page['url']})")

if __name__ == "__main__":
    generate_index()
