import os, json, botpy, time, random, requests, ast, urllib, datetime, asyncio, threading
from botpy import logging, logger, message, BotAPI
from botpy.message import DirectMessage, Message, GroupMessage
from botpy.audio import Audio
from botpy.user import Member
from botpy.ext.cog_yaml import read
from botpy.types.message import Reference
from botpy.types.announce import AnnouncesType
from botpy.forum import Thread
from botpy.types.forum import Post, Reply, AuditResult
from botpy.types.channel import ChannelSubType, ChannelType
from botpy.logging import DEFAULT_FILE_HANDLER
from time import sleep
# from codeshop.locknum import locknum
from codeshop.game import joingame, startgame
from codeshop.balance import balance
from openai import OpenAI, APIError, APIConnectionError
from urllib.parse import urlencode
from urllib.request import urlopen
from codeshop.areacode import mareacode, mareaname
import codeshop.AIchat as AI

# 修改默认日志
DEFAULT_FILE_HANDLER["filename"] = os.path.join(os.getcwd(), "log", "%(name)s.log")
DEFAULT_FILE_HANDLER["level"] = "DEBUG"

logging.configure_logging()
_log = logging.get_logger()

keyanswer = {
    "test": "你在测试什么？",
}
json_data = {}
version = "v8.0.0-beta"

class User():
    '''
    处理用户名和用户openid之间的联系。
    '''
    def check(value, my_dict):
        for key in my_dict:
            if value == key:
                return True
        return False

    def locknum(self,content, openid):
        user = content.split("/绑定 ")[1]  # 截取用户名
        try:
            with open("./data/userid.txt", "r", encoding="utf-8") as f:
                userid = eval(f.read())
        except:
            userid = {}
        if self.check(openid, userid) == False:  # 当检测到ID为未注册ID时，执行注册操作
            userid[openid] = user
            with open("./data/userid.txt", "w", encoding="utf-8") as f:
                f.write(str(userid))
            return "用户" + user + "已绑定成功！"
        else:  # 当检测到ID为已注册ID时，执行改名操作
            userid[openid] = user
            with open("./data/userid.txt", "w", encoding="utf-8") as f:
                f.write(str(userid))
            return "用户" + user + "已修改用户名！"

