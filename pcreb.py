# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os
import datetime
import time
import cv2
import random
# 注意：请确保手机或模拟器的真实分辨率为 1280 x 720
# 先安装必备库
# pip3 install opencv-python numpy pandas
# 然后修改以下设置
# 1.设定临时工作文件夹，以路径符号 / 或 \ 结尾，建议设置为内存盘以减少硬盘磨损
tempdir = "/Volumes/RamDisk/"
# 2.刷新速度（秒）。太快会超过硬盘存取速度。内存盘建议1，其他建议3
refreshspeed = 1

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
    return str(int(round(f,0)))+"%"

def dimcom(a,b=0,se=5):
    """整数模糊比较"""
    if abs(a - b) <= se:
        return True
    return False

def wait3(istr=""):
    """等待3秒"""
    for w in range(0,3):
        time.sleep(1)
        tlog(str(3-w) + " " + istr + "...")

def btnr(btni):
    """生成按钮点击位置"""
    btnfx = btni[0]
    btnfy = btni[1]
    btntx = btni[0] + btni[2]
    btnty = btni[1] + btni[3]
    btnx = random.randint(btnfx,btntx)
    btny = random.randint(btnfy,btnty)
    return [btnx,btny]

t1 = [
    [0,"LOGO画面",24,392,255,255,255],
    [1,"Now Loading...",993,619,255,255,255],
    [2,"标题画面",634,546,247,81,148],
    [3,"战斗中",1174,18,255,255,189],
    [4,"WIN!",378,252,66,158,123],
    [5,"获得道具",549,199,198,65,49],
    [6,"FAILED",503,107,74,113,189],
    [7,"重试提示框",374,349,90,150,239]
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
    [649,462,273,63] #OK
]

cmd = os.popen('adb devices')
cmdreq = cmd.read()
cmdarr = cmdreq.split('\n')
title("超异域公主焊接(国服)自动重新挑战工具")
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
input("现在请开始战斗，战斗开始后按回车键继续：")
tlog("按 Ctrl+C 中止，中止之前请勿操作设备")
imgfile = tempdir + "pcrt.png"
i = 0
while True:
    i += 1
    tlog("识别序号：" + str(i))
    os.popen("adb -s \""+devicename+"\" exec-out screencap -p > \""+imgfile+"\"")
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
        if (dimcom(tr,r) and dimcom(tg,g) and dimcom(tb,b)):
            modeid = nt[0]
            tlog("当前状态（"+str(modeid)+"）："+tname)
            break
    if (modeid == -1):
        tlog("当前状态：未知")
    elif (modeid == 3): #正在战斗
        for waveinfo in t2:
            x = waveinfo[1]
            y = waveinfo[2]
            tr = waveinfo[3]
            tg = waveinfo[4]
            tb = waveinfo[5]
            b, g, r = img[y, x]
            if (dimcom(tr,r,50) and dimcom(tg,g,50) and dimcom(tb,b,50)):
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
                tlog("wave: "+str(waveid)+"/3")
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
    elif (modeid == 4): #WIN!
        t4c = t4[0]
        y = t4c[0]
        tr = t4c[1]
        tg = t4c[2]
        tb = t4c[3]
        xarr = t4[1]
        star = 0
        wait3("正在获取战斗评价")
        for x in xarr:
            b, g, r = img[y, x]
            if (dimcom(tr,r,50) and dimcom(tg,g,50) and dimcom(tb,b,50)):
                star += 1
        if star == 3:
            tok("战斗结束： ★ ★ ★")
        elif star == 2:
            twarn("战斗结束： ★ ★ ☆")
        elif star == 1:
            twarn("战斗结束： ★ ☆ ☆")
        wait3("秒后自动点按「下一步」按钮")
        btnxy = btnr(t5[0])
        os.popen("adb shell input tap "+str(btnxy[0])+" "+str(btnxy[1]))
        wait3("等待动画")
    elif (modeid == 5):
        wait3("秒后自动点按「再次挑战」按钮")
        btnxy = btnr(t5[1])
        os.popen("adb shell input tap "+str(btnxy[0])+" "+str(btnxy[1]))
        wait3("等待动画")
    elif (modeid == 6):
        twarn("警告：战斗败北，已自动停止")
        quit()
    elif (modeid == 7):
        wait3("秒后自动点按「OK」按钮")
        btnxy = btnr(t5[2])
        os.popen("adb shell input tap "+str(btnxy[0])+" "+str(btnxy[1]))
        wait3("等待动画")