#!/usr/bin/env python3
"""
Generate index.html with scraped pages data
"""

import json
import datetime
from urllib.parse import urlparse
import os

def url_to_filename(url):
    """Convert URL to filename"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    if not path:
        path = 'index'
    # Replace special characters with underscores
    filename = path.replace('/', '_').replace('-', '_')
    return f"{filename}.html"

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
        page_card = f'''                <div class="page-card">
                    <div class="page-info">
                        <div class="page-title">{page['title']}</div>
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
        print(f"   {i:2d}. {page['title']} ({page['url']})")

if __name__ == "__main__":
    generate_index()
