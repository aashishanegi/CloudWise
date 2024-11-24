import requests
from bs4 import BeautifulSoup
import csv

# Function to fetch and scrape the articles from The Hindu website
def get_hindu_articles():
    url = 'https://www.thehindu.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch articles. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    
    # Locate the <h3> tags with class 'ABC' and find <a> tags inside them
    for item in soup.find_all('h3', {'class': 'title'})[3:9]:  # Adjust class name 'ABC' based on actual structure
        anchor_tag = item.find('a')  # Find the <a> tag inside the <h3>
        if anchor_tag:
            title = anchor_tag.get_text(strip=True)
            link = anchor_tag['href']
            
            # Check if the link is a full URL or a relative URL
            if not link.startswith('http'):
                link = 'https://www.thehindu.com' + link
            
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
        
        # Get the main content area with class 'articlebodycontent'
        article_body = soup.find('div', {'class': 'articlebodycontent col-xl-9 col-lg-12 col-md-12 col-sm-12 col-12'})
        
        # Initialize an empty string for the article text
        article_text = ""
        
        # Ensure the article_body is found
        if article_body:
            # Get all the paragraphs within the article body and stop before the publish time
            publish_time_tag = article_body.find('p', {'class': 'publish-time-new'})
            
            # Loop through all the <p> tags before the publish time tag
            for p in article_body.find_all('p'):
                if p == publish_time_tag:
                    break  # Stop before the publish-time-new tag
                article_text += p.get_text() + " "  # Add each paragraph's text to article_text
        
        return article_text.strip()  # Return the cleaned article text
    except Exception as e:
        print(f"Error fetching article content from {link}: {e}")
        return ""


# Function to save the scraped data to a CSV file
def save_to_csv(articles):
    filename = 'hindu_articles.csv'
    fieldnames = ['title', 'article', 'link']
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            writer.writerow(article)
    
    print(f"Data saved to {filename}")

# Run the scraper
articles = get_hindu_articles()

# Output for verification
for article in articles:
    print(f"Title: {article['title']}")
    print(f"Link: {article['link']}")
    print(f"Article: {article['article'][:500]}...")  # Print the first 500 characters of the article
    print('-' * 80)
