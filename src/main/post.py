# coding=utf-8
import requests
import getinfo
import json


def run(studata, UA, cook):
    """获取处理后的数据
    :param studatae:学生信息
    :param UA:传入的UA
    :param cook:传入的cookie
    :return :打卡结果
    """
    # 读取个人提交信息
    info = getinfo.data(studata, UA, cook)
    # if info['question_data'][2]['isanswered'] == True and info['question_data'][2]['optiontitle'] == '健康':
    #    print("今日打卡已完成，自动打卡取消")
    #    return "重复！已完成"

    # 提交今日打卡
    url = 'https://yq.weishao.com.cn/api/questionnaire/questionnaire/addMyAnswer'
    head = {
        'Host': 'yq.weishao.com.cn',
        'Connection': 'keep-alive',
        'User-Agent': UA,
        'Accept': '*/*',
        'Content-Length': str(len(str(info))),  # json转文字读取长度，再转为字符串
        'Content-Type': 'application/json',
        'Origin': 'https://yq.weishao.com.cn',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://yq.weishao.com.cn/questionnaire/addanswer?page_from=onpublic&activityid=5723&can_repeat=1',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN, zh;q = 0.9',
        'Cookie': cook,
    }
    data = requests.post(url, json=info, headers=head).json()
    if data.get("errcode") == 0:
        print("打卡成功！")
        return "打卡成功！"
    else:
        print("---打卡错误\t" + str(data))
        return data.get("errmsg")
