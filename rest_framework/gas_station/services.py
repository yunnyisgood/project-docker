from rest_framework.common.services import Reader, Printer, Scraper
import numpy as np
import pandas as pd
from selenium import webdriver
from rest_framework.gas_station.entity import FileDTO
from glob import glob
import re


'''
문제 정의!
셀프 주유소는 정말 저렴할까?
4-1 Selenium 사용하기
4-2 서울시 구별 주유소 가격 정보 얻기
4-5. 구별 주유 가격에 대한 데이터의 정리
4-6 서울시 주유 가격 상하위 10개 주유소 지도에 표기하기
'''

class Service(object):

    def __init__(self):
        self.file = FileDTO()
        self.reader = Reader()
        self.printer = Printer()
        self.scraper = Scraper()

    def get_url(self):
        file = self.file
        reader = self.reader
        printer = self.printer
        scraper = self.scraper
        file.url = "https://www.opinet.co.kr/user/main/mainView.do"
        driver = scraper.driver()
        print(driver.get(file.url))

        gu_list_raw = driver.find_element_by_xpath("""//*[@id="SIGUNGU_NM0"]""")
        gu_list = gu_list_raw.find_elements_by_tag_name("option")
        gu_names = [option.get_attribute("value") for option in gu_list]
        gu_names.remove('')
        print(gu_names)

    def gas_station_price_information(self):
        # print(glob('./data/지역_위치별*.xls'))
        file = self.file
        reader = self.reader
        printer = self.printer

        station_files = glob(('./data/지역_위치별*.xls'))  # 한 번에 여러개 파일을 적용할 때는 glob()
        temp_raw = []
        for i in station_files:
            t = pd.read_excel(i, header=2) # fname, context 사용하려면 각 파일마다 일일히 modeling 해줘야 함.
            temp_raw.append(t)
        station_raw = pd.concat(temp_raw)
        station_raw.info()

        # 여기서 부터 print로 확인
        print('*'*100)
        print(station_raw.head(2))
        print(station_raw.tail(2))


        stations = pd.DataFrame({'Oil_store':station_raw['상호'],
                                 '주소':station_raw['주소'],
                                 '가격':station_raw['휘발유'],
                                 '셀프':station_raw['셀프여부'],
                                 '상표':station_raw['상표']})
        print(stations.head())
        stations['구'] = [i.split()[1] for i in stations['주소']]
        stations['구'].unique()
        print(stations['구'] == '서울특별시')  # 에러 확인
        stations[stations['구'] == '서울특별시'] = '성동구'
        stations['구'].unique()
        print(stations[stations['구'] == '특별시'])  # 에러 확인 2
        stations[stations['구'] == '특별시'] = '도봉구'
        stations['구'].unique()
        print(stations[stations['가격'] == '-'])  # 가격 표시 안된곳 찾아내기
        stations = stations[stations['가격'] != ['-']]
        print(stations[stations['가격'] == '성동구'])

        # 아예 숫자가 아닌 것들을 빼버리자 -> 정규식 re 사용 -> match()함수
        p = re.compile('^[0-9]+$')
        temp_stations = []
        for i in stations:
            if p.match(stations['가격'][i]):
                temp_stations.append(stations['가격'][i])

        stations['가격'] = [float(i) for i in temp_stations['가격']]
        stations.reset_index(inplace=True)  # inplace는 confirm의 의미. 되돌릴 수 없이 바꾸라는 의미
        del stations['index']
        printer.dframe(stations)
        print(stations.columns)
        print(stations.head(2))
        print(stations.tail(2))

if __name__ =='__main__':
    s = Service()
    s.gas_station_price_information()
    # s.get_url()