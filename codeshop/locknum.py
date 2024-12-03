import os


def check(value, my_dict):
    for key in my_dict:
        if value == key:
            return True
    return False


def locknum(content, openid):
    user = content.split("/绑定 ")[1]  # 截取用户名
    with open("./temp/userid.txt", "r", encoding="utf-8") as f:
        userid = eval(f.read())
    if check(openid, userid) == False:  # 当检测到ID为未注册ID时，执行注册操作
        userid[openid] = user
        with open("./temp/userid.txt", "w", encoding="utf-8") as f:
            f.write(str(userid))
        return "用户" + user + "已绑定成功！"
    else:  # 当检测到ID为已注册ID时，执行改名操作
        userid[openid] = user
        with open("./temp/userid.txt", "w", encoding="utf-8") as f:
            f.write(str(userid))
        return "用户" + user + "已修改用户名！"
