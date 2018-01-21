# wechat-applet-jump-opencv
基于OpenCV，轻松拿跳一跳高分
`配置简单`、`实验可复现`、`不需要安卓或iOS物理设备`
## 背景 

对于玩家而言，不论人物所在的垫子是什么尺寸或颜色，按压时候下降的速度都是非常稳定的，即可以认为每一个垫子的弹力系数都是一样的。因此，可以猜想相同的按压时长，应该可以获得相同的跳跃距离。经过按压时间-跳跃距离的散点图，验证了这一点。

在按压时长和跳跃距离成正比的条件下，如果能利用图像识别的方法，精确定位起跳点和落地点，就可以精确计算两点的距离并计算对应的按压时长。

## 物体识别原理

跳一跳的人物只有一种素材图片（尺寸不变），推荐落脚点只有一种素材图片（尺寸不变），垫子则大致五十种素材（同种类型的素材会存在不同的尺寸）。

跳一跳的背景色会不断变化，如果简单采用`OpenCV matchTemplate`匹配方式，则需要素材图片的背景色和游戏背景色非常接近才能保持较高的匹配度。

因此有这么两种思路，一种是根据`Canny operator`描绘素材图片和游戏画面的物体边缘；一种是将素材图片和游戏画面分别进行去背景色处理，之后再进行匹配；

经过验证，第一种思路的匹配效果不是很理想，第二种思路的匹配度则基本稳定超过80%。

## 整体流程

1.通过`adb`拉取模拟器的游戏画面

2.识别人物位置

3.识别推荐落地点

4.识别下一步的垫子

5.计算人物与落地点的欧式距离

6.计算按压时间

7.弹跳

## 识别效果
人物识别

![](https://github.com/sthbig/wechat-applet-jump-opencv/blob/master/img/guy-matched.png)

垫子识别

![](https://github.com/sthbig/wechat-applet-jump-opencv/blob/master/img/step-matched1.png)

![](https://github.com/sthbig/wechat-applet-jump-opencv/blob/master/img/step-matched2.png)

### 运行效果

![](https://github.com/sthbig/wechat-applet-jump-opencv/blob/master/img/res1.png)

![](https://github.com/sthbig/wechat-applet-jump-opencv/blob/master/img/res2.png)

### 运行环境

`Python 3.x` (<a href="https://www.python.org/downloads/release/python-364/">参考下载地址</a>)

`adb`（<a href="https://www.xda-developers.com/install-adb-windows-macos-linux/">adb配置方式</a>）

`雷电模拟器`（<a href="http://www.ldmnq.com">模拟器使用和下载指南</a>）

### 使用教程

1.启动雷电模拟器，选择屏幕尺寸 `1920 * 1280`；

2.电脑启动终端（Win 用户 `windows + R` -> `cmd`；Unix/Linux 用户 `terminal`)

3.运行 `auto.py`

### 局限

1.垫子的跳跃系数是一个 `magic number`，暂且做不到随机初始化，通过不断重新开始游戏来学习最佳参数的理想状态；

2.不同尺寸的同种垫子要求各有一张素材图片，是否可以做到尺度不变的物体识别？（尝试过`OpenCV SIFT`，识别效果不是很理想）

### 感谢

<a href="https://github.com/wangshub/wechat_jump_game">@神奇的战士</a>
