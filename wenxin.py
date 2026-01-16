import requests
import json
from api_key_manager import get_api_key

def main(head_question):
    if head_question:
        en = head_question
    else:
        en = input("请输入内容：")
    url = f"https://agentapi.baidu.com/assistant/getAnswer?appId=848ND8p4mQZBogrzhFBYM5iBfLCmi8Cu&secretKey={get_api_key(name='wenxin')}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        'message': {'content': {'type': 'text', 'value': {'showtext': en}}},
        'sourse': '848ND8p4mQZBogrzhFBYM5iBfLCmi8Cu',
        'from': 'openapi',
        'openId': 'test'
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            content = response.json()
            if content.get('data'):
                chunk = content['data']['content'][0]['data']
                print(chunk, end='')
