import re
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import time
import sys
import os

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

TIMEOUT = 10
MAX_PAGES = 1000


class PHPCrawler:
    
    def __init__(self, base_url, max_pages=MAX_PAGES):
        self.base_url = base_url.rstrip('/')
        self.base_domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        
        self.visited_urls = set()
        self.found_urls = set()        
        self.queue = []
        self.pages_crawled = 0
        
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        domain_clean = self.base_domain.replace('.', '_').replace(':', '_')
        self.output_file = f"found_params_{domain_clean}_{timestamp}.txt"
        
        with open(self.output_file, 'w') as f:
            f.write(f"# Target: {self.base_url}\n")
            f.write(f"# Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("#" + "=" * 60 + "\n\n")
        
        print(f"Auto-save: {self.output_file}\n")
    
    def extract_links(self, url, html_content):
        links = set()
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for tag in soup.find_all(href=True):
                href = tag['href'].strip()
                if href and not href.startswith('#') and not href.startswith('javascript:') and not href.startswith('mailto:') and not href.startswith('tel:'):
                    full_url = urljoin(url, href)
                    links.add(full_url)
            
            for tag in soup.find_all('link', href=True):
                href = tag['href'].strip()
                if '?' in href:
                    full_url = urljoin(url, href)
                    links.add(full_url)
            
            for tag in soup.find_all('script', src=True):
                src = tag['src'].strip()
                if '?' in src:
                    full_url = urljoin(url, src)
                    links.add(full_url)
            
            for tag in soup.find_all('form', action=True):
                action = tag['action'].strip()
                if action:
                    full_url = urljoin(url, action)
                    links.add(full_url)
            
            for tag in soup.find_all('iframe', src=True):
                src = tag['src'].strip()
                if '?' in src:
                    full_url = urljoin(url, src)
                    links.add(full_url)
            
            for tag in soup.find_all('img', src=True):
                src = tag['src'].strip()
                if '?' in src:
                    full_url = urljoin(url, src)
                    links.add(full_url)
            
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    js_pattern = re.compile(
                        r'(?:https?://|/)[^\s"\'<>\[\]]+\?(?:[^\s"\'<>\[\]]*=\d+[^\s"\'<>\[\]]*)+'
                    )
                    js_links = js_pattern.findall(script.string)
                    for link in js_links:
                        full_url = urljoin(url, link)
                        links.add(full_url)
            
            for tag in soup.find_all(True):
                for attr in ['onclick', 'onmouseover', 'onmouseout', 'onchange', 'onsubmit', 'onload']:
                    if tag.get(attr):
                        attr_pattern = re.compile(
                            r'(?:https?://|/)[^\s"\'<>\[\]]+\?(?:[^\s"\'<>\[\]]*=\d+[^\s"\'<>\[\]]*)+'
                        )
                        matches = attr_pattern.findall(tag[attr])
                        for match in matches:
                            full_url = urljoin(url, match)
                            links.add(full_url)
            
            for tag in soup.find_all(True):
                for attr in tag.attrs:
                    if attr.startswith('data-') and tag[attr]:
                        val = str(tag[attr])
                        if '?' in val and '=' in val:
                            full_url = urljoin(url, val)
                            links.add(full_url)
            
        except Exception as e:
            pass
        
        return links
    
    def is_valid_url(self, url):
        try:
            parsed = urlparse(url)
            
            if parsed.scheme not in ['http', 'https']:
                return False
            
            if parsed.netloc != self.base_domain:
                return False
            
            skip_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', 
                             '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot',
                             '.pdf', '.doc', '.docx', '.zip', '.rar', '.mp4',
                             '.mp3', '.webp', '.webm']
            if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            return True
        except:
            return False
    
    def has_value_params(self, url):
        parsed = urlparse(url)
        
        if not parsed.query:
            return False
        
        params = parse_qs(parsed.query)
        
        if not params:
            return False
        
        has_value = False
        for key, values in params.items():
            if values and values[0]:
                has_value = True
                break
        
        return has_value
    
    def fetch_page(self, url):
        try:
            resp = self.session.get(url, timeout=TIMEOUT, allow_redirects=True)
            if resp.status_code == 200:
                content_type = resp.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    return resp.text
            return None
        except:
            return None
    
    def crawl(self):
        self.queue.append(self.base_url)
        start_time = time.time()
        
        while self.queue and self.pages_crawled < self.max_pages:
            current_url = self.queue.pop(0)
            
            if current_url in self.visited_urls:
                continue
            
            self.visited_urls.add(current_url)
            self.pages_crawled += 1
            
            html = self.fetch_page(current_url)
            
            if html:
                links = self.extract_links(current_url, html)
                
                for link in links:
                    if self.has_value_params(link):
                        if link not in self.found_urls:
                            self.found_urls.add(link)
                            print(f"[FOUND] {link}")
                            with open(self.output_file, 'a') as f:
                                f.write(link + '\n')
                            f.close()
                    
                    clean_link = link.split('?')[0].split('#')[0]
                    if clean_link not in self.visited_urls and self.is_valid_url(link):
                        if link not in self.queue and clean_link not in self.queue:
                            self.queue.append(clean_link)
            
            time.sleep(0.3)
        
        elapsed_time = time.time() - start_time
        
        print(f"\nSelesai!")
        print(f"   Total ditemukan : {len(self.found_urls)} URL")
        print(f"   Halaman di-crawl: {self.pages_crawled}")
        print(f"   Waktu           : {elapsed_time:.1f} detik")
        print(f"   Tersimpan di    : {self.output_file}")
        
        return self.found_urls



