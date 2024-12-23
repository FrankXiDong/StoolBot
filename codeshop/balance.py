from openai import OpenAI
from urllib.parse import urlencode
from urllib.request import urlopen
import requests, json


def balance(key):
    url = "https://api.deepseek.com/user/balance"
    payload = {}
    headers = {
        "Accept": "application/json",
        #'Authorization': 'Bearer sk-5cd23846d4304f63b93db419bf87641e'
        "Authorization": "Bearer " + key,  # 临时
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    data = json.loads(response.text)
    a = data["balance_infos"][0]["total_balance"]
    return a
