import requests
from bs4 import BeautifulSoup
import time
import sys
import threading
from queue import Queue

# A worker thread to fetch and parse the news from the provided URLs
class NewsFetcherThread(threading.Thread):
    def __init__(self, name, queue, url, news_site_name):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.url = url
        self.news_site_name = news_site_name

    def run(self):
        while True:
            response = requests.get(self.url)
            if self.url == 'https://www.foxnews.com/category/politics/elections/presidential-primaries-candidate-tracker':
              soup = BeautifulSoup(response.text, 'html.parser')
              news_list = soup.find_all('article', {'class': 'article'})

              for news in news_list:
                 link = self.news_site_name
                 title = news.find('h4', class_='title').text
                 abstract = news.find('p', class_='dek').text
                 Time = news.find('span', class_='time').text
                 news_item = (title, abstract, Time, link)
                 if title not in self.queue.seen_titles:
                    self.queue.put(news_item)
                    self.queue.seen_titles.add(title)
                    
              time.sleep(30)
             
            if self.url == 'https://abcnews.go.com/elections':
              soup = BeautifulSoup(response.text, 'html.parser')
              news_list = soup.find_all('section', {'class': 'ContentRoll__Item'})

              for news in news_list:
                link = self.news_site_name
                title = news.find('h2').text
                Time = news.find('div', class_='ContentRoll__TimeStamp').find('div', class_='TimeStamp__Date').text
                abstract = news.find('div', class_='ContentRoll__Desc').text
                news_item = (title, abstract, Time, link)
                if title not in self.queue.seen_titles:
                    self.queue.put(news_item)
                    self.queue.seen_titles.add(title)
                    
              time.sleep(30)
                
            if self.url == 'https://russian.rt.com/business':
              soup = BeautifulSoup(response.text, 'html.parser')
              news_list = soup.find_all('li', {'class': 'listing__column_sections'})

              for news in news_list:
                link = self.news_site_name
                title = news.find('div', class_='card__heading_sections').find('a').text.strip()
                Time = news.find('div', class_='card__date_sections').find('time').text.strip()
                abstract = news.find('div', class_='card__summary_sections').text.strip()
                news_item = (title, abstract, Time, link)
                if title not in self.queue.seen_titles:
                    self.queue.put(news_item)
                    self.queue.seen_titles.add(title)
                    
              time.sleep(30)

class Queue:
    def __init__(self):
        self.queue = []
        self.seen_titles = set()

    def put(self, item):
        self.queue.append(item)

    def get(self):
        if self.queue:
            return self.queue.pop(0)
        else:
            return None

# The main class to fetch the news and start the background threads
class NewsAggregator:
    def __init__(self):
        self.news_queue = Queue()
        self.urls = ['https://www.foxnews.com/category/politics/elections/presidential-primaries-candidate-tracker', 'https://abcnews.go.com/elections', 'https://russian.rt.com/business']
        self.news_sites = ['Fox News', 'ABC News', 'RT News']

    def start_fetching_news(self):
        for i in range(len(self.urls)):
            t = NewsFetcherThread("Thread-{}".format(i + 1), self.news_queue, self.urls[i], self.news_sites[i])
            t.daemon = True
            t.start()

    def print_news(self):
        while True:
          try:
            news_item = self.news_queue.get()
            if news_item is not None:
             time.sleep(0.5)
             print("Source: ", news_item[3])
             print("Title: ", news_item[0])
             print("Description: ", news_item[1])
             print("Time: ", news_item[2])
             print("--------------------------------------------------------------------------------------------------")
          except (KeyboardInterrupt, SystemExit):
            print("\n Exiting the application... \n")
            sys.exit()

if __name__ == "__main__":
    news_aggregator = NewsAggregator()
    news_aggregator.start_fetching_news()
    news_aggregator.print_news()
