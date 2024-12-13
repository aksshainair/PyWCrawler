# Web Crawler Project

This project is a web crawler that fetches the details (Title, Description, and Keywords) of a given webpage and its linked pages recursively. The crawler can be configured to crawl a single seed URL or multiple seed URLs from a file. It also allows the user to specify a depth limit for crawling. The crawled data is saved to a CSV file.

## Features
- **Crawl a single or multiple URLs**: Supports both single URL input and reading URLs from a file.
- **Crawl linked pages recursively**: Follows links on each page up to the specified depth limit.
- **Random User-Agent Rotation**: Randomizes the user-agent in requests to simulate different browsers.
- **Error Handling**: Logs errors for failed requests or invalid URLs.
- **Depth Limiting**: Option to limit the crawl depth.
- **Data Saving**: Saves crawled page details (Title, Description, Keywords, URL) to a CSV file.

## Requirements
- Python 3.x
- The following Python packages are required:
  - `requests`
  - `beautifulsoup4`
  - `csv`
  - `logging`
  - `re`
  - `random`
  - `concurrent.futures`

You can install the required packages using pip:

```bash
pip install requests beautifulsoup4
```

## How It Works

1. **Input Seed URL**: The program asks whether you want to input a single URL or a list of URLs from a file.
2. **Fetch Page Details**: For each URL, the crawler fetches the page title, description, and keywords from the page’s meta tags.
3. **Follow Links**: The program recursively follows links found on the page and crawls them until the specified depth is reached.
4. **Data Output**: The crawled data (Title, Description, Keywords, URL) is saved to a CSV file for later use.
5. **Logging**: All activities, including errors and crawled pages, are logged to a log file (`crawler.log`).

## Usage

### Step 1: Run the Script
Run the script by executing the Python file:

```bash
python crawler.py
```

### Step 2: Input Seed URLs
- **Option 1**: Input a single seed URL.
- **Option 2**: Input a file containing multiple URLs (one URL per line).

Example input for single URL:
```
Enter '1' to input a single seed URL or '2' to input a file with multiple seed URLs: 1
Enter the seed URL: https://example.com
```

Example input for a file with multiple URLs:
```
Enter '1' to input a single seed URL or '2' to input a file with multiple seed URLs: 2
Enter the file name containing seed URLs: urls.txt
```

### Step 3: Enable Depth Limiting (Optional)
You will be prompted whether you want to enable depth limiting:
```
Do you want to enable depth limiting? (yes/no): yes
Enter the maximum depth for crawling: 3
```

### Step 4: View the Results
- The crawled data is saved to a CSV file (`crawled_data.csv`).
- Logs are saved in the `crawler.log` file for troubleshooting.

### Example Output (CSV):
The data for each crawled URL will be saved in the following format:

```
Title,Description,Keywords,URL
"Example Title","This is an example description.","keyword1, keyword2","https://example.com"
```

### Example Output (Log):
The log file (`crawler.log`) will contain entries like:

```
2024-12-12 10:00:00 - INFO - Initialized CSV file with headers
2024-12-12 10:01:00 - INFO - Fetched details for https://example.com
2024-12-12 10:02:00 - INFO - Crawled https://example.com
2024-12-12 10:03:00 - ERROR - Error fetching https://brokenlink.com: 404 Not Found
```

### Depth Limiting

The script allows the user to specify a maximum depth for crawling. For example, if the depth is set to `2`, the crawler will crawl the seed URL, then follow links on the seed URL (depth 1), and then follow links found on those pages (depth 2). It will not follow links beyond the specified depth.


### 3. **CSV Output**
The crawled data is saved in a CSV file. Each row represents a page with its title, description, keywords, and URL.

### 4. **Log File**
All events, including successful crawls and errors, are logged to the `crawler.log` file.

## Troubleshooting

- **Invalid URL**: Ensure that the seed URL(s) you provide are valid and accessible.
- **Failed Requests**: Check the `crawler.log` file for error details related to failed requests or network issues.
- **Permission Denied**: If you get a permission error while writing to the CSV file, make sure you have write permissions to the directory.

## Future Enhancements
- **Rate Limiting**: Add support for rate limiting to avoid being blocked by websites.
- **Robots.txt Parsing**: Respect `robots.txt` to avoid crawling disallowed pages.
- **Enhanced Data Extraction**: Add support for extracting more metadata, such as author, publish date, etc.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.