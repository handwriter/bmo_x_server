import requests

result = requests.get("http://on24.ru/login", params={"login": "test", "password": "test"}).json()
print(result)
# import pymysql
# db = pymysql.connect(host='31.31.198.18', user='u1233588_leonidl', passwd='asddsafghhgf8954MAILS', db='u1233588_db', charset='utf8')