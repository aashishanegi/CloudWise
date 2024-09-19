from flask import Flask, render_template
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz

app = Flask(__name__)

# Initialize the summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

articles = []  # Global list to store fetched articles

# Function to fetch articles and summarize
def get_articles():
    url = 'https://www.bbc.com/news'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch articles. Status code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    fetched_articles = []
    for item in soup.find_all('h2', {'data-testid': 'card-headline'}):
        title = item.text.strip()
        parent = item.find_parent('a')
        link = 'https://www.bbc.com' + parent['href'] if parent else '#'
        fetched_articles.append({'title': title, 'link': link})
    
    print(f"Fetched {len(fetched_articles)} articles")
    return fetched_articles

def summarize_article(article_text):
    print(f"Summarizing article: {article_text}")
    summary = summarizer(article_text, max_length=50, min_length=25, clean_up_tokenization_spaces=True, do_sample=False)
    return summary[0]['summary_text']

def update_daily_news():
    global articles
    print(f"Running daily update at {datetime.now()}")
    fetched_articles = get_articles()
    summarized_articles = []
    for article in fetched_articles[:5]:  # Limiting to first 5 articles
        summary = summarize_article(article['title'])
        summarized_articles.append({'title': article['title'], 'summary': summary, 'link': article['link']})
    articles = summarized_articles
    print(f"Updated {len(articles)} articles")

@app.route('/')
def index():
    return render_template('main.html', articles=articles)

# Specify the timezone (for example, Indian Standard Time)
timezone = pytz.timezone('Asia/Kolkata')

def update_daily_news():
    """
    This function fetches the latest articles, summarizes them,
    and stores them in the global `articles` list.
    """
    global articles
    current_time = datetime.now(timezone)  # Get the current time in the specified timezone
    print(f"Running daily update at {current_time} (timezone-aware)")  # Print the time for debugging
    
    # Simulate fetching articles (you can replace this with your actual fetching logic)
    fetched_articles = get_articles()
    
    if not fetched_articles:
        print("No articles were fetched.")
    else:
        print(f"Fetched {len(fetched_articles)} articles.")

    summarized_articles = []
    for article in fetched_articles[:5]:  # Limiting to the first 5 articles for performance
        summary = summarize_article(article['title'])
        summarized_articles.append({'title': article['title'], 'summary': summary, 'link': article['link']})
    
    articles = summarized_articles  # Store the updated articles

if __name__ == '__main__':
    # Set up the scheduler to run the task every 24 hours
    scheduler = BackgroundScheduler(timezone=timezone)  # Explicitly set the timezone for the scheduler
    scheduler.add_job(func=update_daily_news, trigger="interval", hours=24)  # Run every 24 hours
    scheduler.start()

    # Run the function once when the server starts to ensure data is fetched on startup
    update_daily_news()

    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
