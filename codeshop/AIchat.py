from openai import OpenAI, APIError, APIConnectionError
from urllib.parse import urlencode
from urllib.request import urlopen
import json, requests

class ResponseSplitter:
    """
    该类用于处理文本内容，根据特定的规则对文本进行分割和缓存管理。
    本模块代码来自@幽灵。
    """
    def __init__(self):
        """
        初始化Test类的实例。
        """
        self.buffer = ''

    def process(self, new_content, max_length:int=300):
        """
        处理新的文本内容。
        
        参数:
        - new_content: 新的文本内容，将被添加到缓存中。
        
        该方法根据文本中的换行符和最大长度限制，对文本内容进行分割和缓存更新。
        """
        self.buffer += new_content
        # 优先处理双换行
        dbl_newline = self.buffer.rfind('\n\n')
        if dbl_newline != -1:
            yield self.buffer[:dbl_newline]
            self.buffer = self.buffer[dbl_newline+2:]
            return
        # 处理单换行（仅在超过长度时）
        single_newline = self.buffer.rfind('\n')
        if single_newline > max_length:
            yield self.buffer[:single_newline]
            self.buffer = self.buffer[single_newline+1:]
            return

    def flush(self):
        """
        清空缓存并返回剩余的文本内容。
        
        返回:
        - 如果缓存中有内容，则返回缓存内容；否则返回None。
        """
        content = self.buffer.strip()
        self.buffer = ''
        return content if content else None
    

def image(text, img):
    model_name = "Qwen/Qwen2-VL-72B-Instruct"
    base_url = "https://api.siliconflow.com/v1/chat/completions"
    api_key = "sk-croaumeyumtijxdbwwxbizeopqzjdyvrqzmnfdfhfjrjycfi"
    ins = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "image_url":img,"text":text},
        #{"role": "assistant", "content": "收到图片了，你有什么问题吗？"},
        #{"role": "user", "text":text,"type":"text"}
    ]
    payload = {
        "model": model_name,
        "messages": ins,
        "max_tokens": 2000,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.request("POST", base_url, json=payload, headers=headers)
        #if response.text["error_msg"]:
        #     return response.text["error_msg"]
        print(response.text)
        ans = json.loads(response.text)
        #print(response.text)
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
    except json.JSONDecodeError as e:
        return f"【异常】JSON解析失败，原始响应内容: {response.text}"
    except APIError as e:
        return f"【异常】API错误: {e.status_code} {e.message}"
    except APIConnectionError as e:
        return f"【异常】连接错误: {e}"
    except Exception as e:
        return f"【异常】未知错误: {str(e)}"

def aistream(ins, api_key, model_name, base_url):
    payload = {
        "model": model_name,
        "messages": ins,
        "max_tokens": 2000,
        "stream":True
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.request("POST", base_url, json=payload, headers=headers, stream=True)
        collected_content = ""
        splitter = ResponseSplitter()
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                for content in splitter.process(chunk):
                    yield content
        # 处理最终残留内容
        final_content = splitter.flush()
        if final_content:
            yield final_content
        try:
            ans = json.load(response.text)
            think = ans["choices"][0]["message"]["reasoning_content"]
            with open("./data/think.txt", "w", encoding="utf-8") as file:
                file.write(think)
                print(think)
        except:
            pass
    except json.JSONDecodeError as e:
        return f"【异常】JSON解析失败，原始响应内容: {response.text}"
    except APIError as e:
        return f"【异常】API错误: {e.status_code} {e.message}"
    except APIConnectionError as e:
        return f"【异常】连接错误: {e}"
    except Exception as e:
        return f"【异常】未知错误: {str(e)}"
    
def aichat(ins, api_key, model_name, base_url):
    payload = {
        "model": model_name,
        "messages": ins,
        "max_tokens": 2000,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.request("POST", base_url, json=payload, headers=headers)
        #if response.text["error_msg"]:
        #     return response.text["error_msg"]
        ans = json.loads(response.text)
        #print(response.text)
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
    except json.JSONDecodeError as e:
        return f"【异常】JSON解析失败，原始响应内容: {response.text}"
    except APIError as e:
        return f"【异常】API错误: {e.status_code} {e.message}"
    except APIConnectionError as e:
        return f"【异常】连接错误: {e}"
    except Exception as e:
        return f"【异常】未知错误: {str(e)}"


