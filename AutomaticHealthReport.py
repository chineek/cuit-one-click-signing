from urllib.parse import urlencode, quote
import json5
import requests
from tkinter import *
from tkinter.messagebox import *
import platform
import os
import re
import time
import traceback

# 首先加载配置项
with open('config.json', 'r', encoding="utf-8") as f:
    cfgData = json5.load(f)
    f.close()
print("Config: ", cfgData)
# 初始化环境变量
common = {'codeKey': ''}
ssion = requests.session()


# 正则取值
def find_by_reg(reg, content):
    p = re.compile(reg)
    return p.findall(content)[0]


def yzm_get():
    # 首次请求
    http_headers = {
        'Connection': 'Keep-Alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'
    }
    response = ssion.get("http://jszx-jxpt.cuit.edu.cn/jxgl/xs/netks/sj.asp?jkdk=Y", headers=http_headers)
    next_url = find_by_reg('URL=(.+?)\"', response.content.decode("gb2312"))
    print("next_url:", next_url)
    http_headers['Host'] = 'login.cuit.edu.cn'
    response = ssion.get(next_url, headers=http_headers)
    # 验证码请求
    # 1. 正则表达式匹配js生成的验证码
    common['codeKey'] = find_by_reg('var codeKey = \'(.+?)\';', response.content.decode("gb2312"))
    print("yzmCode:", common['codeKey'])

    # 2. 获取验证码图片
    t = time.time()
    tmp = int(round(t * 1000))
    http_body = {'k': str(common['codeKey']),
                 't': str(tmp)
                 }
    http_headers['Accept'] = 'image/png, image/svg+xml, image/*; q=0.8, */*; q=0.5'
    http_headers['Referer'] = 'http://login.cuit.edu.cn/Login/xLogin/Login.asp'
    response = ssion.get("http://login.cuit.edu.cn/Login/xLogin/yzmDvCode.asp?" + urlencode(http_body),
                         headers=http_headers)
    file = open('yzmImage.bmp', 'wb')
    file.write(response.content)
    file.close()

    # 3. 使用操作系统打开验证码图片
    user_platform = platform.system()
    yzm_image = 'yzmImage.bmp'
    if user_platform == 'Darwin':
        os.subprocess.call(['open', yzm_image])
    elif user_platform == 'Linux':
        os.subprocess.call(['xdg-open', yzm_image])
    else:
        os.startfile(yzm_image)
    B1["text"] = "点击重新获取验证码"


