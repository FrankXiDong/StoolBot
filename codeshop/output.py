from time import sleep
from openai import OpenAI, APIError, APIConnectionError
from urllib.parse import urlencode
from urllib.request import urlopen
import json, random
from codeshop.areacode import mareacode, mareaname
import codeshop.AIchat as AI


def arcode(areanum):
    area = areanum.split("查地方 ")[1]
    ans = str(mareacode(area))
    ans = ans.replace("[", "").replace("]", "")
    if "1000060" in ans:
        return "没有查到该区号，请确认区号是否正确，指令有无多余标点字符和空格。"
    else:
        return "区号" + area + "的对应地为: " + ans


def arname(areaname):
    area = areaname.split("查区号 ")[1]
    if "三沙" in area:
        ans = "0898"
    else:
        ans = str(mareaname(area))
        ans = ans.replace("[", "").replace("]", "")
    if "1000060" in ans:
        return "没有查到该地方，请确认地方是否正确，是否为地级行政区划正式名称，指令有无多余标点字符和空格。"
    else:
        return "地方 " + area + " 的区号为: " + ans


def check(value, my_dict):
    for key in my_dict:
        if value == key:
            return True
    return False


def tryagain(text):  # 给消息加密，躲避屏蔽词
    result = "".join(
        [char + "丨" if i < len(text) - 1 else char for i, char in enumerate(text)]
    )
    return result


def chatsimple(api_key, model_name, user_message, system_message, temp_message, base_url):
    '''普通模式的对话'''
    temp_message = eval(temp_message)
    ins = (
        [{"role": "system", "content": system_message}]
        + temp_message
        + [{"role": "user", "content": user_message}]
    )
    return AI.aichat(ins, api_key, model_name, base_url)

def chatlearning(api_key, model_name, user_message, system_message, temp_message, base_url):
    '''维权模式的对话'''
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
    return AI.aichat(ins, api_key, model_name, base_url)


def chatgame(api_key, model_name, user_message, system_message, base_url):
    '''游戏模式的对话'''
    client = OpenAI(api_key=api_key, base_url=base_url)
    ins = [{"role": "system", "content": system_message},{"role": "user", "content": user_message}]
    return AI.aichat(ins, api_key, model_name, base_url)
    
def game_answer(api_key, model_name, user_message, system_message, temp_message, base_url):
    '''模拟教育部门回复游戏'''
    client = OpenAI(api_key=api_key, base_url=base_url)
    temp_message = []
    ins = (
        [{"role": "system", "content": system_message}]
        #+ temp_message
        + [{"role": "user", "content": user_message}]
    )
    return AI.aichat(ins, api_key, model_name, base_url)
    
def before(text):
    with open("../config.json", "r", encoding="utf-8") as fp:
        json_data = json.load(fp)
        api_key = json_data["ai"]["before"]["key"]
        base_url = json_data["ai"]["before"]["base_url"]
        model_name = json_data["ai"]["before"]["model"]
        
    client = OpenAI(api_key=api_key, base_url=base_url)
    temp_message = []
    ins = [{"role": "user", "content": text}]
    return AI.aichat(ins, api_key, model_name, base_url)


