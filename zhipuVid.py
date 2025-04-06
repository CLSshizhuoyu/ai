import requests
import json
import time
def main(head_question, mode, pic=""):
    if head_question:
        en = head_question
    else:
        en = input("请输入内容：")
    t1 = round(time.time(), 2)

    url = "https://open.bigmodel.cn/api/paas/v4/videos/generations"
    headers = {
        "Authorization": "6fa8f15bd00f4cccb9b1b0fd40476de4.0QiDr1JSiSfXMEpA",
        "Content-Type": "application/json"
    }
    if pic:
        data = {
            "model": "CogVideoX-Flash",
            "prompt": en,
            "with_audio" : False,
            "image_url" : pic
        }
    else:
        data = {
            "model": "CogVideoX-Flash",
            "prompt": en,
            "with_audio" : False
        }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    print("已发送请求，正在等待回复…")
    ID = response.json()["id"]
    t2 = time.time()
    t4 = round(t2 - t1, 2)
    print(f"任务创建成功，正在生成中… {t4}s")

    time.sleep(10)

    url = f"https://open.bigmodel.cn/api/paas/v4/async-result/{ID}"
    headers = {
        "Authorization": "6fa8f15bd00f4cccb9b1b0fd40476de4.0QiDr1JSiSfXMEpA",
        "Content-Type": "application/json"
    }

    for times in range(10):
        response = requests.get(url, headers = headers)
        response.raise_for_status()
        last = response.json()
        if last['task_status'] == 'SUCCESS':
            break
        elif times == 9:
            print("请求超时，请尝试重试！")
            return([None, None])
        else:
            time.sleep(5)
    
    t3 = time.time()
    t5 = round(t3 - t1, 2)
    print(f"生成完毕，总用时{t5}s")
    # 使用Chrome浏览器打开特定网址
    if mode:
        return [last['video_result'][0]['url'], 
            last['video_result'][0]['cover_image_url']]
    else:
        import webbrowser
        webbrowser.open(last['video_result'][0]['url'])
        webbrowser.open(last['video_result'][0]['cover_image_url'])
        return 0


'''
client = ZhipuAI(api_key="")  # 请填写您自己的APIKey

response = client.videos.generations(
    model="cogvideox-2",
    prompt="比得兔开小汽车，游走在马路上，脸上的表情充满开心喜悦。"
    quality="quality",  # 输出模式，"quality"为质量优先，"speed"为速度优先
    with_audio=True,
    size="1920x1080",  # 视频分辨率，支持最高4K（如: "3840x2160"）
    fps=30,  # 帧率，可选为30或60
)
print(response)
client = ZhipuAI(api_key="")  # 请填写您自己的APIKey

response = client.videos.retrieve_videos_result(
    id="8868902201637896192"
)
print(response)
'''