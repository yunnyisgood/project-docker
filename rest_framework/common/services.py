import json
import googlemaps
import pandas as pd
from rest_framework.common.abstracts import PrinterBase, ReaderBase, ScraperBase
from selenium import webdriver


class Printer(PrinterBase):

    def dframe(self, this):
        print(this)
        print(f'cctv 의 type \n {type(this)} 이다.')
        print(f'cctv 의 column \n {this.columns} 이다.')
        print(f'cctv 의 상위 5개 행\n {type(this.head(1))} 이다.')
        print(f'cctv 의 null\n {this.isnull().sum()}개')


class Reader(ReaderBase):

    def new_file(self, file) -> str:
        return file._context + file._fname

    def csv(self, file) -> object:
        return pd.read_csv(f'{self.new_file(file)}.csv', encoding='UTF-8', thousands=',')

    def xls(self, file, header, usecols) -> object:
        return pd.read_excel(f'{self.new_file(file)}.xls', header=header, usecols=usecols)

    def json(self, file) -> object:
        return json.load(open(f'{self.new_file(file)}.json', encoding='UTF-8'))

    def gmaps(self) -> object:
        return googlemaps.Client(key='AIzaSyAdsgtjzlmn8G1wM1wrMrSomONGj-3vt9A')

class Scraper(ScraperBase):

    def driver(self) -> object:
        return webdriver.Chrome('C:/Users/bitcamp/chromedriver')






