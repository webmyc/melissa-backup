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
        path = 'homepage'  # Root URL goes to homepage.html
    
    # Handle blog pages from mykajabi.com
    if 'mykajabi.com/blog/' in url:
        # Extract just the blog post slug from the URL
        slug = url.split('/blog/')[-1]
        filename = f"blog_{slug.replace('-', '_')}.html"
    else:
        # Replace special characters with underscores
        filename = path.replace('/', '_').replace('-', '_') + '.html'
    
    return filename

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
    with open('index_template.html', 'r') as f:
        template = f.read()
    
    # Generate page cards HTML
    page_cards = []
    for page in results:
        filename = url_to_filename(page['url'])
        # Extract title from HTML content
        title = extract_title_from_html(page['html_content'])
        
        # Add Blog: prefix for blog pages from mykajabi.com
        if 'mykajabi.com/blog/' in page['url']:
            title = f"Blog: {title}"
        
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
    
    # Update other template placeholders
    current_time = datetime.datetime.now().isoformat()
    template = template.replace('{{TOTAL_PAGES}}', str(len(results)))
    template = template.replace('{{LAST_UPDATED}}', current_time.split('T')[0])
    template = template.replace('{{TIMESTAMP}}', current_time)
    
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
        
        # Add Blog: prefix for blog pages from mykajabi.com
        if 'mykajabi.com/blog/' in page['url']:
            title = f"Blog: {title}"
        
        print(f"   {i:2d}. {title} ({page['url']})")

if __name__ == "__main__":
    generate_index()
