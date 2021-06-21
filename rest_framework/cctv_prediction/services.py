from rest_framework.common.entity import FileDTO
from rest_framework.common.services import Reader, Printer
import pandas as pd
import numpy as np
from sklearn import preprocessing
import folium

'''
> 문제정의 
서울시의 범죄현황과 CCTV 현황을 분석해서                                                                                                                                 
정해진 예산안에서 구별로 다음해에 배분하는 기준을 마련하시오.              
예산안을 입력하면, 구당 할당되는 CCTV 카운티를 자동으로
알려주는 AI 프로그램을 작성하시오. 
'''


class CCTVService(Reader):

    def __init__(self):
        self.file = FileDTO()
        self.reader = Reader()
        self.printer = Printer()

        self.crime_rate_columns = ['살인검거율', '강도검거율', '강간검거율', '절도검거율', '폭력검거율']
        self.crime_columns = ['살인', '강도', '강간', '절도', '폭력']
        self.arrest_columns = ['살인검거', '강도검거', '강간검거', '절도검거', '폭력검거']

    def save_police_pos(self):
        dto = self.file
        reader = self.reader
        printer = self.printer
        dto.context = './data/'
        dto.fname = 'crime_in_seoul'
        crime = reader.csv(dto)
        # printer.dframe(reader.csv(dto))
        station_names = []
        for name in crime['관서명']:
            station_names.append('서울'+str(name[:-1]+'경찰서'))
        station_addrs = []
        station_lats = []
        station_lngs = []
        gmaps = reader.gmaps()
        for name in station_names:
            t = gmaps.geocode(name, language='ko')
            station_addrs.append(t[0].get('formatted_address'))
            t_loc = t[0].get('geometry')
            station_lats.append(t_loc['location']['lat'])
            station_lngs.append(t_loc['location']['lng'])
            # print(f'name{t[0].get("formatted_address")}')
        gu_names = []
        for name in station_addrs:
            t = name.split()
            gu_name = [gu for gu in t if gu[-1] == '구'][0]
            gu_names.append(gu_name)
        crime['구별'] =gu_names
        # 구와 경찰서의 위치가 다른 경우 수작업
        crime.loc[crime['관서명']=='혜화서', ['구별']] =='종로구'
        crime.loc[crime['관서명']=='서부서', ['구별']] =='은평구'
        crime.loc[crime['관서명']=='강서서', ['구별']] =='양천구'
        crime.loc[crime['관서명']=='중앙서', ['구별']] =='성북구'
        crime.loc[crime['관서명']=='방배서', ['구별']] =='서초구'
        crime.loc[crime['관서명']=='수서서', ['구별']] =='강남구'
        crime.to_csv('./saved_data/police_pos.csv')

    def save_cctv_pop(self):
        dto = self.file
        reader = self.reader
        printer = self.printer
        dto.context = './data/'
        dto.fname = 'cctv_in_seoul'
        cctv = reader.csv(dto)
        # printer.dframe(cctv)

        dto.fname = 'pop_in_seoul'
        pop = reader.xls(dto, header=2, usecols='B, D, G, J, N')
        # 또는 => pop = reader.xls(dto, 2, 'B', 'D', 'G', 'J', 'N)
        # printer.dframe(pop)

        cctv.rename(columns={cctv.columns[0]:'구별'}, inplace=True) # coulumn의 [0]번째를 구별로 준다는 의미

        pop.rename(columns={
            pop.columns[0]: '구별',
            pop.columns[1]: '인구수',
            pop.columns[2]: '한국인',
            pop.columns[3]: '외국인',
            pop.columns[4]: '고령자'
        }, inplace=True)
        # print([26])
        pop.drop([26], inplace=True) # inplace=True -> 삭제하는데 동의한다는 의미
        print(pop)
        pop['외국인비율'] = pop['외국인'].astype(int) / pop['인구수'].astype(int) *100
        pop['고령자비율'] = pop['고령자'].astype(int) / pop['인구수'].astype(int) *100

        cctv.drop(['2013년도 이전', '2014년', '2015년', '2016년'], 1, inplace=True)  # 1이라면 세로로 지우기, 0이면 가로로
        cctv_pop = pd.merge(cctv, pop, on='구별')  # merge -> 2개 파일 합치기
        cor1 = np.corrcoef(cctv_pop['고령자비율'], cctv_pop['소계'])
        cor2 = np.corrcoef(cctv_pop['외국인비율'], cctv_pop['소계'])
        print(f'고령자비율과 CCTV의 상관계수 {str(cor1)} \n'
              f'외국인비율과 CCTV의 상관계수 {str(cor2)} ')

        """ -> 아래처럼 출력됨.
         고령자비율과 CCTV 의 상관계수 [[ 1.         -0.28078554]
                                     [-0.28078554  1.        ]] 
         외국인비율과 CCTV 의 상관계수 [[ 1.         -0.13607433]
                                     [-0.13607433  1.        ]]
        r이 -1.0과 -0.7 사이이면, 강한 음적 선형관계,
        r이 -0.7과 -0.3 사이이면, 뚜렷한 음적 선형관계,
        r이 -0.3과 -0.1 사이이면, 약한 음적 선형관계,
        r이 -0.1과 +0.1 사이이면, 거의 무시될 수 있는 선형관계,
        r이 +0.1과 +0.3 사이이면, 약한 양적 선형관계,
        r이 +0.3과 +0.7 사이이면, 뚜렷한 양적 선형관계,
        r이 +0.7과 +1.0 사이이면, 강한 양적 선형관계
        고령자비율 과 CCTV 상관계수 [[ 1.         -0.28078554] 약한 음적 선형관계
                                    [-0.28078554  1.        ]]
        외국인비율 과 CCTV 상관계수 [[ 1.         -0.13607433] 거의 무시될 수 있는
                                    [-0.13607433  1.        ]]                        
         """
        cctv_pop.to_csv('./saved_data/cctv_pop.csv')

    def save_police_norm(self):
        dto = self.file
        reader = self.reader
        dto.context = './saved_data/'
        dto.fname = 'police_pos'
        police_pos = reader.csv(dto)
        police = pd.pivot_table(police_pos, index='구별', aggfunc=np.sum)
        police['살인검거율'] = (police['살인 검거'].astype(int) / police['살인 발생'].astype(int) * 100)
        police['강도검거율'] = (police['강도 검거'].astype(int) / police['강도 발생'].astype(int) * 100)
        police['강간검거율'] = (police['강간 검거'].astype(int) / police['강간 발생'].astype(int) * 100)
        police['절도검거율'] = (police['절도 검거'].astype(int) / police['절도 발생'].astype(int) * 100)
        police['폭력검거율'] = (police['폭력 검거'].astype(int) / police['폭력 발생'].astype(int) * 100)
        police.drop(columns={'살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거'}, axis=1, inplace=True)

        for i in self.crime_rate_columns:
            police.loc[police[i] > 100, 1] = 100  # 데이터값의 기간 오류로 100을 넘으면 100으로 계산하라는 의미
        police.rename(columns={
            '살인 발생': '살인',
            '강도 발생': '강도',
            '강간 발생': '강간',
            '철도 발생': '철도',
            '폭력 발생': '폭력',
        }, inplace=True)

        x = police[self.crime_rate_columns].values
        min_max_scalar = preprocessing.MinMaxScaler()
        """
            스케일링은 선형변환을 적용하여
            전체 자료의 분포를 평균 0, 분산 1이 되도록 만드는 과정
            """
        x_scaled = min_max_scalar.fit_transform(x.astype(float))
        """
            정규화 normalization
            많은 양의 데이터를 처리함에 있어 데이터의 범위(도메인)를 일치시키거나
            분포(스케일)를 유사하게 만드는 작업
            """
        police_norm = pd.DataFrame(x_scaled, columns=self.crime_columns, index=police.index)
        police_norm[self.crime_rate_columns] = police[self.crime_rate_columns]
        police_norm['범죄'] = np.sum(police_norm[self.crime_rate_columns], axis=1)
        police_norm['검거'] = np.sum(police_norm[self.crime_columns], axis=1)
        police_norm.to_csv('./saved_data/police_norm.csv', sep=',')

    def save_folium_map(self):
        # DataFrame으로 정형화
        dto = self.file
        reader = self.reader
        dto.context = './saved_data/'
        dto.fname = 'police_norm'
        police_norm = reader.csv(dto)

        dto.fname = 'police_pos'
        police_pos = reader.csv(dto)

        dto.context = './data/'
        dto.fname = 'crime_in_seoul'
        crime = reader.csv(dto)

        dto.fname = 'kr-state'
        state_geo = reader.json(dto)

        # 시각화
        station_names = []
        for name in crime['관서명']:
            station_names.append('서울' + str(name[:-1] + '경찰서'))
        station_addrs = []
        station_lats = []
        station_lngs = []
        gmaps = reader.gmaps()
        for name in station_names:
            t = gmaps.geocode(name, language='ko')
            station_addrs.append(t[0].get('formatted_address'))
            t_loc = t[0].get('geometry')
            station_lats.append(t_loc['location']['lat'])
            station_lngs.append(t_loc['location']['lng'])

        police_pos['lats'] = station_lats
        police_pos['lngs'] = station_lngs
        temp = police_pos[self.arrest_columns] / police_pos[self.arrest_columns].max()
        police_pos['검거'] = np.sum(temp, axis=1)

        folium_map = folium.Map(location=[37.5502, 126.982], zoom_start=12, title='Stamen Toner')  # title 색깔은 레드

        folium.Choropleth(
            geo_data=state_geo,
            name="choropleth",
            data=tuple(zip(police_norm['구별'], police_norm['범죄'])),
               # zip(a, b) -> a, b를 하나로 합친 다음 tuple로 전환
            columns=["State", "Crime Rate"],
            key_on="feature.id",
            fill_color="PuRd", # 색깔은 퍼플
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Unemployment Rate (%)",
        ).add_to(folium_map)
        for i in police_pos.index:
            folium.CircleMarker([police_pos['lat'][i], police_pos['lng'][i]], radius=police_pos['검거'][i] *10,
                                                                    fill_color='#0a0a32').add_to(folium_map)

        folium.LayerControl().add_to(folium_map)
        folium_map.save('./saved_data/seoul_crime.html')


if __name__ == '__main__':
    service = CCTVService()
    service.save_folium_map()
    # service.save_police_norm()
    # service.save_cctv_pop()
    # service.save_police_pos()

