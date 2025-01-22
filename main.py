import os, json, botpy, time, random, requests, ast, urllib, datetime
from botpy import logging, logger, message, BotAPI
from botpy.message import DirectMessage, Message, GroupMessage
from botpy.ext.cog_yaml import read
from botpy.types.message import Reference
from botpy.types.announce import AnnouncesType
from botpy.forum import Thread
from botpy.types.forum import Post, Reply, AuditResult
from botpy.types.channel import ChannelSubType, ChannelType
from time import sleep
from codeshop.locknum import locknum
from codeshop.game import joingame, startgame
from codeshop.balance import balance
from codeshop.output import arcode, arname, tryagain, chat_body
from botpy.audio import Audio
import asyncio

logging.configure_logging()
_log = logging.get_logger()
keyanswer = {
    "test": "你在测试什么？",
    "你是哪个省的": "妈妈生的（误）",
}
json_data = {}
version = ""


class MyClient(botpy.Client):

    async def on_ready(self):  # 初次启动时
        global version
        with open("./data/version.txt", "r", encoding="utf-8") as file:
            version=file.read()
        start_txt = "\
-----------启动成功------------\n\
    小板凳频道管家，启动！\n\
    版本:"+version
        print(start_txt)
        try:
            await self.api.post_group_message(
                    group_openid="7C54D45EDDE030719971497006C0CA03",
                    msg_type=0,
                    content="机器人已启动",
                )
        except:
            logger.info("机器人已启动，主动消息发送失败")
            pass
        #asyncio.create_task(self.send_periodic_message())

    async def send_periodic_message(self):
        target_time = datetime.time(hour=19, minute=55)
        
        while True:
            now = datetime.datetime.now()
            target_datetime = datetime.datetime.combine(now.date(), target_time)
            
            if now > target_datetime:
                # 如果当前时间已经过了目标时间，则设置为第二天的目标时间
                target_datetime += datetime.timedelta(days=1)
            
            # 计算等待时间
            wait_seconds = (target_datetime - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            
            # 发送消息
            await self.api.post_group_message(
                group_openid="7C54D45EDDE030719971497006C0CA03",
                msg_type=0,
                content="这是一条定时发送的消息",
            )

    

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
            logger.info(
                f"新增了一个提示词。\n发送指令的ID：{openid}\n提示词内容：{word}"
            )
            return
        if "读取" in message.content:
            with open("./data/tryagain.txt", "r", encoding="utf-8") as f:
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
                a = tryagain(result)
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

            logger.info(
                f"修改了g_a_a提示词。\n发送指令的ID：{openid}\n提示词内容：{text}"
            )
        else:
            return

    async def on_audio_start(self, audio: Audio):
        await self.api.on_microphone(audio.channel_id)

    async def on_group_at_message_create(self, message: GroupMessage):  # 收到群消息时
        print(message)
        global json_data
        dataid = eval(str(message.author))
        open_id = dataid["member_openid"]  # 获取open_id
        result = False
        if "/绑定 " in message.content:  # 绑定用户名和open_id
            result = locknum(message.content, open_id)
        elif (
            "加入真心话" in message.content or "参加真心话" in message.content
        ):  # 加入游戏
            result = joingame(message.author)
        elif "开始真心话" in message.content:  # 开始游戏
            result = startgame(message.author)
        elif "查询余额" in message.content:
            chose = json_data["ai_chose"]
            key = json_data["ai"][chose]["key"]
            data = balance(key=key)
            result = "剩余的余额为：" + data + "元人民币。"
        elif "读取" in message.content:
            with open("./data/tryagain.txt", "r", encoding="utf-8") as f:
                result = f.read()
        elif "查地方 " in message.content:
            result = arcode(message.content)
        elif "查区号 " in message.content:
            result = arname(message.content)
        elif "清空上下文" in message.content:
            with open("./data/temp_message.txt", "w", encoding="utf-8") as file:
                file.write("[]")
            with open("./data/temp_message_game.json", "w", encoding="utf-8") as file:
                json.dump([], file)
            result = "已经清空了缓存的所有上下文数据！"
        elif "功能" in message.content:
            with open("./data/aboutme.txt", "r", encoding="utf-8") as file:
                result = file.read()
        else:
            data = False
            for k, r in keyanswer.items():
                if k in message.content:  # 如果在固定问答内容中，使用固定问答文本
                    result = r
                    data = True
            if data == False:
                chose = json_data['ai_chose']
                key = json_data["ai"][chose]["key"]
                model = json_data["ai"][chose]["model"]
                base_url = json_data["ai"][chose]["base_url"]
                result = chat_body(
                    message.content, key=key, model=model, base_url=base_url
                )  # 调用chat_body函数处理消息
        if result != False:
            try:
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    msg_id=message.id,
                    content=f"{result}",
                )
                result = True
            except:
                a = tryagain(result)
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
        else:
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                content=f"机器人的程序貌似出错了，请联系开发者处理！",
            )
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
    # intents = botpy.Intents(public_guild_messages=True, direct_message=True, guilds=True)
    with open("../config.json", "r", encoding="utf-8") as fp:
        json_data = json.load(fp)
        appid = json_data["bot"]["appid"]
        secret = json_data["bot"]["secret"]
    client = MyClient(intents=intents, timeout=8)
    client.run(appid=appid, secret=secret)
