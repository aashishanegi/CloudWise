import requests
from bs4 import BeautifulSoup
import csv

# Function to fetch and scrape the articles from the BBC website
def get_bbc_articles():
    url = 'https://www.bbc.com/news'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch articles. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    
    # Locate the main headlines section, skip the first 11, and limit to the next 6
    for item in soup.find_all('a', {'class': 'sc-2e6baa30-0 gILusN'})[11:17]:
        title = item.get_text(strip=True)
        link = item['href']
        
        # Check if the link is a full URL or a relative URL
        if not link.startswith('http'):
            link = 'https://www.bbc.com' + link
        
        # Fetch the article content by visiting the article link
        article_content = get_article_content(link)
        
        articles.append({
            'title': title,
            'article': article_content,
            'link': link
        })
    
    save_to_csv(articles)
    return articles

# Function to fetch the article content from the article page
def get_article_content(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all the paragraphs inside the article body
        article_body = soup.find_all('div', {'data-component': 'text-block'})
        article_text = ' '.join([p.get_text() for p in article_body])
        
        return article_text.strip()
    except Exception as e:
        print(f"Error fetching article content from {link}: {e}")
        return ""

# Function to save the scraped data to a CSV file
def save_to_csv(articles):
    filename = 'bbc_articles.csv'
    fieldnames = ['title', 'article', 'link']
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            writer.writerow(article)
    
    print(f"Data saved to {filename}")

# Run the scraper
articles = get_bbc_articles()

# Output for verification
for article in articles:
    print(f"Title: {article['title']}")
    print(f"Link: {article['link']}")
    print(f"Article: {article['article'][:500]}...")  # Print the first 500 characters of the article
    print('-' * 80)
