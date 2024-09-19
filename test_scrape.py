import requests
from bs4 import BeautifulSoup

def get_articles():
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
    # Adjusting to match the new HTML structure
    for item in soup.find_all('h2', {'data-testid': 'card-headline'}):
        title = item.text.strip()
        parent = item.find_parent('a')  # Get the parent <a> tag to find the link
        link = 'https://www.bbc.com' + parent['href'] if parent else '#'
        articles.append({'title': title, 'link': link})

    print(f"Fetched {len(articles)} articles: {articles}")
    return articles


# Run the test function
if __name__ == "__main__":
    get_articles()
