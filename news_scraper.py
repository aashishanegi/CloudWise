import requests
from bs4 import BeautifulSoup
import csv
import schedule
import time
import json
import os

# Function to scrape news from a website
def scrape_news():
    news_data = []
    news_websites = [
        "https://www.bbc.com/news",
        "https://www.cnn.com",
        "https://www.reuters.com",
        "https://www.aljazeera.com",
        "https://www.nytimes.com"
    ]
    
    for site in news_websites:
        try:
            response = requests.get(site)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('h3')  # Update based on each site's article selector
            
            for article in articles[:5]:
                headline = article.get_text(strip=True)
                description = headline  # Placeholder, assuming headline and description are similar
                news_data.append({'headline': headline, 'description': description})
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {site}: {e}")
    
    with open('data/news_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['headline', 'description'])
        writer.writeheader()
        for news in news_data:
            writer.writerow(news)

# Function to fetch gold and silver prices
def fetch_gold_silver_prices():
    try:
        response = requests.get('https://api.metals.live/v1/spot')
        response.raise_for_status()
        prices = response.json()
        
        gold_price = next((item['price'] for item in prices if item['metal'] == 'gold'), 'N/A')
        silver_price = next((item['price'] for item in prices if item['metal'] == 'silver'), 'N/A')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching metal prices: {e}")
        gold_price = silver_price = 'N/A'
    
    return {'gold': gold_price, 'silver': silver_price}

# Function to fetch stock prices (this is just a placeholder)
def fetch_stock_prices():
    try:
        response = requests.get('https://api.example.com/stock-prices')
        response.raise_for_status()
        stock_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stock prices: {e}")
        stock_data = "N/A"
    return stock_data

# Function to fetch weather data
def fetch_weather(location="Dehradun"):
    api_key = os.getenv('WEATHER_API_KEY')
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return "N/A"

# Function to run all tasks
def cron_task():
    print("Running daily cron job to update news, prices, and weather...")
    scrape_news()

    gold_silver_prices = fetch_gold_silver_prices()
    print(f"Gold Price: {gold_silver_prices['gold']} Silver Price: {gold_silver_prices['silver']}")

    weather_data = fetch_weather()
    print(f"Weather: {json.dumps(weather_data, indent=2)}")
    # Store data appropriately or pass to frontend

# Run cron job once daily at the configured time
schedule_time = os.getenv('SCHEDULE_TIME', "00:00")
schedule.every().day.at(schedule_time).do(cron_task)

while True:
    schedule.run_pending()
    time.sleep(1)
