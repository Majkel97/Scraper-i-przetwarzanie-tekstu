import requests
import json
import os
from bs4 import BeautifulSoup


def fetch_page(session, url):
    """
    Fetches the content of a web page using the provided session and URL.

    Parameters:
    - session (requests.Session): A requests session object for making HTTP requests.
    - url (str): The URL of the web page to fetch.

    Returns:
    - BeautifulSoup: A BeautifulSoup object containing the parsed HTML content of the page.

    If an error occurs during the HTTP request, the function prints an error message and returns None.
    """

    try:
        print(f"Fetching {url}")
        response = session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_hotel_links(soup):
    """
    Extracts hotel links from the frequently rated section of a BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): A BeautifulSoup object representing the parsed HTML content.

    Returns:
    - list: A list of modified hotel URLs extracted from the frequently rated section.
            If no frequently rated section is found, an empty list is returned.

    The function searches for a specific div with class "swiper-wrapper" in the provided soup.
    If found, it extracts all 'a' tags within that div, modifies the URLs, and returns the list.
    If the frequently rated section is not found, it prints a message and returns an empty list.
    """

    frequently_rated = soup.find("div", class_="swiper-wrapper")
    if not frequently_rated:
        print("No frequently rated section found.")
        return []

    print("Parsing hotel links.")
    offer_links = frequently_rated.find_all("a")
    urls = []
    for link in offer_links:
        parts = link.get("href").split("/")
        url = "https://www.wakacje.pl/opinie/hotele/" + "/".join(parts[3:])
        index_href = url.rfind("-")
        urls.append(url[: index_href + 1] + "h" + url[index_href + 1 :])
    return urls


def extract_opinions(soup):
    """
    Extracts opinions from the specified section of a BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): A BeautifulSoup object representing the parsed HTML content.

    Returns:
    - list: A list of strings containing extracted opinions.
            If no opinions list is found, an empty list is returned.

    The function looks for a specific div with class "opinions__list" in the provided soup.
    If found, it extracts all 'p' tags with class "opinion__attributes-content" within that div,
    retrieves the text content of each tag, and returns the list of opinions.
    If the opinions list is not found, it prints a message and returns an empty list.
    """

    opinions_list = soup.find("div", class_="opinions__list")
    if not opinions_list:
        print("No opinions list found.")
        return []

    print("Extracting opinions...")
    opinions = opinions_list.find_all("p", class_="opinion__attributes-content")
    return [opinion.get_text(strip=True) for opinion in opinions]


def scrape_hotel_opinions(session, url):
    """
    Scrapes hotel opinions from the specified URL and its paginated pages.

    Parameters:
    - session (requests.Session): A requests session object for making HTTP requests.
    - url (str): The URL of the hotel page to scrape opinions from.

    Returns:
    - list: A list of strings containing scraped opinions.
            If an error occurs during the scraping process, an empty list is returned.

    The function fetches the HTML content of the provided URL using the given session.
    It then extracts opinions from the initial page using the extract_opinions function.
    If pagination is detected, the function iterates through paginated pages and extracts
    opinions from each page. The final list of opinions is returned.
    """

    print(
        "---------------------------------------------------------------------------------------"
    )
    print(f"Scraping opinions for {url}")
    soup = fetch_page(session, url)
    if not soup:
        return []

    opinions = extract_opinions(soup)
    next_page = soup.find("li", class_="pagination__item--next")

    while next_page:
        next_page_url = "https://www.wakacje.pl" + str(next_page.find("a").get("href"))
        soup = fetch_page(session, next_page_url)
        if soup:
            opinions.extend(extract_opinions(soup))
            next_page = soup.find("li", class_="pagination__item--next")
        else:
            break
    return opinions


def main():
    url = "https://www.wakacje.pl/hotele/"
    data = []

    with requests.Session() as session:
        print(f"Fetching main page: {url}")
        soup = fetch_page(session, url)
        if soup:
            hotel_urls = parse_hotel_links(soup)
            for hotel_url in hotel_urls:
                opinions = scrape_hotel_opinions(session, hotel_url)
                data.append({"hotel_url": hotel_url, "opinions": opinions})

    with open("results/1_opinions.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"")
    print(f"Opinions saved to file '1_opinions.py'!")
    print(f"")


if __name__ == "__main__":
    if not os.path.exists("results"):
        os.makedirs("results")
    main()
