#这个class放在另一个文件内供调用
class ReportGame:
    def __init__(self,possibility_data):
        self.possibility_data=possibility_data
        self.finalwin=0
        #possibility_data是一个字典，存储各种合理的举报方式的成功率(这里的成功率指的是被记录的成功率，不是最终成功率)，比如{"使用12345"：0.2}一定要包含其他举报方式这一个key
    def selectcase(self,user_input):
        #user_input是游戏输入，用ai来判断属于哪种举报方式
        import random
        #先判断输入是否合法
        if len(user_input)<=5:
            return "请输入正常游戏内容"
        #让ai判断是否属于合理举报方式，不合理则return 0，问的部分我不会写你来写（）
        prompt="你认为下列举报方式合不合理，你只需要回答 合理 或者 不合理，不要有额外词汇"+user_input
        #下面构造prompt#
        prompt="你觉得这段话属于哪种举报方式,你只需要回答是下面的哪种，不要有额外词汇"
        b=list(self.possibility_data.keys())
        for i in b:
            prompt=prompt+"\n"+i
        ai_answer = "" #用prompt问ai得到ai_answer
        return self.possibility_data[ai_answer] if ai_answer!="其他举报方式" else random.random(0,0.3)
    def make_output(self,possibility,minadd=0.05,maxadd=0.2):
        #已经知道这种举报方式的成功率了，这个函数来构造回复,minadd和maxadd是决定最终成功率加多少
        import random
        a=True if random.random()<possibility else False
        if a:
            answer="您的举报被有关部门成功记录了"+"\n"
            #成功记录的概率越高，加的应该越多#
            finaladd=random.random(minadd+(maxadd-minadd)*possibility,maxadd);self.finalwin+=finaladd
            finaladd=str(int(100*finaladd))+"%"
            answer+="成功率增加了"+finaladd+"\n"
            answer+="你可选择继续举报或者查询最终结果"+"\n"+"现在成功率是"+str(int(self.finalwin*100))+"%"
            return answer
        else:
            return "您的举报未被记录"+"\n"+"你可选择继续举报或者查询最终结果"+"\n"+"现在成功率是"+str(int(self.finalwin*100))+"%"
    def result(self):
        #查询并返回最终结果#
        import random
        a=True if random.random()<self.finalwin else False
        if a:
            return "你举报成功了，学校停止了补课"
        else:
            return "你举报失败了"

'''
#接下来的部分放在main里面运行，假定已经触发了游戏模式,用户的输入为user_input
possibility_data={}#懒得写
game=game(possibility_data)
while user_input!="查询结果":
    a=game.selectcase(user_input)
    if a!=0:
        #把a直接输出给用户然后continue,我不会写
    else:
        b=game.make_output(a)
        #把b直接输出给用户然后continue,我不会写
c=game.result()
#把c直接输出给用户,我不会写
'''






    