def chat_body(content, key, model, base_url): 
    model_name = model
    model_chat = " no prompt "
    temp_message_chat = "[]"
    check = before('请回答“yes”或“no”，不要输出其他任何字符：以下问题是否与维权、举报学校、教育法律法规或政策文件、补课等有关？\n'+content)
    print(check)
    # 分情况请求不同的API
    if "/游戏" in content:
        return "开发中（测试版）机器人的游戏功能暂时无法使用，敬请谅解！"
        with open("./prompt/newgame_level.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        try:
            with open("./data/ai_game.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []
        content = content.replace("/游戏", "")
        ans = chatgame(key, model_name, content, prompt, base_url)
        # 定义选项及其对应概率（权重）
        options = ['a', 'b', 'c', 'd']
        weights = [5, 30, 50, 15]
        # 根据权重随机选择一个结果
        result = random.choices(options, weights=weights, k=1)[0]
        # result = 'd'
        if result == 'a':
            with open("./prompt/newgame_a.txt", "r", encoding="utf-8") as f:
                prompt = f.read()
        elif result == 'b':
            with open("./prompt/newgame_b.txt", "r", encoding="utf-8") as f:
                prompt = f.read()
        elif result == 'c':
            with open("./prompt/newgame_c.txt", "r", encoding="utf-8") as f:
                prompt = f.read()
        elif result == 'd':
            with open("./prompt/newgame_d.txt", "r", encoding="utf-8") as f:
                prompt = f.read()
        else:
            return "二轮概率选择器错误"
        ans = chatgame(key, model_name, content, prompt, temp_message_game, base_url)
        level = result.upper()
        response = f"\n【游戏模式2.0】【经评估，该结果为 {level} 级情况】 \n{ans}"
        game = True
        if temp_message_game.__len__() > 10:# 限制消息记录数量
            temp_message_game = temp_message_game[-10:] # 保留最近5条消息
    elif "/回复模拟" in content:
        access = random.random() < 0.4
        if access == True:
            with open("./prompt/model_g_a_a.txt", "r", encoding="utf-8") as f:
                model_g_a = f.read()
        else:
            with open("./prompt/model_g_a.txt", "r", encoding="utf-8") as f:
                model_g_a = f.read()
        content = content.replace("/回复模拟", "")
        ans = game_answer(
            key, model_name, content, model_g_a, temp_message_chat, base_url
        )
        response = f"【模拟教育局回复游戏（是否成功：{access}）】\n{ans}"
        game = 0
    elif "维权" in content or 'yes' in check:
        try:
            with open("./prompt/model.txt", "r", encoding="utf-8") as f:
                model_chat = f.read()
            with open("./data/temp_message.txt", "r", encoding="utf-8") as f:
                temp_message_chat = f.read()
        except:
            pass
        ans = chatlearning(key, model_name, content, model_chat, temp_message_chat, base_url)
        response = ans
        game = False
    else:
        try:
            with open("./prompt/model.txt", "r", encoding="utf-8") as f:
                model_chat = f.read()
            with open("./data/temp_message.txt", "r", encoding="utf-8") as f:
                temp_message_chat = f.read()
        except:
            pass
        ans = chatsimple(key, model_name, content, model_chat, temp_message_chat, base_url)
        response = ans
        game = False
    print(response)
    if response == "":
        return "【异常】机器人出现异常错误，程序返回了一个空值，请联系开发者处理。"
    answer = after(response)
    temp_message = eval(temp_message_chat)
    if temp_message.__len__() > 10:# 限制消息记录数量
        temp_message = temp_message[-10:] # 保留最近5条消息
    
    if game == False:
        temp_message.append({"role": "user", "content": content})
        temp_message.append({"role": "assistant", "content": ans})
        with open("./data/temp_message.txt", "w", encoding="utf-8") as file:
            file.write(str(temp_message))
        text = "\n" + answer + "\n\nPS：以上内容为AI自动生成，仅供参考。"
    elif game == 0:
        text = "\n" + answer + "\n\nPS：以上内容为AI自动生成，仅供娱乐，无实际意义; 本游戏不支持存储上下文数据"
    else:
        temp_message_game = []# 临时
        temp_message_game.append({"role": "user", "content": content})
        temp_message_game.append({"role": "assistant", "content": ans})
        with open("./data/temp_message_game.json", "w", encoding="utf-8") as file:
            json.dump(temp_message_game, file, ensure_ascii=False, indent=4)
        text = "\n" + answer + "\n\nPS：以上内容为AI自动生成，仅供娱乐，无实际意义。"
    with open("./data/tryagain.txt", "w", encoding="utf-8") as file:
        file.write(text)
    return text


def after(text):
    # 对回答进行修改，以免被拦截
    answer = text
    if ".com" in answer:
        answer = answer.replace(".", "点")
    if ".cn" in answer:
        answer = answer.replace(".", "点")
    answer = answer.replace("中国共产党", "CPC")
    answer = answer.replace("中共", "CPC")
    answer = answer.replace("共产党", "CPC")
    answer = answer.replace("习近平总书记","Mr.Xi")
    answer = answer.replace("习近平主席","Mr.Xi")
    answer = answer.replace("习近平", "Mr.Xi")
    answer = answer.replace("毛泽东","Mr.Mao")
    answer = answer.replace("总书记","ZongShuJi")
    answer = answer.replace("中华人民共和国主席","President of China")
    answer = answer.replace("中央军委主席","Chairman of the Central Military Commission")
    answer = answer.replace("中央军事委员会主席","Chairman of the Central Military Commission")
    answer = answer.replace("中央委员会","Central Committee")
    answer = answer.replace("市委书记","市Wei书Ji")
    return answer
