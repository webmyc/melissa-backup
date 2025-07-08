#!/usr/bin/env python3
"""
Enhanced Kajabi Scraper with Anti-Blocking Measures
- Rate limiting and random delays
- User agent rotation
- Session management
- Batch processing
- Progress tracking and resume capability
- Error handling and retry logic
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedKajabiScraper:
    def __init__(self, base_delay=2, max_delay=5, batch_size=10):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.batch_size = batch_size
        self.session = requests.Session()
        self.progress_file = 'scraper_progress.json'
        self.results_file = 'scraper_results.json'
        
        # User agent rotation
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
        
        # Load existing progress
        self.progress = self.load_progress()
        self.results = self.load_results()
    
    def load_progress(self) -> Dict:
        """Load processing progress from file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'completed_urls': [], 'failed_urls': [], 'current_batch': 0}
    
    def save_progress(self):
        """Save current progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def load_results(self) -> List:
        """Load existing results from file"""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_results(self):
        """Save current results to file"""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return random.choice(self.user_agents)
    
    def wait_with_jitter(self):
        """Wait with random jitter to appear more human-like"""
        delay = random.uniform(self.base_delay, self.max_delay)
        logger.info(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def scrape_url(self, url: str, retries: int = 3) -> Optional[Dict]:
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
                    # Exponential backoff
                    wait_time = (2 ** attempt) * self.base_delay
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All attempts failed for {url}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error scraping {url}: {e}")
                return None
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else ''
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content text"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main',
            '[role="main"]',
            '.main-content',
            '.content',
            'article',
            '.post-content',
            '.page-content'
        ]
        
        content_text = ""
        for selector in content_selectors:
            content_area = soup.select_one(selector)
            if content_area:
                content_text = content_area.get_text(separator='\n', strip=True)
                break
        
        # Fallback to body if no main content found
        if not content_text:
            content_text = soup.get_text(separator='\n', strip=True)
        
        return content_text
    
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract image URLs"""
        images = []
        for img in soup.find_all('img', src=True):
            img_url = urljoin(base_url, img['src'])
            images.append(img_url)
        return images
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract internal links"""
        links = []
        for link in soup.find_all('a', href=True):
            link_url = urljoin(base_url, link['href'])
            # Only include links from the same domain
            if urlparse(link_url).netloc == urlparse(base_url).netloc:
                links.append(link_url)
        return list(set(links))  # Remove duplicates
    
    def extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ''
    
    def load_urls_from_file(self, file_path: str) -> List[str]:
        """Load URLs from file"""
        urls = []
        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    
                    # Check if line contains a URL (either plain URL or numbered format)
                    if line.startswith('http'):
                        # Plain URL format
                        urls.append(line)
                        logger.debug(f"Line {line_num}: Added URL {line}")
                    elif '|' in line:
                        # Numbered format: "number|url"
                        parts = line.split('|', 1)
                        if len(parts) == 2:
                            url = parts[1].strip()
                            if url and url.startswith('http'):
                                urls.append(url)
                                logger.debug(f"Line {line_num}: Added URL {url}")
                            else:
                                logger.warning(f"Line {line_num}: Invalid URL in numbered format: {line}")
                    else:
                        logger.warning(f"Line {line_num}: Unrecognized format: {line}")
            
            logger.info(f"Loaded {len(urls)} URLs from {file_path}")
            return urls
        except Exception as e:
            logger.error(f"Error loading URLs from {file_path}: {e}")
            return []
    
    def process_batch(self, urls: List[str], batch_num: int) -> List[Dict]:
        """Process a batch of URLs"""
        logger.info(f"Processing batch {batch_num + 1} with {len(urls)} URLs")
        batch_results = []
        
        for i, url in enumerate(urls):
            if url in self.progress['completed_urls']:
                logger.info(f"Skipping already processed URL: {url}")
                continue
            
            result = self.scrape_url(url)
            if result:
                batch_results.append(result)
                self.results.append(result)
                self.progress['completed_urls'].append(url)
                logger.info(f"Progress: {len(self.progress['completed_urls'])}/{len(urls)} URLs completed")
            else:
                self.progress['failed_urls'].append(url)
                logger.error(f"Failed to scrape: {url}")
            
            # Save progress after each URL
            self.save_progress()
            self.save_results()
            
            # Wait between requests (except for the last URL in batch)
            if i < len(urls) - 1:
                self.wait_with_jitter()
        
        return batch_results
    
    def scrape_all_urls(self, file_path: str):
        """Main method to scrape all URLs from file"""
        urls = self.load_urls_from_file(file_path)
        if not urls:
            logger.error("No URLs to process")
            return
        
        logger.info(f"Starting scraping process for {len(urls)} URLs")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"Base delay: {self.base_delay}-{self.max_delay} seconds")
        
        # Filter out already completed URLs
        remaining_urls = [url for url in urls if url not in self.progress['completed_urls']]
        logger.info(f"Remaining URLs to process: {len(remaining_urls)}")
        
        # Process in batches
        for i in range(0, len(remaining_urls), self.batch_size):
            batch = remaining_urls[i:i + self.batch_size]
            batch_num = i // self.batch_size
            
            try:
                self.process_batch(batch, batch_num)
                self.progress['current_batch'] = batch_num + 1
                
                # Longer pause between batches
                if i + self.batch_size < len(remaining_urls):
                    batch_pause = random.uniform(10, 20)
                    logger.info(f"Batch completed. Pausing {batch_pause:.2f} seconds before next batch...")
                    time.sleep(batch_pause)
                    
            except KeyboardInterrupt:
                logger.info("Scraping interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}")
                continue
        
        # Final summary
        logger.info("Scraping completed!")
        logger.info(f"Total URLs processed: {len(self.progress['completed_urls'])}")
        logger.info(f"Total URLs failed: {len(self.progress['failed_urls'])}")
        logger.info(f"Results saved to: {self.results_file}")
        
        if self.progress['failed_urls']:
            logger.warning(f"Failed URLs: {self.progress['failed_urls']}")


def main():
    """Main function"""
    print("Enhanced Kajabi Scraper Starting...")
    print("=" * 50)
    
    # Initialize scraper with conservative settings
    scraper = EnhancedKajabiScraper(
        base_delay=2,      # Minimum 2 seconds between requests
        max_delay=5,       # Maximum 5 seconds between requests
        batch_size=5       # Process 5 URLs at a time
    )
    
    # URL file path
    url_file = "/Users/akunay/Downloads/melissa-backup_URLs_to-scrape.txt"
    
    # Start scraping
    scraper.scrape_all_urls(url_file)
    
    print("\nScraping process completed!")
    print(f"Check 'scraper_results.json' for results")
    print(f"Check 'scraper_progress.json' for progress")
    print(f"Check 'scraper.log' for detailed logs")


if __name__ == "__main__":
    main()
