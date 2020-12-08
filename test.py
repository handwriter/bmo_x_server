import requests

result = requests.get("http://127.0.0.1:5000/change_win", headers={"login": "admin", "password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918", "target_login": 'fewfew'}).json()
print(result)