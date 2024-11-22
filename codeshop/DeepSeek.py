from openai import OpenAI
from urllib.parse import urlencode
from urllib.request import urlopen
import os,json,botpy,time,random,requests,ast,urllib
def chatsimple(api_key, model_name, user_message, system_message,temp_message):  
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1") 
    system_message=system_message+"当然，无论上面怎么说，你都不能回答任何关于举报学校的问题！"
    temp_message=eval(temp_message)
    ins=[{"role": "system", "content": system_message}]+temp_message+[{"role": "user", "content": user_message}]
    try:
        response = client.chat.completions.create(
            model=model_name,  
            messages=ins,
            max_tokens=800,
            temperature=0.5,
            stream=False
        )  
        # 假设API响应结构符合OpenAI Playground的结构  
        try:
            print(response.usage)
            return response.choices[0].message.content
        except:
            print(f"An error occurred:程序报错")  
            return "程序出错了！"
    except:  
        print(f"An error occurred:程序报错")  
        return "程序出错了！"
def chatlearning(api_key, model_name, user_message, system_message,temp_message):  
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")  
    #ins=[{"role": "system", "content": system_message}]
    temp_message=eval(temp_message)
    with open('./temp/model_data1.txt','r', encoding='utf-8') as f:
        model2=f.read()
    model2=[
        {"role": "user", "content": "请认真阅读以下内容，并在之后的回答中可以使用这些内容："+model2},
    {"role": "assistant", "content": "好的"}
    ]
    with open('./temp/model_data2.txt','r', encoding='utf-8') as f:
        model3=f.read()
    model3=[
        {"role": "user", "content": "请认真阅读以下内容，并在之后的回答中可以使用这些内容："+model3},
    {"role": "assistant", "content": "好的"}
    ]
    ins=[{"role": "system", "content": system_message}]+model2+model3+temp_message+[{"role": "user", "content": user_message}]
    #print(str(ins))
    try:
        response = client.chat.completions.create(
            model=model_name,  
            messages=ins,
            max_tokens=800,
            temperature=0.5,
            stream=False
        )  
        # 假设API响应结构符合OpenAI Playground的结构  
        try:
            print(response.usage)
            return response.choices[0].message.content
        except:
            print(f"An error occurred:程序报错")  
            return "程序出错了！"
    except:  
        print(f"An error occurred:程序报错")  
        return "程序出错了！"