import webbrowser
import requests
import json
import time
def main(head_question, mode):
    if head_question:
        en = head_question
    else:
        en = input("请输入内容：")
    t1 = time.time()

    url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    headers = {
        "Authorization": "0a364811e3394194897d5cf61e933a94.NATjpJv8z77Eo2l9",
        "Content-Type": "application/json"
    }
    data = {
        "model": "CogView-3-Flash",
        "prompt": en
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    t2 = time.time()
    t3 = round(t2 - t1, 2)
    print(f"生成完毕，总用时{t3}s")
    if mode:
        return [response.json()['data'][0]['url'], None]
    else:
        webbrowser.open(response.json()['data'][0]['url'])