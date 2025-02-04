from openai import OpenAI, APIError, APIConnectionError
from urllib.parse import urlencode
from urllib.request import urlopen
import json, requests


def chatsimple(api_key, model_name, user_message, system_message, temp_message, base_url):
    '''普通模式的对话'''
    temp_message = eval(temp_message)
    ins = (
        [{"role": "system", "content": system_message}]
        + temp_message
        + [{"role": "user", "content": user_message}]
    )
    if True:
    #try:
        payload = {
        "model": model_name,
        "messages": ins,
        "max_tokens": 2000,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", base_url, json=payload, headers=headers)
    ans = json.loads(response.text)
    # print(response.text)
    # return str(response.text)
    try:
        think = ans["choices"][0]["message"]["reasoning_content"]
        with open("./data/think.txt", "w", encoding="utf-8") as file:
            file.write(think)
            print(think)
    except:
        pass
    with open("./data/tryagain.txt", "w", encoding="utf-8") as file:
        file.write(ans["choices"][0]["message"]["content"])
    return ans["choices"][0]["message"]["content"]
    '''
    except:
        print(f"机器人程序codeshop.DeepSeek出错了！2")
        return "机器人程序codeshop.DeepSeek出错了！2"
    '''

def chatlearning(api_key, model_name, user_message, system_message, temp_message, base_url):
    '''维权模式的对话'''
    client = OpenAI(api_key=api_key, base_url=base_url)
    # ins=[{"role": "system", "content": system_message}]
    temp_message = eval(temp_message)
    with open("./prompt/model_data1.txt", "r", encoding="utf-8") as f:
        model2 = f.read()
    model2 = [
        {
            "role": "user",
            "content": "请认真阅读以下内容，并在之后的回答中可以使用这些内容：" + model2,
        },
        {"role": "assistant", "content": "好的"},
    ]
    with open("./prompt/model_data2.txt", "r", encoding="utf-8") as f:
        model3 = f.read()
    model3 = [
        {
            "role": "user",
            "content": "请认真阅读以下内容，并在之后的回答中可以使用这些内容：" + model3,
        },
        {"role": "assistant", "content": "好的"},
    ]
    ins = (
        [{"role": "system", "content": system_message}]
        + model2
        + model3
        + temp_message
        + [{"role": "user", "content": user_message}]
    )
    # if True:
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=ins,
            temperature=0.7,
            max_tokens=8000,
            stream=False,
        )
        # 假设API响应结构符合OpenAI Playground的结构
        print(response.usage)
        return response.choices[0].message.content
    except json.JSONDecodeError as e:
        print(f"JSON解析失败，原始响应内容: {response.text}")
        return "服务响应异常，请稍后再试"
    except APIError as e:
        print(f"API错误: {e.status_code} {e.message}")
        return "服务暂时不可用，请稍后再试"
    except APIConnectionError as e:
        print(f"连接错误: {e}")
        return "网络连接异常，请检查网络设置"
    except Exception as e:
        print(f"未知错误: {str(e)}")
        return "服务出现意外错误"


def chatgame(api_key, model_name, user_message, system_message, base_url):
    '''游戏模式的对话'''
    client = OpenAI(api_key=api_key, base_url=base_url)
    ins = [{"role": "system", "content": system_message},{"role": "user", "content": user_message}]
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=ins,
            max_tokens=400,
            temperature=1.0,
            stream=False,
        )
        # 假设API响应结构符合OpenAI Playground的结构
        try:
            print(response.usage)
            return response.choices[0].message.content
        except:
            print(f"机器人程序codeshop.DeepSeek出错了！")
            return "机器人程序codeshop.DeepSeek出错了！"
    except:
        print(f"机器人程序codeshop.DeepSeek出错了！")
        return "机器人程序codeshop.DeepSeek出错了！"
    
def game_answer(api_key, model_name, user_message, system_message, temp_message, base_url):
    '''模拟教育部门回复游戏'''
    client = OpenAI(api_key=api_key, base_url=base_url)
    temp_message = []
    ins = (
        [{"role": "system", "content": system_message}]
        #+ temp_message
        + [{"role": "user", "content": user_message}]
    )
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=ins,
            max_tokens=400,
            temperature=1.0,
            stream=False,
        )
        # 假设API响应结构符合OpenAI Playground的结构
        try:
            print(response.usage)
            return response.choices[0].message.content
        except:
            print(f"机器人程序codeshop.DeepSeek出错了！")
            return "机器人程序codeshop.DeepSeek出错了！"
    except:
        print(f"机器人程序codeshop.DeepSeek出错了！")
        return "机器人程序codeshop.DeepSeek出错了！"
    
def before(text):
    with open("../config.json", "r", encoding="utf-8") as fp:
        json_data = json.load(fp)
        api_key = json_data["ai"]["before"]["key"]
        base_url = json_data["ai"]["before"]["base_url"]
        model = json_data["ai"]["before"]["model"]
        
    client = OpenAI(api_key=api_key, base_url=base_url)
    temp_message = []
    ins = [{"role": "user", "content": text}]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=ins,
            stream=False,
        )
        # 假设API响应结构符合OpenAI Playground的结构
        try:
            print(response.usage)
            return response.choices[0].message.content
        except:
            print(f"机器人程序codeshop.DeepSeek出错了！")
            return "机器人程序codeshop.DeepSeek出错了！"
    except:
        print(f"机器人程序codeshop.DeepSeek出错了！")
        return "机器人程序codeshop.DeepSeek出错了！"
    
