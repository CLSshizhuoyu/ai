from api_key_manager import get_api_key
import webbrowser
import requests
import json
import time
size = ["1024x1024", "768x1344", "864x1152", "1344x768", "1152x864", "1440x720", "720x1440"]

def main(head_question, mode, si = 1):
    if head_question:
        en = head_question
    else:
        en = input("请输入内容：")
    t1 = time.time()

    url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    headers = {
        "Authorization": get_api_key(name="Pic"),
        "Content-Type": "application/json"
    }
    data = {
        "model": "CogView-3-Flash",
        "prompt": en,
        "size" : size[si - 1]
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
