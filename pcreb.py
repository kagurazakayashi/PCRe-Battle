# -*- coding: utf-8 -*-
#!/usr/bin/python3
from sys import version_info
if version_info.major != 3:
    raise Exception("请使用 Python 3 来运行本脚本。（当前 Python 版本为 "+str(version_info.major)+" ）")
import os
import sys
import datetime
import time
import cv2
import random
import signal
import easygui
import getopt
# 注意：请确保手机或模拟器的真实分辨率为 1280 x 720
# 先安装必备库 pip3 install opencv-python numpy pandas easygui
# 更多说明请参阅 README.md
tempdir = ""
refreshspeed = 2
waitingtime = 3
readonly = 0
prevmode = 0

def tlog(loginfo:"信息内容",end='\n'):
    """输出前面带时间的信息"""
    nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    nowtime = '['+nowtime.split('.')[0]+']'
    print("\033[35m",end='')
    print(nowtime,end='\033[0m ')
    print(loginfo,end=end)

def twarn(loginfo:"信息内容"):
    """输出警告"""
    tlog("\033[33m"+loginfo+"\033[0m")

def terr(loginfo:"信息内容"):
    """输出错误"""
    tlog("\033[31m"+loginfo+"\033[0m")

def tok(loginfo:"信息内容"):
    """输出正确"""
    tlog("\033[32m"+loginfo+"\033[0m")

def title(loginfo:"信息内容"):
    """输出标题"""
    tlog("\033[1m"+loginfo.center(30,'=')+"\033[0m")

def f2s(f):
    """浮点转整数文本"""
    text = str(int(round(f,0)))
    if len(text) == 1:
        return "  "+text+"%"
    elif len(text) == 2:
        return " "+text+"%"
    else:
        return text+"%"

def dimcom(a,b=0,se=5):
    """整数模糊比较"""
    if abs(a - b) <= se:
        return True
    return False

def wait3(waitingtime,istr=""):
    """等待3秒"""
    for w in range(0,waitingtime):
        tlog(str(waitingtime-w) + " " + istr + "...")
        time.sleep(1)

def btnr(btni):
    """生成按钮点击位置"""
    btnfx = btni[0]
    btnfy = btni[1]
    btntx = btni[0] + btni[2]
    btnty = btni[1] + btni[3]
    btnx = random.randint(btnfx,btntx)
    btny = random.randint(btnfy,btnty)
    return [btnx,btny]

def screenshot(devicename,imgfile):
    """获取屏幕截图"""
    cmd = os.popen("adb -s \""+devicename+"\" exec-out screencap -p 2>&1 > \""+imgfile+"\"")
    cmdreq = cmd.read()
    if ("not found" in cmdreq) or ("offline" in cmdreq):
        terr("错误：与设备的连接丢失，程序中止。")
        tlog(cmdreq)
        quit()
    elif cmdreq != "":
        terr("错误："+cmdreq)
        quit()

def tap(x,y,readonly):
    """发送点击命令"""
    if readonly == 1:
        twarn("\a[只读模式] 战斗完毕，请手工开始战斗后按回车键继续：")
        easygui.msgbox("战斗完毕！请手工开始战斗后，重新开始本程序。", title="PCR 战斗完毕",ok_button="退出")
        quit()
        return
    elif readonly == 3:
        return
    cmd = os.popen("adb shell input tap "+str(x)+" "+str(y)+" 2>&1")
    cmdreq = cmd.read()
    if ("found" in cmdreq) or ("offline" in cmdreq):
        terr("错误：与设备的连接丢失，程序中止。")
        tlog(cmdreq)
        quit()
    elif cmdreq != "":
        terr("错误："+cmdreq)
        quit()

def gameoveri():
    global gameover
    global gameover0
    global gameover1
    global gameover2
    global gameover3
    gameovera = gameover0+gameover1+gameover2+gameover3
    tlog("本次已完成战斗: "+str(gameover)+" 。")
    tlog("本次已记录评价: "+str(gameovera)+" 。")
    tlog("★ ★ ★ 评价: "+str(gameover3)+" 。")
    tlog("★ ★ ☆ 评价: "+str(gameover2)+" 。")
    tlog("★ ☆ ☆ 评价: "+str(gameover1)+" 。")
    tlog("☆ ☆ ☆ 评价: "+str(gameover0)+" 。")

def exit(signum, frame):
    tok("收到退出指令...")
    gameoveri()
    tok("程序退出。")
    quit()

t1 = [
    [0,"LOGO画面",24,392,255,255,255],
    [1,"Now Loading...",993,619,255,255,255],
    [2,"标题画面",634,546,247,81,148],
    [3,"战斗中",1174,18,255,255,189],
    [4,"WIN!",378,252,66,158,123],
    [5,"获得道具",549,199,198,65,49],
    [6,"FAILED",503,107,74,113,189],
    [7,"重试提示框",374,349,90,150,239],
    [8,"提示框",351,194,74,134,222],
    [9,"BOSS结算",182,641,99,150,238]
]
# wave
t2 = [
    [2,35,42,99,101,115],
    [1,35,42,247,251,247],
    [3,32,44,74,77,90]
]
# hp/mp
t3 = [
    [669,119,200,696,230],
    [260,420,581,742,901]
]
# star
t4 = [
    [178,255,252,180],
    [565,637,709],
]
# btn
t5 = [
    [974,641,270,63], #下一步
    [778,624,211,60], #再次挑战
    [649,462,273,63], #OK
    [942,643,271,62]
]
# boss
t6 = [
    [629,97,255,223,115]
]

