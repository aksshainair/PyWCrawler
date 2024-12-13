import requests
from bs4 import BeautifulSoup
import csv
import logging
import re
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import sys

# Configure logging
logging.basicConfig(filename='crawler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List of user agents to randomize requests
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
]

def get_random_user_agent():
    """Return a random user agent from the list."""
    return random.choice(USER_AGENTS)

def is_valid_url(url):
    """Check if the provided URL is valid."""
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

# Global lists to keep track of crawled and crawling URLs
already_crawled = []
crawling = []

def get_details(url):
    """Fetch and parse the details of the given URL."""
    headers = {'User-Agent': get_random_user_agent()}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.title.string if soup.title else ""
    description = ""
    keywords = ""

    for meta in soup.find_all('meta'):
        if 'name' in meta.attrs:
            if meta.attrs['name'].lower() == 'description':
                description = meta.attrs['content']
            if meta.attrs['name'].lower() == 'keywords':
                keywords = meta.attrs['content']

    logging.info(f"Fetched details for {url}")
    return {"Title": title.strip() if title else "", "Description": description.strip(), "Keywords": keywords.strip(), "URL": url}

def follow_links(url, depth, max_depth, depth_limit_enabled):
    """Recursively follow links from the given URL up to the specified depth."""
    if depth_limit_enabled and depth > max_depth:
        return

    global already_crawled, crawling
    headers = {'User-Agent': get_random_user_agent()}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    for link in soup.find_all('a', href=True):
        l = link['href']
        if not l.startswith('https'):
            l = requests.compat.urljoin(url, l)

        if l not in already_crawled:
            already_crawled.append(l)
            crawling.append((l, depth + 1))
            details = get_details(l)
            if details:
                logging.info(f"Crawled {l}")
                save_to_csv(details)

    if crawling:
        next_url, next_depth = crawling.pop(0)
        follow_links(next_url, next_depth, max_depth, depth_limit_enabled)

def save_to_csv(data):
    """Save the crawled data to a CSV file."""
    try:
        with open('crawled_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Description', 'Keywords', 'URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(data)
        logging.info(f"Saved data for {data['URL']} to CSV")
    except Exception as e:
        logging.error(f"Error saving data to CSV: {e}")

def crawl_seed_url(seed_url, max_depth, depth_limit_enabled):
    """Crawl the given seed URL and follow links up to the specified depth."""
    seed_details = get_details(seed_url)
    if seed_details:
        save_to_csv(seed_details)
        already_crawled.append(seed_url)
    follow_links(seed_url, 0, max_depth, depth_limit_enabled)

if __name__ == "__main__":
    seed_urls = []

    # User input for seed URLs
    choice = input("Enter '1' to input a single seed URL or '2' to input a file with multiple seed URLs: ")
    if choice == '1':
        while True:
            start = input("Enter the seed URL: ")
            if is_valid_url(start):
                seed_urls.append(start)
                break
            else:
                print("Invalid URL. Please enter a valid URL.")
    elif choice == '2':
        file_name = input("Enter the file name containing seed URLs: ")
        try:
            with open(file_name, 'r') as file:
                for line in file:
                    url = line.strip()
                    if is_valid_url(url):
                        seed_urls.append(url)
                    else:
                        print(f"Invalid URL found in file: {url}")
        except FileNotFoundError:
            print("File not found. Please enter a valid file name.")
            exit(1)
        print(seed_urls)
    else:
        print("Invalid choice. Please restart the program and enter '1' or '2'.")
        exit(1)

    # Initialize CSV file with headers
    try:
        with open('crawled_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Description', 'Keywords', 'URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        logging.info("Initialized CSV file with headers")
    except Exception as e:
        logging.error(f"Error initializing CSV file: {e}")

    # User input for depth limiting
    depth_limit_enabled = input("Do you want to enable depth limiting? (yes/no): ").strip().lower() == 'yes'
    max_depth = 0
    if depth_limit_enabled:
        max_depth = int(input("Enter the maximum depth for crawling: "))

    # Start crawling using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(crawl_seed_url, url, max_depth, depth_limit_enabled): url for url in seed_urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error crawling {url}: {e}")

    logging.info(f"Finished crawling. Total links crawled: {len(already_crawled)}")
    print(f"Finished crawling. Total links crawled: {len(already_crawled)}")