def start_report():
    try:
        B2["text"] = "请求数据和运算中..."
        # 首先读取用户输入的验证码
        yzm = E1.get()
        if yzm == "":
            showinfo('提示', '请获取并输入验证码')
            return
        # 封装POST请求头
        http_headers = {
            'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
            'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.9, en-US; q=0.7, en; q=0.6, '
                               'zh-Hant-TW; q=0.4, zh-Hant; q=0.3, ja; q=0.1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
            'Cache-Control': 'max-age=0',
            'Referer': 'http://login.cuit.edu.cn/Login/xLogin/Login.asp',
            'Upgrade-Insecure-Requests': '1'
        }
        http_body = {'WinW': '1368',
                     'WinH': '872',
                     'txtId': cfgData["XueHao"],
                     'txtMM': cfgData["MiMa"],
                     'verifycode': yzm,
                     'codeKey': common['codeKey'],
                     'Login': 'Check',
                     'IbtnEnter.x': '34',
                     'IbtnEnter.y': '34'
                     }
        response = ssion.post("http://login.cuit.edu.cn/Login/xLogin/Login.asp", data=http_body,
                              headers=http_headers)
        date_now_day = time.strftime("%m%d")
        print("date_now_day", date_now_day)
        dk_link = find_by_reg('href=(.+?) target=_self>' + date_now_day + '疫情防控', response.content.decode("gb2312"))
        print("dk_link:", dk_link)
        response = ssion.get("http://jszx-jxpt.cuit.edu.cn/jxgl/xs/netks/" + dk_link, headers=http_headers)
        page_info = response.content.decode("gb2312")
        pag_url = response.url
        # 封装基本信息
        cfgData.pop("XueHao")
        cfgData.pop("MiMa")
        cfgData["B2"] = "提交打卡"
        cfgData["RsNum"] = find_by_reg('name=RsNum value=(.+?)>', page_info)
        cfgData["Id"] = find_by_reg('name=Id  value=\"(.+?)\">', page_info)
        cfgData["Tx"] = find_by_reg('name=Tx value=(.+?)>', page_info)
        cfgData["canTj"] = "1"
        cfgData["isNeedAns"] = find_by_reg('name=isNeedAns value=(.+?)>', page_info)
        cfgData["UTp"] = find_by_reg('name=UTp value=(.+?)>', page_info)
        cfgData["ObjId"] = find_by_reg('name=ObjId  value=\"(.+?)\">', page_info)
        cfgData["zw1"] = ""
        cfgData["zw2"] = ""
        cfgData["cxStYt"] = find_by_reg('name=cxStYt value=\"(.+?)\">', page_info)
        # 封装表单信息
        cfgData["th_1"] = find_by_reg('name=th_1 value=(.+?)>', page_info)
        cfgData["th_2"] = find_by_reg('name=th_2 value=(.+?)>', page_info)
        cfgData["th_3"] = find_by_reg('name=th_3 value=(.+?)>', page_info)
        cfgData["sF21648_N"] = find_by_reg('name=sF21648_N value=(.+?)>', page_info)
        cfgData["sF21649_N"] = find_by_reg('name=sF21649_N value=(.+?)>', page_info)
        cfgData["sF21650_N"] = find_by_reg('name=sF21650_N value=(.+?)>', page_info)
        # 聚合sF21648系列
        cfgData["wtOR_1"] = ""
        for i in range(1, 6):
            cfgData["wtOR_1"] += cfgData["sF21648_" + str(i)] + "\\|/"
        cfgData["wtOR_1"] += cfgData["sF21648_6"]
        # 聚合sF21649系列
        cfgData["wtOR_2"] = ""
        for j in range(1, 4):
            cfgData["wtOR_2"] += cfgData["sF21649_" + str(j)] + "\\|/"
        cfgData["wtOR_2"] += cfgData["sF21649_4"]
        # 聚合sF21650系列
        cfgData["wtOR_3"] = ""
        for k in range(1, 10):
            cfgData["wtOR_3"] += cfgData["sF21650_" + str(k)] + "\\|/"
        cfgData["wtOR_3"] += cfgData["sF21650_10"]
        #  URL加密信息
        # data_encoding_arr = ['sF21648_2', 'sF21648_4', 'sF21648_6', 'sF21649_2',
        #                      'sF21650_2', 'sF21650_3', 'sF21650_4', 'sF21650_10',
        #                      'wtOR_1', 'wtOR_2', 'wtOR_3']
        # for dataIdx in data_encoding_arr:
        #     cfgData[dataIdx] = quote(cfgData[dataIdx].encode("gb2312"))
        cfg_data_text = urlencode(cfgData, encoding='gb2312')
        print("cfg_data_text: ", cfg_data_text)
        # 自动注入完成
        http_headers = {
            'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
            'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.9, en-US; q=0.7, en; q=0.6, '
                               'zh-Hant-TW; q=0.4, zh-Hant; q=0.3, ja; q=0.1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
            'Referer': pag_url,
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'Keep-Alive'
        }
        # ssion.cookies['refreshCT'] = 'UserName=' + cfgData['UTp'] + '%5F' + cfgData['ObjId']
        # print("refreshCT: ", 'UserName=' + cfgData['UTp'] + '%5F' + cfgData['ObjId'])
        response = ssion.post("http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netks/editSjRs.asp", data=cfg_data_text,
                              headers=http_headers)
        info = find_by_reg('window\.(.+?)\(\"提交打卡成功！\"\);', response.content.decode("gb2312"))
        if info == "alert":
            showinfo("打卡成功", "一键打卡成功啦！可以登录网站检查打卡情况。")
        else:
            showerror("打卡失败", "打卡失败，未收到成功信息！")
    except Exception as e:
        showerror('异常',
                  '异常解决方案：请您检查账号密码、验证码、配置文件是否正确！\n'
                  '详细信息：' +
                  str(e) + "\n无法解决可提供以下信息给开发者:\n" +
                  str(traceback.format_exc()))
    finally:
        B2["text"] = "一键打卡结束"


# 2.3 展示验证码输入界面
root = Tk()
root.title("cuit一键健康打卡")
Text1 = Label(root, text="CUIT一键健康打卡工具 BY：Chineek")
Text2 = Label(root, text="*打卡前请您先配置setting.json文件", fg="red")

B1 = Button(root, text="点击获取验证码", command=yzm_get)
F = Frame(root, bg='white')
L1 = Label(F, text="验证码")
E1 = Entry(F, bd=5)
B2 = Button(root, text="一键打卡", command=start_report, bg="green", fg="white")

Text1.pack()
Text2.pack()
B1.pack(pady=10)
F.pack(pady=5)
L1.pack(side=LEFT)
E1.pack(side=RIGHT)
B2.pack(pady=10, padx=10, fill=X)

root.mainloop()