title("超异域公主焊接(国服)自动重新挑战工具 v1.1")
tlog("正在启动...")
try:
    opts, args = getopt.getopt(sys.argv[1:],"r:t:s:w:",["readonly=","tempdir=","refreshspeed=","waitingtime="])
except getopt.GetoptError:
    terr("输入参数不正确，使用方法请参阅 README.md 。")
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-r", "--readonly"):
        tlog("只读模式: "+arg)
        readonly = int(arg)
    elif opt in ("-t", "--tempdir"):
        tlog("临时工作文件夹: "+arg)
        tempdir = arg
    elif opt in ("-s", "--refreshspeed"):
        tlog("刷新速度: "+arg)
        refreshspeed = int(arg)
    elif opt in ("-w", "--waitingtime"):
        tlog("等待时间: "+arg)
        waitingtime = int(arg)

signal.signal(signal.SIGINT, exit)
signal.signal(signal.SIGTERM, exit)
if len(sys.argv) > 1:
    if sys.argv[1] == "r":
        readonly = 1
gameover = 0
gameover3 = 0
gameover2 = 0
gameover1 = 0
gameover0 = 0
cmd = os.popen('adb devices')
cmdreq = cmd.read()
cmdarr = cmdreq.split('\n')
time.sleep(1)
tlog("正在查找设备...")
if (cmdarr[0] != "List of devices attached"):
    terr("错误：ADB 配置错误。")
    tlog("请先安装 ADB 并确保 adb 命令能够在命令行中运行。")
    quit()
if (cmdarr[1] == ""):
    terr("错误：没有找到设备。")
    tlog("请先启动 模拟器 或 连接到手机 并 开启 adb 调试。")
    tlog("如果使用的是 MuMu 模拟器，请尝试 http://mumu.163.com/2017/12/19/25241_730476.html")
    quit()
tlog("找到了以下设备：")
i = 0
devicelist = []
for device in cmdarr:
    if (device == ""):
        continue
    devicearr = device.split('\t')
    if (len(devicearr) != 2):
        continue
    i += 1
    emulator = ""
    if "emulator" in devicearr[0]:
        emulator = "（Android 模拟器）"
    tlog("序号："+str(i)+", 名称："+devicearr[0]+", 类型："+devicearr[1]+emulator)
    devicelist.append(devicearr)
deviceid = 1
if (len(devicelist) > 1):
    sel = input("请输入要连接设备的序号：")
    deviceid = int(sel)
    if (devicelist < 0 or devicelist > len(cmdarr)-1):
        terr("错误：输入不正确。")
        quit()
else:
    print("请输入要连接设备的序号：1 （只有1个设备，自动选择第1个）")
