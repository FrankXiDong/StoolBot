import json, random


def check(value, my_dict):
    for key in my_dict:
        if value == key:
            return True
    return False


def joingame(author):
    with open("./data/scor.txt", "r") as f:
        score = eval(f.read())
    a = eval(str(author))
    openid = a["member_openid"]
    with open("./data/userid.txt", "r", encoding="utf-8") as f:
        userid = eval(f.read())
    if openid in str(userid) == False:
        return "请先绑定你的QQ号或用户名。\n\
绑定方法：@机器人并发送指令“/绑定 ”+QQ号或用户名"
    else:
        a_name = userid[openid]
        a_id = openid
        if openid in str(score):
            return "用户" + a_name + "已加入过了，请勿重复加入！"
        else:
            score[a_id] = {"name": a_name, "exe": 1, "score": 0}
            with open("./data/scor.txt", "w") as f:
                f.write(str(score))
            return "用户" + a_name + "加入游戏成功~"


def startgame(author):
    with open("./data/scor.txt", "r") as f:
        score = eval(f.read())
    a = eval(str(author))
    openid = a["member_openid"]
    with open("./data/userid.txt", "r", encoding="utf-8") as f:
        userid = eval(f.read())
    a_name = userid[openid]
    a_id = openid
    n = len(score.keys())
    if n <= 1:
        return "参加的人数不够呢，快去邀请其他人一起加入吧！"
    else:
        win = random.randint(1, n)
        a = 0
        loser = []
        for i in score:
            a += 1
            if a == win:
                winner = score[i]["name"]
            else:
                loser.append(score[i]["name"])
        loser = str(loser).replace("[", "").replace("]", "")
        a = "获胜者：" + winner + "，\n输家：" + loser + "\n请输家接受获胜者的惩罚~"
        score = {}
        with open("./data/scor.txt", "w") as f:
            f.write("{}")
        return a
