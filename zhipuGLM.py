import json
import time
import requests
from datetime import datetime


#前置问题预设，如果问题含特殊字符或无法键入，写入此变量
#变量若有问题预设将只会运行一遍

class other():
    def Help():
        h = input("请输入帮助类型：( 1 命令咒语 q 退出)")
        if h == '1':
            print(f"\n命令控制：在输入的问题前添加命令即可获得更准确答复。\n命令有：\n\编程 \解题\n\数据分析\n\翻译\n\创作\n\n普通对话或翻译不需要命令\n")
        elif h.lower() == 'q':
            pass
        else:
            print("无法识别，请重新尝试")
    
    def history():
        with open('deepseek对话记录.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()

        space_lines_count = 0
        for i in range(len(lines) - 1, -1, -1):
            if '=-=-' in lines[i]:
                space_lines_count += 1
                if space_lines_count == 10:
                    break
        print(f'\n\n')
        print(''.join(lines[i:]))
        print(f'\n已找到{space_lines_count}条结果\n')

def Other():
    a = input("请输入类型：( 1 帮助 2 历史对话 q 退出)")
    if a == '1':
        other.Help()
    elif a == '2':
        other.history()
    elif a.lower() == 'q':
        pass
    else:
        print("无法识别，请重新尝试")

def save_to_file(file, content, is_question=False):
    """保存对话内容到文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if is_question:
        file.write(
            f"\n[{timestamp}] Question:\n{content}\n\n[{timestamp}] Answer:\n")
    else:
        file.write(content)

def main(head_question):
    # 配置
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": "1d15bd7c402c456980138df6f289a7df.I9zNkevSMUxnOfK7",
        "Content-Type": "application/json"
    }

    # 打开文件用于保存对话
    with open("deepseek对话记录.txt", "a", encoding="utf-8") as file:
        times = 0
        while True:
            # 获取用户输入
            times += 1
            if head_question:
                question = head_question
            else:
                begin_time = round(time.time(), 1)
                if times == 1:
                    question = input("请输入您的问题 (输入 q 退出, o 其他): ").strip()
                else:
                    question = input("\n请输入您的问题 (输入 q 退出, o 其他): ").strip()
                if question.lower() == 'q':
                    print("程序已退出")
                    break
                if question.lower() == 'o':
                    print("-" * 30)
                    Other()
                    break
                if len(question) >= 50:
                    print("字数过长")
                    continue
                end_time = round(time.time(), 1)
                if end_time - begin_time < 5:
                    continue
            temperature = 1.3
            if '\编程' in question or '\解题' in question:
                question = question[3 : len(question)]
                temperature = 0.0
            elif '\数据分析' in question:
                question = question[5 : len(question)]
                temperature = 1.0
            elif '\创作' in question:
                question = question[3 : len(question)]
                temperature = 1.5
            else:pass
            # 保存问题
            save_to_file(file, question, is_question=True)

            # 准备请求数据
            data = {
                "model" : "glm-4-flash",
                "messages" : [
                    {
                        "role": "system",
                        "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "top_p" : 0.7,
                "temperature" : 0.95,
                "max_tokens" : 1024,
                "stream" : True
            }

            try:
                # 发送流式请求
                response = requests.post(
                    url, json=data, headers=headers, stream=True)
                response.raise_for_status()  # 检查响应状态

                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            if line == 'data: [DONE]':
                                continue

                            try:
                                content = json.loads(
                                    line[6:])  # 去掉 'data: ' 前缀
                                if content['choices'][0]['delta'].get('content'):
                                    chunk = content['choices'][0]['delta']['content']
                                    print(chunk, end='', flush=True)
                                    file.write(chunk)
                                    file.flush()
                            except json.JSONDecodeError:
                                continue

                # 添加分隔符
                print(f"\n{'-'*30}\n")
                file.write(f"\n{'=-'*15}")
                file.flush()

            except requests.exceptions.ConnectionError:
                print(f"\n{chr(0x1f4f6)}  网络好像开小差了\n")

            except requests.RequestException as e:
                error_msg = f"请求错误: {str(e)}\n"
                print(error_msg)
                file.write(error_msg)
                file.flush()
            if head_question:
                break
