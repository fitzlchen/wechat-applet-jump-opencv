# -*- coding: utf-8 -*-

import os
import sys
import time
import math
import random
from PIL import Image
import cv2
import numpy as np

VERSION = "0.9.8"
index = 0
def pull_screenshot():
    global index
    os.system('adb shell screencap -p /sdcard/autojump.png')
    os.system('adb pull /sdcard/autojump.png ./' + str(index) + '.png')

def jump(distance):
    # 按压时间 = 两点欧式距离 * 弹跳系数
    press_time = distance * 2.673
    press_time = int(press_time)
    rand = 50 * random.random()
    cmd = 'adb shell input swipe {} {} {} {} {}'.format(400 + rand, 500 + rand, 400 + rand, 500 + rand, str(press_time))
    #cmd = 'adb shell input swipe 320 410 320 410 ' + str(press_time)
    print(cmd)
    os.system(cmd)

def recognizeKeyPoint(nextImage, keypoint):
    # 落脚点灰度值范围 [245,247]
    keypoint[keypoint != 245] = 0
    nextImage[(nextImage < 243) | (nextImage > 247)] = 0
    res = cv2.matchTemplate(nextImage, keypoint,cv2.TM_CCOEFF_NORMED)
    min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)
    # 只取匹配度大于80%的情况
    if max_val < 0.8:
        print('keypoint not match')
        return None
    else :
        return max_loc

def recognizeJumper(nextImage, template):
    # 人物灰度值范围 [50,90]
    template[(template < 50) | (template > 90)]  = 0
    nextImage[(nextImage < 50) | (nextImage > 90)]  = 0
    res = cv2.matchTemplate(nextImage,template,cv2.TM_CCOEFF_NORMED)
    min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)
    # 只取匹配度大于80%的情况
    if max_val < 0.8:
        print('jumper not match')
        return None
    else :
        return max_loc

def recognizeNextStep(nextImage, template, background):
    shape = template.shape
    # 去棋盘背景色
    template_background = template[0,0]
    template[(template_background - 10 < template) & (template < template_background + 10)] = 0
    nextImage[(background - 10 < nextImage) & (nextImage < background + 10)] = 0
    res = cv2.matchTemplate(nextImage,template,cv2.TM_CCOEFF_NORMED)
    min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)
    # 可能出现人物阴影遮挡的情况，需要降低匹配度
    if max_val < 0.8:
        return None
    else :
        return (max_loc[0],max_loc[1],shape[1],shape[0])

# 计算两点欧式距离
def calDistance(src,tgt):
    return ((src[0]-tgt[0])**2 + (src[1] - tgt[1])**2)**0.5

def checkRuntime(prompt, true_value='y', false_value='n', default=True):
    """
    检查是否已经为启动程序做好了准备
    """
    default_value = true_value if default else false_value
    prompt = '{} {}/{} [{}]: '.format(prompt, true_value,
        false_value, default_value)
    i = input(prompt)
    if not i:
        return default
    while True:
        if i == true_value:
            return True
        elif i == false_value:
            return False
        prompt = 'Please input {} or {}: '.format(true_value, false_value)
        i = input(prompt)


def main():
    """
    主函数
    """
    op = checkRuntime('请确保手机打开了 ADB 并连接了电脑,然后打开跳一跳并【开始游戏】后再用本程序，确定开始？')
    if not op:
        print('bye')
        return
    global index

    i, next_rest, next_rest_time = (0, random.randrange(3, 10),
                                    random.randrange(5, 10))
    # 加载小人图片
    guy = cv2.imread('resource\\guy.png',0)
    guy_h,guy_w = guy.shape
    # 加载关键落地点图片
    keypoint = cv2.imread('resource\\surface\\landing.png',0)
    key_h,key_w = keypoint.shape

    # 第一次跳跃固定按压时间为715.5-717ms
    i = input('继续游戏按y，其他按键重新开始')
    if i != 'y':
        jump(267.7+random.random())
        time.sleep(random.uniform(1.5, 2))

    while True:
        # 拉取下一幅图
        pull_screenshot()
        nextImage = cv2.imread(str(index) + '.png',0)
        # 优先判断跳跃者位置
        loc = recognizeJumper(nextImage, guy)
        if loc == None:
            print('can not recogize jumper')
            quit(255)
        print('[guy location]loc:{}'.format(loc))
        gravityCenterOfGuy = [loc[0] + guy_w, loc[1] + guy_h/2]
        cv2.rectangle(nextImage, (loc[0], loc[1]), (loc[0] + guy_w, loc[1] + guy_h), (255,255,255), 1)
        # 小人中心
        cv2.rectangle(nextImage, (int(gravityCenterOfGuy[0]), int(gravityCenterOfGuy[1])), (int(gravityCenterOfGuy[0]) + 10, int(gravityCenterOfGuy[1]) + 10), (255,255,255), 1)

        # 判断图片中是否有理想落地点
        nextImage = cv2.imread(str(index) + '.png',0)
        # 获取小人周围背景的像素值
        background_pixal = nextImage[loc[1], loc[0]]
        loc = recognizeKeyPoint(nextImage, keypoint)
        if loc != None:
            x,y = loc
            print('[key point location]x:{},y:{}'.format(x, y))
            # 画出落脚点位置
            cv2.rectangle(nextImage, loc, (x + key_w, y + key_h), (255,255,255), 1)
            gravityCenterOfTemplate = [loc[0] + int(key_w/2), loc[1] + int(key_h/2)]
        else :
            # 识别下一步的棋子
            locs = []
            for file in os.listdir('resource\\surface\\'):
                nextImage = cv2.imread(str(index) + '.png',0)
                blockTemplate = cv2.imread('resource\\surface\\' + file,0)
                loc = recognizeNextStep(nextImage, blockTemplate, background_pixal)
                # 棋盘横向范围[200,1080]
                if loc != None and loc[0] > 200:
                   locs.append(loc)
            # 选出横坐标最小的 loc
            if len(locs) == 0:
                loc = None
            else :
                loc = sorted(locs, key=lambda item: item[0])[0]
    
            # 在图片上圈出目标物体
            if loc == None or loc[0] > gravityCenterOfGuy[0]:
                print('nothing match. Please jump next step by your own and restart this program.')
                quit(255)
            else :
                w = loc[2]
                h = loc[3]
                print('[next step]width:{},height:{}'.format(w, h))
                cv2.rectangle(nextImage, (loc[0], loc[1]), (loc[0] + w, loc[1] + h), (255,255,255), 1)
                gravityCenterOfTemplate = [loc[0] + w/2 , loc[1] + 0.485*h]
                # 垫子中心
                cv2.rectangle(nextImage, (int(gravityCenterOfTemplate[0]), int(gravityCenterOfTemplate[1])), (int(gravityCenterOfTemplate[0]) + 10, int(gravityCenterOfTemplate[1]) + 10), (255,255,255), 1)
                print('[next step location]x:{},y:{}'.format(gravityCenterOfTemplate[0], gravityCenterOfTemplate[1]))

        # 计算小人与目标地点的距离
        distance = calDistance(gravityCenterOfGuy, gravityCenterOfTemplate)
        print('distance:{}'.format(distance))
        # 将匹配图像留底，用于回顾
        cv2.imwrite(str(index) + '-matched.png',nextImage)
        jump(distance)
        index += 1
        # 为了保证截图的时候应落稳了，多延迟一会儿，随机值防 ban
        time.sleep(random.uniform(2.5, 3))


if __name__ == '__main__':
    main()