class SimplePHPCrawler:
    
    def __init__(self, base_url, max_pages=200):
        self.base_url = base_url.rstrip('/')
        self.base_domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        
        self.visited_urls = set()
        self.found_urls = set()
        self.queue = []
        
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        domain_clean = self.base_domain.replace('.', '_').replace(':', '_')
        self.output_file = f"found_params_{domain_clean}_{timestamp}.txt"
        
        with open(self.output_file, 'w') as f:
            f.write(f"# Target: {self.base_url}\n")
            f.write(f"# Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("#" + "=" * 60 + "\n\n")
        
        print(f"Auto-save: {self.output_file}\n")
    
    def extract_links_regex(self, html, current_url):
        links = set()
        
        patterns = [
            re.compile(r'href=["\']([^"\']*\?[^"\']*)["\']', re.IGNORECASE),
            re.compile(r'src=["\']([^"\']*\?[^"\']*)["\']', re.IGNORECASE),
            re.compile(r'action=["\']([^"\']*\?[^"\']*)["\']', re.IGNORECASE),
            re.compile(r'location\.href\s*=\s*["\']([^"\']*\?[^"\']*)["\']', re.IGNORECASE),
            re.compile(r'window\.open\(["\']([^"\']*\?[^"\']*)["\']', re.IGNORECASE),
            re.compile(r'(?:https?://[^\s"\'<>\[\]]+\?(?:[^\s"\'<>\[\]]*=\w+[^\s"\'<>\[\]]*)+)', re.IGNORECASE),
            re.compile(r'(?:/[^\s"\'<>\[\]]*\?(?:[^\s"\'<>\[\]]*=\w+[^\s"\'<>\[\]]*)+)', re.IGNORECASE),
        ]
        
        for pattern in patterns:
            matches = pattern.findall(html)
            for match in matches:
                clean = match.split('"')[0].split("'")[0].split('>')[0].strip()
                if clean:
                    full_url = urljoin(current_url, clean)
                    links.add(full_url)
        
        return links
    
    def has_value_params(self, url):
        parsed = urlparse(url)
        if not parsed.query:
            return False
        params = parse_qs(parsed.query)
        for key, values in params.items():
            if values and values[0]:
                return True
        return False
    
    def is_valid_url(self, url):
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False
            if parsed.netloc != self.base_domain:
                return False
            skip_ext = ('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico',
                       '.svg', '.woff', '.woff2', '.ttf', '.eot', '.pdf', '.zip')
            if any(parsed.path.lower().endswith(ext) for ext in skip_ext):
                return False
            return True
        except:
            return False
    
    def crawl(self):
        self.queue.append(self.base_url)
        crawled = 0
        
        while self.queue and crawled < self.max_pages:
            current_url = self.queue.pop(0)
            
            if current_url in self.visited_urls:
                continue
            
            self.visited_urls.add(current_url)
            crawled += 1
            
            try:
                resp = self.session.get(current_url, timeout=10)
                if resp.status_code == 200 and 'text/html' in resp.headers.get('Content-Type', ''):
                    links = self.extract_links_regex(resp.text, current_url)
                    
                    for link in links:
                        if self.has_value_params(link):
                            if link not in self.found_urls:
                                self.found_urls.add(link)
                                print(f"[FOUND] {link}")
                                with open(self.output_file, 'a') as f:
                                    f.write(link + '\n')
                        
                        parsed = urlparse(link)
                        if parsed.netloc == self.base_domain or parsed.netloc == '':
                            clean_link = link.split('?')[0].split('#')[0]
                            if clean_link not in self.visited_urls:
                                self.queue.append(clean_link)
            except:
                pass
            
            time.sleep(0.3)
        
        print(f"\nSelesai!")
        print(f"   Total ditemukan : {len(self.found_urls)} URL")
        print(f"   Halaman di-crawl: {crawled}")
        print(f"   Tersimpan di    : {self.output_file}")
        
        return self.found_urls


def main():
    print("""
        
          TOOLS URL PARAMETER FINDER

Dev      : Ohang
Telegram : Cyber Operation Culture MY
            
    """)
    
    try:
        from bs4 import BeautifulSoup
        use_bs4 = True
    except ImportError:
        print("BeautifulSoup4 tidak terinstall (pip install beautifulsoup4)")
        print("Menggunakan regex mode\n")
        use_bs4 = False
    
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = input("URL target: ").strip()
    
    if not target_url:
        print("URL kosong!")
        return
    
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    print("\nMetode:")
    print(" 1. BeautifulSoup (akurat)")
    print(" 2. Regex (cepat)")
    
    method = input("\nPilih (1/2, default 1): ").strip() or '1'
    
    max_input = input("Max halaman (default 1000): ").strip()
    max_pages = int(max_input) if max_input.isdigit() else 1000
    
    print()
    
    if method == '2' or not use_bs4:
        crawler = SimplePHPCrawler(target_url, max_pages=max_pages)
    else:
        crawler = PHPCrawler(target_url, max_pages=max_pages)
    
    try:
        crawler.crawl()
    except KeyboardInterrupt:
        print(f"\n\nDihentikan!")
        print(f"   Ditemukan: {len(crawler.found_urls)} URL")
        print(f"   Tersimpan: {crawler.output_file}")

if __name__ == "__main__":
    main()
