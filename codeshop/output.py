from time import sleep
import json
from codeshop.areacode import mareacode, mareaname
from codeshop.DeepSeek import chatlearning, chatsimple, chatgame


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
        [char + "丿" if i < len(text) - 1 else char for i, char in enumerate(text)]
    )
    return result


def chat_body(content, key): 
    model_name = "deepseek-chat"
    with open("./temp/model.txt", "r", encoding="utf-8") as f:
        model_chat = f.read()
    with open("./temp/temp_message.txt", "r", encoding="utf-8") as f:
        temp_message_chat = f.read()
    with open("./temp/model_game.txt", "r", encoding="utf-8") as f:
        model_game = f.read()
    with open("./temp/temp_message_game.json", "r", encoding="utf-8") as f:
        temp_message_game = json.load(f)
    # 分情况请求不同的API
    if "/游戏" in content:
        content = content.replace("/游戏", "")
        ans = chatgame(
            key, model_name, content, model_game, temp_message_game
        )
        response = "【游戏模式】\n" + ans
        game = True
    elif "维权" in content:
        ans = chatlearning(key, model_name, content, model_chat, temp_message_chat)
        response = ans
        game = False
    else:
        ans = chatsimple(key, model_name, content, model_chat, temp_message_chat)
        response = ans
        game = False
    print(response)
    if "机器人程序codeshop.DeepSeek出错" in response:
        ins = False
        return 0
    answer = after(response)
    temp_message = eval(temp_message_chat)
    if temp_message.__len__() > 10:# 限制消息记录数量
        temp_message = temp_message[-10:] # 保留最近5条消息
    if game == False:
        temp_message.append({"role": "user", "content": content})
        temp_message.append({"role": "assistant", "content": ans})
        with open("./temp/temp_message.txt", "w", encoding="utf-8") as file:
            file.write(str(temp_message))
        text = "\n" + answer + "\n\nPS：以上内容为AI自动生成，仅供参考。"
    else:
        temp_message_game.append({"role": "user", "content": content})
        temp_message_game.append({"role": "assistant", "content": ans})
        with open("./temp/temp_message_game.json", "w", encoding="utf-8") as file:
            json.dump(temp_message_game, file, ensure_ascii=False, indent=4)
        text = "\n" + answer + "\n\nPS：以上内容为AI自动生成，仅供娱乐，无实际意义。"
    return text


def after(text):
    # 对回答进行修改，以免被拦截
    answer = text
    if ".com" in answer:
        answer = answer.replace(".", "点")
    if ".cn" in answer:
        answer = answer.replace(".", "点")
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
    answer = answer.replace("市委书记","CPC市丿委员会，书丿记")
    return answer
