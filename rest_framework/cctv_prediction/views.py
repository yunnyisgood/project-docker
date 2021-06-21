import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
from services import CCTVService

class CCTV_Api(object):

    @staticmethod
    def main():
        while 1:
            service = CCTVService()
            menu = input('0-Exit, 1-read_csv 2-read_xls 3-read_json')
            if menu == '0':
                break
            elif menu == '1':
                service.csv({'context':'./data/', 'fname':'cctv_in_seoul'})
            elif menu == '2':
                service.xls({'context':'./data/', 'fname':'pop_in_seoul'})
            elif menu == '3':
                service.json({'context':'./data/', 'fname':'geo_simple'})
            else:
                continue

CCTV_Api.main()


