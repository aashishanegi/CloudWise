from flask import Flask, render_template
from transformers import pipeline
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Initialize the summarizer with the explicit setting for clean_up_tokenization_spaces
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

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
    for item in soup.find_all('h2', {'data-testid': 'card-headline'}):
        title = item.text.strip()
        parent = item.find_parent('a')  # Get the parent <a> tag to find the link
        link = 'https://www.bbc.com' + parent['href'] if parent else '#'
        articles.append({'title': title, 'link': link})

    print(f"Fetched {len(articles)} articles: {articles}")
    return articles

def summarize_article(article_text):
    # Print the title being summarized to see if this part is working
    print(f"Summarizing article: {article_text}")
    summary = summarizer(article_text, max_length=50, min_length=25, clean_up_tokenization_spaces=True, do_sample=False)
    print(f"Summary: {summary[0]['summary_text']}")
    return summary[0]['summary_text']

@app.route('/')
def index():
    print("Fetching articles...")
    articles = get_articles()
    
    # If no articles were fetched, log it
    if len(articles) == 0:
        print("No articles were fetched.")
    
    summarized_articles = []
    for article in articles[:5]:  # Limiting to the first 5 articles for performance
        summary = summarize_article(article['title'])
        summarized_articles.append({'title': article['title'], 'summary': summary, 'link': article['link']})
    
    print(f"Summarized {len(summarized_articles)} articles.")
    return render_template('index.html', articles=summarized_articles)

if __name__ == '__main__':
    app.run(debug=True)
