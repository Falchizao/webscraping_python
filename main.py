import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from xlwt import *

excel = Workbook(encoding = 'utf-8')

table = excel.add_sheet('data')
table.write(0, 0, 'filme_url')
table.write(0, 1, 'filme_nome')
table.write(0, 2, 'filme_desc')
table.write(0, 3, 'filme_nota')
table.write(0, 4, 'filme_popularidade')
table.write(0, 5, 'filme_artistas')
table.write(0, 6, 'filme_metaScore')
table.write(0, 7, 'filme_data')
table.write(0, 8, 'filme_genero')

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:

    def __init__(self, urls=[]):
        self.visited_urls = []
        self.urls_to_visit = urls
        self.linha = 1
        self.userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

    def download_url(self, url):
        headers = {"user-agent": self.userAgent}
        return requests.get(url, headers=headers).text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find('table', {'class': 'chart'}).find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl_filme(self, urlconcat):
        html = self.download_url(urlconcat)
        soup = BeautifulSoup(html, 'html.parser')

        filme_title = soup.find("title").getText()
        filme_score = soup.find("span", {"class": "sc-7ab21ed2-1 jGRxWM"}).getText()
        filme_desc = soup.find("span", {"class": "sc-16ede01-2 gXUyNh"}).getText()
        filme_popularidade = soup.find("div", {"class": "sc-edc76a2-1 gopMqI"}).getText()
        filme_data = soup.find("span", {"class" : "sc-8c396aa2-2 itZqyK"}).getText()
        filme_genero = soup.find("span", {"class" : "ipc-chip__text"}).getText()
        filme_metaScore = soup.find("span", {"class" : "score-meta"}).getText()
        filme_artistas = soup.find("a", {"class": "ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"}).getText()

        table.write(self.linha, 0, urlconcat)
        table.write(self.linha, 1, filme_title)
        table.write(self.linha, 2, filme_desc)
        table.write(self.linha, 3, filme_score)
        table.write(self.linha, 4, filme_popularidade)
        table.write(self.linha, 5, filme_artistas)
        table.write(self.linha, 6, filme_metaScore)
        table.write(self.linha, 7, filme_data)
        table.write(self.linha, 8, filme_genero)

    def crawl(self, url):
        html = self.download_url(url)
        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(url)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling: {url}')

            try:
                self.crawl(url)
            except Exception:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                if self.linha > 1:
                    self.visited_urls.append(url)
                    try:
                        self.crawl_filme(url)
                    except:
                        print(f' err on url: {url}')
                self.linha += 1
                if self.linha > 15:
                    break

if __name__ == '__main__':
    Crawler(urls=['https://www.imdb.com/chart/top/?ref_=nv_mv_250']).run()
    excel.save('web_crawler_vinicius_marcelo.xls')