import requests
from bs4 import BeautifulSoup
import time
import sys
import threading
from queue import Queue

class NewsFetcher: 
    def __init__(self, name, queue, url, news_site_name):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.url = url
        self.news_site_name = news_site_name
    
    def GetFoxNews(self):
        url = 'https://www.foxnews.com/category/politics/elections/presidential-primaries-candidate-tracker'
        html = requests.get(url).text
        soup = bs4.BeautifulSoup(html, features='html.parser')
        news_divs = soup.find_all('article', class_='article')
        news_list = []

        for div in news_divs:
            title = div.find('h4', class_='title').text
            summary = div.find('p', class_='dek').text
            date = div.find('span', class_='time').text
            link = 'foxnews.com'
            news_list.append( NewsInfo( title, date, summary, link ))
        
        return news_list
    pass

    def GetAbcNews(self):
        url = 'https://abcnews.go.com/elections'
        html = requests.get(url).text
        soup = bs4.BeautifulSoup(html, features='html.parser')
        news_sections = soup.find_all('section', class_='ContentRoll__Item')
        news_list = []

        for section in news_sections:
            title = section.find('h2').text
            date = section.find('div', class_='ContentRoll__TimeStamp').find('div', class_='TimeStamp__Date').text
            summary = section.find('div', class_='ContentRoll__Desc').text
            link='abcnews.go.com'        
            news_list.append( NewsInfo( title, date, summary, link ))
        
        return news_list
    pass

    def GetRtNews(self):
        url = 'https://russian.rt.com/business'
        html = requests.get(url).text
        soup = bs4.BeautifulSoup(html, features='html.parser')
        news_items = soup.find_all('li', class_='listing__column_sections')
        news_list = []

        for item in news_items:
            title = item.find('div', class_='card__heading_sections').find('a').text.strip()
            date = item.find('div', class_='card__date_sections').find('time').text.strip()
            summary = item.find('div', class_='card__summary_sections').text.strip()
            link='russian.rt.com'        
            news_list.append( NewsInfo( title, date, summary, link ))

        return news_list
    pass

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

if __name__ == '__main__':
    updater = NewsUpdater()
    app = ConsoleApp(updater)
    app.run()
