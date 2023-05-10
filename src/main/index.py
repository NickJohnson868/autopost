# coding=utf-8
import base64
import hashlib
import hmac
import json
import os
import random
import time
import urllib.parse

import requests

import getinfo
import post
import sign


def add_sign():
    timestamp = str(round(time.time() * 1000))
    secret = 'SEC09cb713b2d871cbf98b9720d09813e9107b3e1c9d530db53880d6dfa8246e218'
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = "https://oapi.dingtalk.com/robot/send?access_token=abfbd24d57748ca16ad9aa0fadb93f12cdd4068bb3385db25b41908afb6ef24c" + "&timestamp=" + timestamp + "&sign=" + sign
    return url


def qq(text):
    data = {
        "text": {
            "content": text
        },
        "msgtype": "text"
    }
    h = requests.post(add_sign(), json=data)


def run():
    print("开始 " + time.strftime("%Y/%m/%d") + " 的打卡任务")
    # 读取用户列表
    path = os.getcwd()
    if path.find("main") == -1:
        path += "/main"
    with open(path + "/users.json", 'r', encoding='utf-8') as file:
        allinfo = json.loads(file.read())
    with open(path + "/ua.txt", 'r', encoding='utf-8') as file:
        allUA = file.read().split("\n")
    text = '| 姓名 |  结果  |'
    for item in allinfo:
        name = item.get("name")
        print("开始为 " + name + " 打卡...")
        # 随机UA
        UA = random.choice(allUA)

        idx = 0
        exception = ''
        response = '无法连接到打卡接口，或者登录失败'
        while idx == 0 or exception == "'set-cookie'":
            try:
                # 获取用户cookie
                cook = sign.login(item, UA)
                # 获取返回的打卡结果
                response = post.run(item, UA, cook)
                # 若打卡成功，则exception = ''
                exception = ''
            except Exception as e:
                # 如果获取用户的cookie失败，则循环
                if str(e) == "'set-cookie'":
                    # 发消息通知我出现此类现象
                    qq(name + '用户出现cookie获取失败现象')
                    if idx < 3:
                        # 循环三次获取
                        exception = "'set-cookie'"
                        print(name + '用户获取cookie失败，尝试重试')
                    else:
                        # 超过三次默认失败
                        exception = ''
                        print('获取cookie失败，尝试次数过多，将自动跳过当前任务')
                        qq(name + '用户获取cookie失败，尝试次数过多，将自动跳过当前任务')
                else:
                    # 出现其他异常不处理，默认失败
                    exception = ''
                    print('---为' + name + '打卡失败\t' + str(e))
            idx += 1
            time.sleep(3)

        try:
            # 如果用户打卡信息为不健康，则通知我
            info = getinfo.data(item, UA, cook)
            if info['question_data'][1]['optiontitle'] != '健康':
                print('---' + name + '用户打卡信息为不健康，请及时修改')
                qq(name + '用户打卡信息为不健康，请及时修改')
        except Exception as e:
            print('---' + name + '用户获取健康信息失败！')
            qq(name + '用户获取健康信息失败！')

        # 为推送填写打卡信息
        text += f" \n| {name} | {response} |"
        time.sleep(3)

    print(time.strftime("%Y/%m/%d") + "的打卡任务结束\n")
    try:
        qq(time.strftime("%Y年%m月%d日") + "\n自动打卡任务已完成\n" + text)
    except requests.exceptions.ConnectionError:
        print("推送qq通知出错")


if __name__ == '__main__':
    while True:
        day = time.strftime("%m-%d", time.localtime())
        now_localtime = time.strftime("%H:%M", time.localtime())
        post_time = '00:00'
        with open('./time.txt', 'r') as file:
            post_time = file.read().replace('\n', '').replace('\r', '')
        if now_localtime == post_time:
            run()
        time.sleep(10)
