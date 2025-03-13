import requests
from bs4 import BeautifulSoup
import time


def scrape_loveread(book_id, start_page=1, output_file_path="book.txt"):
    base_url = f"http://loveread.me/read_book.php?id={book_id}&p="
    page = start_page
    all_text = []

    print("Starting scraping process...")

    while True:
        url = base_url + str(page)
        print(f"Fetching page {page}: {url}")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Page {page} not found. Stopping.")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        text_div = soup.find("div", class_="textBook")

        if not text_div:
            print(f"No more text found on page {page}. Stopping.")
            break

        page_text = text_div.get_text(strip=True, separator="\n")
        all_text.append(page_text)
        print(f"Scraped page {page}: {len(page_text)} characters")

        page += 1
        time.sleep(1)  # Be polite, avoid hammering the server

    print("Saving text to file...")
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))

    print(f"Scraping completed. Text saved to {output_file_path}")


# Example usage
scrape_loveread(book_id=78528, output_file_path="C://Users//LENOVO//PycharmProjects//NewsScrapper//book.txt")
