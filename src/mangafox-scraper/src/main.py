import requests
from scraper import Scraper
from downloader import Downloader

def main():
    # Initialize the scraper and downloader
    scraper = Scraper()
    downloader = Downloader()

    # Scrape the library content
    library_content = scraper.scrape_library()

    # Process and download the content
    for content in library_content:
        downloader.download_content(content)

if __name__ == "__main__":
    main()