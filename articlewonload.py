import os
import requests
import re
from bs4 import BeautifulSoup
from newspaper import Article
from datetime import datetime

def download_article_as_markdown(url, output_folder):
    # Download and parse the article
    article = Article(url)
    article.download()
    article.parse()

    # Prepare filename
    title = article.title.strip().replace(' ', '_').replace('/', '_')
    if not title:
        title = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title[:50]}.md"

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    filepath = os.path.join(output_folder, filename)

    # Optional metadata
    date_str = article.publish_date.strftime("%Y-%m-%d") if article.publish_date else "Unknown Date"
    metadata = f"# {article.title}\n\n" \
               f"**URL:** [{url}]({url})  \n" \
               f"**Published:** {date_str}\n\n"

    # Combine metadata and cleaned article text
    content = metadata + article.text.strip()

    # Save as .md file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Markdown article saved to: {filepath}")

def get_article_links_from_page(listing_url):
    """Extract article links from a given listing page."""
    base_url = "https://edhrec.com"
    response = requests.get(listing_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    article_links = []

    # Use more general selector for article links
    for link_tag in soup.select('a[href^="/articles/"]'):
        href = link_tag.get('href')
        if href:
            full_url = base_url + href
            if full_url not in article_links:
                article_links.append(full_url)

    return article_links


# Example usage
#url = "https://edhrec.com/articles/the-best-free-white-spells-for-commander"
#output_folder = "data/Articles/Guides"
#download_article_as_markdown(url, output_folder)

listing_url = "https://edhrec.com/articles/page/"
output_folder = "data/Articles/Guides"
article_urls =[]
for n in range(101,300,1):
    url = listing_url + str(n)
    articles = get_article_links_from_page(url)
    article_urls.extend(articles)

article_pattern = re.compile(r'^https://edhrec\.com/articles/(?!tag/|author/|page/)[a-z0-9\-]+$', re.IGNORECASE)

valid_articles = [url for url in article_urls if article_pattern.match(url)]

for url in valid_articles:
    try:
        download_article_as_markdown(url, output_folder)
    except Exception as e:
        print(f"Failed to process {url}: {e}")