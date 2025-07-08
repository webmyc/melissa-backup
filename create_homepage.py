#!/usr/bin/env python3
"""
Create homepage.html with full HTML content
"""

import json

def create_homepage():
    """Create homepage.html with full HTML content"""
    
    # Read the scraped results
    with open('scraper_results.json', 'r') as f:
        results = json.load(f)
    
    # Find the homepage
    for page in results:
        if page['url'] == 'https://melissa.respira.live/':
            # Use the full HTML content directly
            html_content = page['html_content']
            
            # Write the HTML file
            with open('homepage.html', 'w') as f:
                f.write(html_content)
            
            print(f"📝 Created homepage.html")
            break

if __name__ == "__main__":
    create_homepage()
