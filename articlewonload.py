import os
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

# Example usage
url = "https://www.tcgplayer.com/content/article/Top-10-Best-Creature-Types-in-MTG/6cd88f78-e355-4d08-88cd-eede4c34056b/"
output_folder = "data/Articles/Guides"
download_article_as_markdown(url, output_folder)
