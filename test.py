# -*- coding: utf-8 -*-
from qg_botsdk import BOT, Model
from openai import OpenAI
import json
import re
import threading
class AI:
    def __init__(self):
        self.llm_check=cg[cg['llm_check']]
        self.llm_query=cg[cg['llm_query']]
        with open('check_prompt.txt', 'r',encoding='utf-8') as file:
            self.check_prompt=file.read()
        with open('query_prompt.txt', 'r',encoding='utf-8') as file:
            self.query_prompt=file.read()        
    def check(self, msg):
        bot.logger.info('开始检验')
        client=OpenAI(api_key=self.llm_check['api_key'], 
                      base_url=self.llm_check['base_url'])
        response = client.chat.completions.create(
            model=self.llm_check['model'],
            messages=[
                {"role": "system", "content": self.check_prompt},
                {"role": "user", "content": msg}
            ]
            #stream=True
        )

        reply = response.choices[0].message.content
        
        return reply
    def query(self, msg):
        client=OpenAI(api_key=self.llm_query['api_key'], 
                      base_url=self.llm_query['base_url'])
        response = client.chat.completions.create(
            model=self.llm_query['model'],
            messages=[
                {"role": "system", "content": self.query_prompt},
                {"role": "user", "content": msg}
            ],
            stream=True
        )
        collected_content = ""
        splitter = ResponseSplitter()
        for chunk in response:
            if chunk.choices:
                delta = chunk.choices[0].delta
                if delta.content:
                    for content in splitter.process(delta.content):
                        yield content
        # 处理最终残留内容
        final_content = splitter.flush()
        if final_content:
            yield final_content

class ResponseSplitter:
    def __init__(self):
        self.buffer = ''
        self.max_length = 150

    def process(self, new_content):
        self.buffer += new_content
        # 优先处理双换行
        dbl_newline = self.buffer.rfind('\n\n')
        if dbl_newline != -1:
            yield self.buffer[:dbl_newline]
            self.buffer = self.buffer[dbl_newline+2:]
            return
            
        # 处理单换行（仅在超过长度时）
        single_newline = self.buffer.rfind('\n')
        if single_newline > self.max_length:
            yield self.buffer[:single_newline]
            self.buffer = self.buffer[single_newline+1:]
            return
                    

        

    def flush(self):
        content = self.buffer.strip()
        self.buffer = ''
        return content if content else None
class Guild:
    def __init__(self,name):
        self.name = name
        bot.logger.info(f'机器人在{self.name}运行')
        self.id = ''
        
    def set(self,guild_id):
        if self.id != '':
            return True
        name=bot.api.get_guild_info(guild_id).data.name
        if (name != self.name):
            return False
        global bot_id; bot_id=bot.api.get_bot_info().data.id

        self.id = guild_id
        self.channels = bot.api.get_guild_channels(self.id).data
        self.roles = bot.api.get_guild_roles(self.id).data.roles

        self.admin_ids = [sf.id for sf in self.roles if '管理' in sf.name]
        self.channel_dict = {channel.name: channel.id for channel in self.channels}
        self.role_dict = {sf.name: sf.id for sf in self.roles}

        self.formal_id = self.role_dict['正式成员']
        self.smartboy_id = self.role_dict['违规发帖-请先看公告']

        #self.log_id = self.channel_dict['机器人运行日志']
        self.assessment_id = self.channel_dict['AI自动审核区']
        self.cooperation_id = self.channel_dict['互助区']
        self.answer_id = self.channel_dict['答疑区']
        self.notice_id = self.channel_dict['公告区']
        #self.instant_id = self.channel_dict['即时互助区']
        
        return True

class Messager:
    def __init__(self,data: Model.MESSAGE):
        self.data=data
        self.guild_id=data.guild_id
        self.channel_id=data.channel_id

        self.author_id=data.author.id
        self.name=data.author.username
        #bot.logger.info(data)
        if 'content' in data.__dict__:
            self.message=re.sub(r'<@!\d+>', '', data.content)
        else:
            self.message=''
        self.roles=data.member.roles

        self.head=f'<@{self.author_id}>\n'
        self.success = (f'你通过了考核，请点击<#{guild.cooperation_id}>前往互助区发帖，主动私信联系别人互助。')

    def set_formal(self,id):
        bot.api.create_role_member(id,guild.id,guild.formal_id)
    def reply(self, msg):
        self.data.reply(msg,message_reference_id=self.data.id)
    def is_at(self):
        if '@小灵bot' in self.message:
            return True
        if 'mentions' not in self.data.__dict__:
            return False
        return any(item.id == bot_id for item in self.data.mentions) 

    def is_admin(self):
        return set(guild.admin_ids)&set(self.roles)
    def genshin(self):
        if '/深渊使用率' in self.message or '/角色持有' in self.message:
            self.reply('玩原神玩的')
            return True
        return False
    def set(self):
        if self.message!=' 过':
            return
        if not self.is_admin():
            self.reply('你不是管理员，没有使用该指令的权限')
            return
        members=''
        for member in self.data.mentions:
            self.set_formal(member.id)
            members+=f'<@{member.id}>'
        self.reply(f'已将{members}设置为正式成员\n{self.success}')
        
    def ai_check(self):
        bot.logger.info(self.name+'发布委托表：\n'+self.message)
        checked=ai.check(self.message)
        bot.logger.info('\n'+checked)
        #bot.logger.info(checked)
        msg=json.loads(checked)
        reply = ''
        for value in msg.values():
            if value!='合法':
                reply += f'{value}\n'
        return reply[:-1]
    def check(self):
        if self.channel_id!=guild.assessment_id:
            return
        if not self.is_at():
            if len(self.message) > 150:
                #self.reply(('长度大于150，已调用自动审核功能\n'
                #            '请在委托表前 @小灵bot 以稳定调用自动审核功能'))
                pass
            else:
                return
        if len(self.message) < 50:
            self.reply('长度小于50，这不是一个正常的委托表')
            return
        #self.reply(('小灵bot已收到委托表,预计10s后会回复审核结果'
        #   '（没有这条消息说明你的消息违规，被tx拦截了，请截图后去人工区考核）'))
        reply=self.ai_check()
        if reply=='':
            self.set_formal(self.author_id)
            self.reply(self.success)
            bot.logger.info(f' {self.name} 通过考核')
        else:
            self.reply(reply)
    def query(self):
        if self.channel_id!=guild.answer_id:
            return 
        if not self.is_at():
            return 
        with query_lock:  # 在 ai_query 方法中加锁
            self.reply('小灵bot收到问题，正在编写回复')
            bot.logger.info('开始答疑')
            reply=''
            for chunk in ai.query(self.message):
                self.data.reply(chunk)
                reply+=chunk
            bot.logger.info(reply)


with open('../qq-bot.json', 'r', encoding='utf-8') as file:
    cg = json.load(file)
bot = BOT(**cg['bot'], is_private=True)
ai = AI()
guild = Guild(cg[cg['run_guild']])
query_lock = threading.Lock() # 创建一个锁

@bot.bind_msg()
def deliver(data: Model.MESSAGE):
    if not guild.set(data.guild_id):
        return 
    if data.guild_id!=guild.id:
        return
    msg=Messager(data)

    if msg.genshin():
        return
    msg.set()
    msg.check()
    msg.query()


if __name__ == "__main__":
    bot.start()