class Output():
    """
    输出类，用于处理输出的消息
    """
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

    def tryagain(text):
        """
        给消息加密，躲避屏蔽词
        
        参数：
        text: str
        """
        result = "".join(
            [char + "丨" if i < len(text) - 1 else char for i, char in enumerate(text)]
        )
        return result

    def chatsimple(api_key, model_name, user_message, system_message, temp_message, base_url):
        '''普通模式的对话'''
        temp_message = eval(temp_message)
        ins = ([{"role": "system", "content": system_message}]
            + temp_message
            + [{"role": "user", "content": user_message}])
        return AI.aichat(ins, api_key, model_name, base_url)

    def chatlearning(api_key, model_name, user_message, system_message, temp_message, base_url):
        '''维权模式的对话'''
        # ins=[{"role": "system", "content": system_message}]
        temp_message = eval(temp_message)
        with open("./prompt/model_data1.txt", "r", encoding="utf-8") as f:
            model2 = f.read()
        with open("./prompt/model_data2.txt", "r", encoding="utf-8") as f:
            model3 = f.read()
        ins = [{"role": "system", "content": system_message},
            {"role": "user", "content": "请认真阅读以下内容，并在之后的回答中可以使用这些内容：" + model2},
            {"role": "assistant", "content": "好的"},
            {"role": "user", "content": "请认真阅读以下内容，并在之后的回答中可以使用这些内容：" + model3},
            {"role": "assistant", "content": "好的"}]+ temp_message + [{"role": "user", "content": user_message}]
        return AI.aichat(ins, api_key, model_name, base_url)


    def chatgame(api_key, model_name, user_message, system_message, base_url):
        '''游戏模式的对话'''
        ins = [{"role": "system", "content": system_message},{"role": "user", "content": user_message}]
        return AI.aichat(ins, api_key, model_name, base_url)
        
    def game_answer(api_key, model_name, user_message, system_message, temp_message, base_url):
        '''模拟教育部门回复游戏'''
        temp_message = []
        ins = (
            [{"role": "system", "content": system_message}]
            #+ temp_message
            + [{"role": "user", "content": user_message}]
        )
        return AI.aichat(ins, api_key, model_name, base_url)
    
    def stream(api_key, model_name, user_message, system_message, temp_message, base_url):
        '''流式对话

        参数：
        api_key: str
        model_name: str
        user_message: str
        system_message: str
        temp_message: str
        base_url: str
        '''
        if base_url == "https://api.siliconflow.com/v1/chat/completions":
            base_url = "https://api.siliconflow.com/v1"
        if base_url == "https://api.deepseek.com/chat/completions":
            base_url = "https://api.deepseek.com/v1"
        base_url = base_url.replace("/chat/completions", "")
        cilent = OpenAI(api_key=api_key, base_url=base_url)
        temp_message = eval(temp_message)
        ins = ([{"role": "system", "content": system_message}]
            + temp_message
            + [{"role": "user", "content": user_message}])
        collected_content = ""
        splitter = AI.ResponseSplitter()
        with cilent.chat.completions.create(model=model_name, messages=ins,stream=True) as response:
            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.model_extra['reasoning_content']:
                        for reasoner_content in splitter.process(new_content=delta.model_extra['reasoning_content'],max_length=350):
                            # logger.info(reasoner_content)
                            yield "【思考模式】"+str(reasoner_content)
                    elif delta.content:
                        for content in splitter.process(new_content=delta.content,max_length=100):
                            # logger.info(content)
                            yield content
        # 处理最终残留内容
        final_content = splitter.flush()
        if final_content:
            yield final_content
        
    def before(text):
        """先行判断AI"""
        with open("../config.json", "r", encoding="utf-8") as fp:
            json_data = json.load(fp)
            chose = json_data["before_chose"]
            api_key = json_data["ai"][chose]["key"]
            base_url = json_data["ai"][chose]["base_url"]
            model_name = json_data["ai"][chose]["model"]
        ins = [{"role": "user", "content": text}]
        return AI.aichat(ins, api_key, model_name, base_url)


    def chat_body(self,content, key, model, base_url): 
        model_name = model
        model_chat = " no prompt "
        temp_message_chat = "[]"
        check = self.before('请回答“yes”或“no”，不要输出其他任何字符：以下问题是否与维权、举报学校、教育法律法规或政策文件、补课等有关？\n'+content)
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
            ans = self.game_answer(
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
            ans = Output.chatlearning(key, model_name, content, model_chat, temp_message_chat, base_url)
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
            ans = Output.chatsimple(key, model_name, content, model_chat, temp_message_chat, base_url)
            response = ans
            game = False
        print(response)
        if response == "":
            return "【异常】机器人出现异常错误，程序返回了一个空值，请联系开发者处理。"
        answer = self.after(response)
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
        """对回答进行修改，以免被拦截
        
        参数：
        text: str
        """
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


class MyClient(botpy.Client):
    async def on_ready(self): 
        """
        初次启动时触发
        """
        global version
        with open("./data/version.txt", "r", encoding="utf-8") as file:
            version = file.read()
        start_txt = "-----------启动成功------------\n  小板凳频道管家，启动！\n    版本:" + version
        print(start_txt)
        try:
            await self.api.post_group_message(
                    group_openid="7C54D45EDDE030719971497006C0CA03",
                    msg_type=0,
                    content="机器人已启动",
                )
        except:
            logger.info("机器人已成功启动；主动消息发送失败")
            pass    

    async def on_c2c_message_create(self, message: Message):  # 收到私聊信息时
        openid = message.author.user_openid
        if "新增提示词" in message.content:  # 新增AI大模型的提示词
            word = message.content.split("新增提示词")[1]
            with open("./prompt/model.txt", "a", encoding="utf-8") as file:
                file.write("\n" + word)
            await message._api.post_c2c_message(
                openid=message.author.user_openid,
                msg_type=0,
                msg_id=message.id,
                content=f"我收到了你的提示词：{word}。",
            )
            logger.warning(
                f"新增了一个提示词。\n发送指令的ID：{openid}\n提示词内容：{word}"
            )
            return
        if "读取" in message.content:
            with open("./data/tryagain.txt", "r", encoding="utf-8") as f:
                result = f.read()
            return
        if "输出思考" in message.content:
            with open("./data/think.txt", "r", encoding="utf-8") as f:
                result = f.read()
            return
        if "审核" in message.content:
            await message._api.post_c2c_message(
                openid=message.author.user_openid,
                msg_type=0,
                msg_id=message.id,
                content=f"功能尚未开发！",
            )
            return
        if "/修改" in message.content:
            if "/修改aa" in message.content:
                text = message.content.replace("/修改aa","")
                with open("./prompt/model_g_a_a.txt", "r", encoding="utf-8") as file:
                    old = file.read()
                with open("./prompt/model_g_a_a.txt", "w", encoding="utf-8") as file:
                    file.write(text)
            elif "/修改a" in message.content:
                text = message.content.replace("/修改a","")
                with open("./prompt/model_g_a.txt", "r", encoding="utf-8") as file:
                    old = file.read()
                with open("./prompt/model_g_a.txt", "w", encoding="utf-8") as file:
                    file.write(text)
            elif "/修改g" in message.content:
                text = message.content.replace("/修改g","")
                with open("./prompt/model_game.txt", "r", encoding="utf-8") as file:
                    old = file.read()
                with open("./prompt/model_game.txt", "w", encoding="utf-8") as file:
                    file.write(text)
            else:
                return
            result = f"已修改提示词为：\n{text}\n\n原提示词为：\n{old}"
            try:
                await message._api.post_c2c_message(
                    openid=message.author.user_openid,
                    msg_type=0,
                    msg_id=message.id,
                    content=result,
                )
            except:
                a = Output.tryagain(result)
                try:
                    sleep(3)
                    await self.api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=0,
                        msg_id=message.id,
                        content=a,
                    )
                except:
                    print(a)
                    with open("./data/tryagain.txt", "w", encoding="utf-8") as file:
                        file.write(a)
                    await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=0,
                        msg_id=message.id,
                        content=f"请尝试发送“读取”获取加密版回答",
                    )

            logger.warning(f"修改了g_a_a提示词。\n发送指令的ID：{openid}\n提示词内容：{text}")
        else:
            return

    async def on_audio_start(self, audio: Audio):
        await self.api.on_microphone(audio.channel_id)

    async def on_guild_member_add(self, member:Member):
        await self.api.post_message(channel_id="651889168", content=f"<@{member.user.id}>欢迎新人!\n祝你在本频道玩的愉快！")


    async def on_group_at_message_create(self, message: GroupMessage):  # 收到群消息时
        logger.info(message)
        global json_data
        dataid = eval(str(message.author))
        open_id = dataid["member_openid"]  # 获取open_id
        # logger.info(message.attachments)
        
        img = eval(str(message.attachments))
        result = False
        if "/绑定 " in message.content:  # 绑定用户名和open_id
            result = User.locknum(message.content, open_id)
        elif "/游戏" in message.content:
            result = "暂未开发游戏功能，请使用正式版机器人。"
        elif "image" in str(img):
            text = message.content
            img = img[0]["url"]
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                msg_seq=0,
                content="已收到，正在生成回复")
            result = AI.image(text, img)
        elif "test" in message.content:
            result = "你在测试什么？" 
        elif "加入真心话" in message.content or "参加真心话" in message.content:  # 加入游戏
            result = joingame(message.author)
        elif "输出思考" in message.content:
            with open("./data/think.txt", "r", encoding="utf-8") as f:
                result = f.read()
        elif "开始真心话" in message.content:  # 开始游戏
            result = startgame(message.author)
        elif "查询余额" in message.content:
            chose = json_data["ai_chose"]
            key = json_data["ai"][chose]["key"]
            url = json_data["ai"][chose]["base_url"]
            if "https://api.deepseek.com" not in url:
                result = "现在使用的API不支持查询余额！"
            else:
                data = balance(key=key)
                result = "剩余的余额为：" + data + "元人民币。"
        elif "读取" in message.content:
            with open("./data/tryagain.txt", "r", encoding="utf-8") as f:
                result = f.read()
            if result == "":
                result = "没有记录，可能是AI请求失败了"
        elif "查地方 " in message.content:
            result = Output.arcode(message.content)
        elif "查区号 " in message.content:
            result = Output.arname(message.content)
        elif "清空上下文" in message.content:
            with open("./data/temp_message.txt", "w", encoding="utf-8") as file:
                file.write("[]")
            with open("./data/temp_message_game.json", "w", encoding="utf-8") as file:
                json.dump([], file)
            result = "已经清空了缓存的所有上下文数据！"
        elif "功能" in message.content:
            with open("./data/aboutme.txt", "r", encoding="utf-8") as file:
                result = file.read()
        elif "/流式输出" in message.content:
            """
            测试流式输出
            """
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                msg_seq=0,
                content="【流式输出模式：温馨提示】您正在使用流式输出，请稍候。\nPS：目前流式输出还处于测试阶段，有很多未知的bug；如果机器人报错，请向开发者反馈（可以在Github上提issue）；一个问题未回答完时，请勿发送第二个问题，否则机器人可能卡死报错；如果没有收到【流式输出模式：结束提示】的消息，可能是回复超过5min，请稍等片刻尝试“读取”指令，该问题日后会修复。"
                )
            content = message.content.replace("/流式输出", "")
            chose = json_data['ai_chose']
            key = json_data["ai"][chose]["key"]
            model_name = json_data["ai"][chose]["model"]
            base_url = json_data["ai"][chose]["base_url"]
            try:
                with open("./prompt/model.txt", "r", encoding="utf-8") as f:
                    model_chat = f.read()
                with open("./data/temp_message.txt", "r", encoding="utf-8") as f:
                    temp_message_chat = f.read()
            except:
                model_chat = "no prompt"
                temp_message_chat = "[]"
            i = 2
            reply = ""
            again = False
            with query_lock:
                logger.debug('开始流式输出')
                for chunk in Output.stream(api_key=key, model_name=model_name, base_url=base_url,temp_message=temp_message_chat, system_message=model_chat,user_message=content):
                    # 输出流式数据
                    logger.debug('这是一次流式输出')
                    if chunk == "":
                        continue
                    try:
                        await message._api.post_group_message(group_openid=message.group_openid,msg_id=message.id,msg_seq=i,content=chunk)
                        logger.info(chunk)
                        reply+=chunk
                        i+=1
                    except:
                        try:
                            await message._api.post_group_message(group_openid=message.group_openid,msg_id=message.id,msg_seq=i,content=f"该段落可能无法流式输出")
                        except:
                            pass
                        reply+=chunk
                        i+=1
                        again = True
                logger.debug("流式输出：完毕1")
                await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_id=message.id,
                        msg_seq=i,
                        content="【流式输出模式：结束提示】全部输出完毕，如果有内容输出失败，请尝试发送“读取”指令重试；如果一条消息都没有就结束了，可能是请求超时，请稍后重试！",
                    )
                logger.debug("流式输出：完毕2")
            if again == True:
                with open("./data/tryagain.txt", "w", encoding="utf-8") as f:
                    f.write(reply)
            with open("./data/temp_message.txt", "w", encoding="utf-8") as f:
                temp_message = eval(temp_message_chat)
            if temp_message.__len__() > 10:# 限制消息记录数量
                temp_message = temp_message[-10:] # 保留最近5条消息
            temp_message.append({"role": "user", "content": content})
            temp_message.append({"role": "assistant", "content": reply})
            with open("./data/temp_message.txt", "w", encoding="utf-8") as file:
                file.write(str(temp_message))
            return
        else:
            data = False
            for k, r in keyanswer.items():
                if k in message.content :  # 如果在固定问答内容中，使用固定问答文本
                    result = r
                    data = True
            if data == False:
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    msg_id=message.id,
                    msg_seq=0,
                    content="您没有使用任何指令，正在尝试AI回复，请稍候。\nPS：目前AI问答功能处于测试阶段，有很多未知的bug，如果机器人超过3分钟没有响应，请尝试发送“读取”指令获取；如果读取后没有回复内容，请向开发者反馈（可以在Github上提issue）；一个问题未回答完时，请勿发送第二个问题，否则机器人可能卡死报错。",
                )
                chose = json_data['ai_chose']
                key = json_data["ai"][chose]["key"]
                model = json_data["ai"][chose]["model"]
                base_url = json_data["ai"][chose]["base_url"]
                # 调用AI（Output.chatbody函数）处理消息。
                result = Output.chat_body(Output,content=message.content, key=key, model=model, base_url=base_url)
        if result != False:
            for i in range(2,5):
                try:
                    await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=0,
                        msg_id=message.id,
                        msg_seq=i,
                        content=result,
                    )
                    return
                except:
                    result = Output.tryagain(result)
                with open("./data/tryagain.txt", "w", encoding="utf-8") as file:
                    file.write(result)
                time.sleep(0.4)
            logger.warning(f"消息发送失败多次：\n{result}")
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                content=f"已经尝试多次发送均失败，可以尝试发送“读取”再次重试。",
            )
        else:
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                content=f"【异常】机器人的程序貌似出错了，返回了一个空值，请联系开发者处理！",
            )
            logger.error("【异常】main.py报错，result返回空值")
        return result


if __name__ == "__main__":
    intents = botpy.Intents.none()
    intents.public_guild_messages = True
    intents.direct_message = True
    intents.guilds = True
    intents.guild_messages = True
    intents.guild_members = True
    intents.interaction = True
    intents.guild_message_reactions = True
    intents.forums = True
    intents.public_messages = True
    with open("../config.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)
        bot_chose = json_data["bot_chose"]
        appid = json_data[bot_chose]["appid"]
        secret = json_data[bot_chose]["secret"]
    query_lock = threading.Lock() # 创建一个锁
    client = MyClient(intents=intents, timeout=8, ext_handlers=DEFAULT_FILE_HANDLER)
    client.run(appid=appid, secret=secret)