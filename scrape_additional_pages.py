#!/usr/bin/env python3
"""
Scrape additional blog pages and add them to the existing results
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from urllib.parse import urlparse
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('additional_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdditionalScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Session configuration
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_random_user_agent(self):
        """Get a random user agent"""
        return random.choice(self.user_agents)
    
    def scrape_url(self, url, retries=3):
        """Scrape a single URL with retry logic"""
        for attempt in range(retries):
            try:
                # Update user agent for each request
                self.session.headers.update({
                    'User-Agent': self.get_random_user_agent()
                })
                
                logger.info(f"Scraping: {url} (attempt {attempt + 1}/{retries})")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Save the full HTML content
                result = {
                    'url': url,
                    'html_content': response.text,
                    'scraped_at': datetime.now().isoformat(),
                    'status_code': response.status_code
                }
                
                logger.info(f"Successfully scraped: {url}")
                return result
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    wait_time = (2 ** attempt) * 2
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All attempts failed for {url}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error scraping {url}: {e}")
                return None
    
    def url_to_filename(self, url):
        """Convert URL to filename"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if not path:
            path = 'index'
        
        # Extract the blog post slug from the path
        if '/blog/' in path:
            slug = path.split('/blog/')[-1]
            filename = f"blog_{slug.replace('-', '_')}.html"
        else:
            filename = path.replace('/', '_').replace('-', '_') + '.html'
        
        return filename
    
    def create_html_file(self, page_data):
        """Create HTML file from scraped data"""
        filename = self.url_to_filename(page_data['url'])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(page_data['html_content'])
        
        logger.info(f"Created HTML file: {filename}")
        return filename
    
    def scrape_additional_pages(self, urls):
        """Scrape the additional pages"""
        results = []
        
        # Load existing results if they exist
        if os.path.exists('scraper_results.json'):
            with open('scraper_results.json', 'r') as f:
                existing_results = json.load(f)
        else:
            existing_results = []
        
        logger.info(f"Starting to scrape {len(urls)} additional pages")
        
        for i, url in enumerate(urls):
            logger.info(f"Processing {i+1}/{len(urls)}: {url}")
            
            # Check if URL already exists
            if any(existing['url'] == url for existing in existing_results):
                logger.info(f"URL already exists in results, skipping: {url}")
                continue
            
            result = self.scrape_url(url)
            if result:
                results.append(result)
                
                # Create individual HTML file
                self.create_html_file(result)
                
                # Add to existing results
                existing_results.append(result)
                
                # Save updated results
                with open('scraper_results.json', 'w') as f:
                    json.dump(existing_results, f, indent=2)
                
                logger.info(f"Added to results: {url}")
            else:
                logger.error(f"Failed to scrape: {url}")
            
            # Wait between requests
            if i < len(urls) - 1:
                delay = random.uniform(2, 5)
                logger.info(f"Waiting {delay:.2f} seconds...")
                time.sleep(delay)
        
        logger.info(f"Scraping completed! Successfully scraped {len(results)} additional pages")
        return results

def main():
    """Main function"""
    additional_urls = [
        "https://melissalouise.mykajabi.com/blog/feminine-embodiment-is-such-a-catch-phrase-now-a-days",
        "https://melissalouise.mykajabi.com/blog/the-hypocrisy-many-men-refuse-to-address-with-pornography",
        "https://melissalouise.mykajabi.com/blog/when-it-comes-to-men-love-is-not-enough"
    ]
    
    scraper = AdditionalScraper()
    results = scraper.scrape_additional_pages(additional_urls)
    
    print(f"\n✅ Successfully scraped {len(results)} additional pages!")
    print("Files created:")
    for result in results:
        filename = scraper.url_to_filename(result['url'])
        print(f"  - {filename}")
    
    print("\n🔄 Next steps:")
    print("1. Run generate_index.py to update the main index")
    print("2. Commit and push changes")

if __name__ == "__main__":
    main()