seldevice = devicelist[deviceid-1]
devicename = seldevice[0]
tlog("已选择设备："+devicename)
# input("现在请开始战斗，战斗开始后按回车键继续：")
tlog("按 Ctrl+C 中止，中止之前请勿操作设备")
imgfile = tempdir + "pcrt.png"
i = 0
while True:
    i += 1
    tlog("识别序号：" + str(i))
    screenshot(devicename,imgfile)
    time.sleep(refreshspeed)
    img = cv2.imread(imgfile, cv2.IMREAD_COLOR)
    for ei in range(0,10):
        if img is None:
            twarn("发生了一次跳帧。如果经常发生，请调高 refreshspeed 。")
            time.sleep(refreshspeed)
            img = cv2.imread(imgfile, cv2.IMREAD_COLOR)
        else:
            break
    if img is None:
        terr("错误：未能获得有效图片信息。")
        quit()
    modeid = -1
    for nt in t1:
        tname = nt[1]
        x = nt[2]
        y = nt[3]
        tr = nt[4]
        tg = nt[5]
        tb = nt[6]
        b, g, r = img[y, x]
        w = len(img[0])
        h = len(img)
        if w != 1280 or h != 720:
            terr("错误：程序要求设备实际屏幕像素必须为 1280x720 才能使用。")
            tlog("当前的屏幕尺寸为 "+str(w)+"x"+str(h)+" 。")
            quit()
        if (dimcom(tr,r) and dimcom(tg,g) and dimcom(tb,b)):
            modeid = nt[0]
            tlog("当前状态（"+str(modeid)+"）："+tname)
            break
    if modeid == -1:
        tlog("当前状态：未知")
    elif modeid == 3: #正在战斗
        for waveinfo in t2:
            x = waveinfo[1]
            y = waveinfo[2]
            tr = waveinfo[3]
            tg = waveinfo[4]
            tb = waveinfo[5]
            b, g, r = img[y, x]
            if (dimcom(tr,r) and dimcom(tg,g) and dimcom(tb,b)):
                waveid = waveinfo[0]
                if waveid == 1:
                    t22 = t2[2]
                    x = t22[1]
                    y = t22[2]
                    tr = t22[3]
                    tg = t22[4]
                    tb = t22[5]
                    b, g, r = img[y, x]
                    if (dimcom(tr,r) and dimcom(tg,g) and dimcom(tb,b)):
                        waveid = 3
                tlog("第 "+str(gameover+1)+" 次战斗中, Wave: "+str(waveid)+"/3")
                break
        hpi = t3[0]
        yline = hpi[0]
        xwidth = hpi[1]
        green = hpi[2]
        ylinem = hpi[3]
        blue = hpi[4]
        hps = t3[1]
        chrid = 0
        barhp = [0,0,0,0,0]
        barmp = [0,0,0,0,0]
        for hpbar in hps:
            hpbarend = hpbar + xwidth
            hp = 0
            mp = 0
            for j in range(hpbar,hpbarend):
                b1, g1, r1 = img[yline, j]
                b2, g2, r2 = img[ylinem, j]
                if (g1 > green):
                    hp += 1
                if (b2 > blue):
                    mp += 1
            barhp[chrid] = hp / xwidth * 100
            barmp[chrid] = mp / xwidth * 100
            chrid += 1
        tlog("血量: ① "+f2s(barhp[0])+"  ② "+f2s(barhp[1])+"  ③ "+f2s(barhp[2])+"  ④ "+f2s(barhp[3])+"  ⑤ "+f2s(barhp[4]))
        tlog("技能: ① "+f2s(barmp[0])+"  ② "+f2s(barmp[1])+"  ③ "+f2s(barmp[2])+"  ④ "+f2s(barmp[3])+"  ⑤ "+f2s(barmp[4]))
    elif modeid == 4: #WIN!
        t4c = t4[0]
        y = t4c[0]
        tr = t4c[1]
        tg = t4c[2]
        tb = t4c[3]
        xarr = t4[1]
        star = 0
        wait3(waitingtime,"正在获取战斗评价")
        gameover += 1
        for x in xarr:
            b, g, r = img[y, x]
            if (dimcom(tr,r,50) and dimcom(tg,g,50) and dimcom(tb,b,50)):
                star += 1
        battleend = "第 "+str(gameover)+" 次战斗结束： "
        if star == 3:
            tok(battleend+"★ ★ ★")
            gameover3 += 1
        elif star == 2:
            twarn(battleend+"★ ★ ☆")
            gameover2 += 1
        elif star == 1:
            twarn(battleend+"★ ☆ ☆")
            gameover1 += 1
        gameoveri()
        wait3(waitingtime,"秒后自动点按「下一步」按钮")
        btnxy = btnr(t5[0])
        tap(btnxy[0],btnxy[1],readonly)
        wait3(waitingtime,"等待动画")
    elif modeid == 5:
        wait3(waitingtime,"秒后自动点按「再次挑战」按钮")
        btnxy = btnr(t5[1])
        tap(btnxy[0],btnxy[1],readonly)
        wait3(waitingtime,"等待动画")
    elif modeid == 6:
        gameover += 1
        gameover0 += 1
        twarn("第 "+str(gameover)+" 次战斗结束： ☆ ☆ ☆")
        twarn("警告：战斗败北，已自动停止")
        gameoveri()
        quit()
    elif modeid == 7:
        wait3(waitingtime,"秒后自动点按「OK」按钮")
        btnxy = btnr(t5[2])
        tap(btnxy[0],btnxy[1],readonly)
        wait3(waitingtime,"等待动画")
    elif modeid == 8: #提示框
        twarn("\a出现了一个提示框，请确认内容。")
        if readonly == 1:
            easygui.msgbox("出现了一个提示框，请确认内容。处理完毕后，重新开始本程序。", title="PCR 提示框",ok_button="退出")
            quit()
        else:
            input("在处理完毕后，按回车键继续...")
    elif modeid == 9: #活动BOSS战
        win = t6[0]
        x = win[0]
        y = win[1]
        tr = win[2]
        tg = win[3]
        tb = win[4]
        b, g, r = img[y, x]
        gameover += 1
        if dimcom(tr,r) and dimcom(tg,g) and dimcom(tb,b):
            gameover3 += 1
            tok("第 "+str(gameover)+" 次战斗结束： BOSS战： 成功。")
            wait3(waitingtime,"秒后自动点按「下一步」按钮")
            btnxy = btnr(t5[3])
            tap(btnxy[0],btnxy[1],readonly)
            wait3(waitingtime,"等待动画")
        else:
            gameover0 += 1
            twarn("第 "+str(gameover)+" 次战斗结束： BOSS战： 失败。")
            twarn("警告：战斗败北，已自动停止")
            quit()
    prevmode = modeid