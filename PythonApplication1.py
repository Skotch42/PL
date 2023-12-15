import requests
import bs4
import time
import queue
import threading

class NewsInfo:
    def __init__(self, t, d, s, l):
        self.title = t
        self.date = d
        self.summary = s
        self.link = l

    def __str__(self):
        return f"Title: {self.title}\nDate: {self.date}\nLink: {self.link}\nSummary: {self.summary}\n=======================================================================================================================\n"

class NewsFetcher: 
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

class NewsUpdater:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.shown_news = set()
        self.news_queue = queue.Queue()

    def update_news(self):      
        while True:
            news = [*self.news_fetcher.GetFoxNews(), *self.news_fetcher.GetAbcNews(), *self.news_fetcher.GetRtNews()]            
            for item in news:
                if item.title not in self.shown_news:
                    self.news_queue.put(item)
                    self.shown_news.add(item.title)                    
            time.sleep(10) # raising this delay can sometimes increase the amount of articles shown (change if not all news on the website are shown)

class ConsoleApp:
    def __init__(self, news_updater):
        self.news_updater = news_updater

    def run(self):
        updater_thread = threading.Thread(target=self.news_updater.update_news, daemon=True)
        updater_thread.start()

        try:
            while True:
                if not self.news_updater.news_queue.empty():
                    new_item = self.news_updater.news_queue.get()
                    print(new_item, '\n')
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print("Exiting the application.\n")

if __name__ == '__main__':
    updater = NewsUpdater()
    app = ConsoleApp(updater)
    app.run()