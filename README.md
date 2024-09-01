# 前言
项目名：数字人视频播放器  
功能：可以通过HTTP API传入需要播放的视频，并排队在web页面自动播放  
目前支持的项目：  
- [Easy-Wav2Lip](https://github.com/anothermartz/Easy-Wav2Lip)（gradio API，使用的B站：眠NEON 提供的整合包：[视频传送门](https://www.bilibili.com/video/BV1rS421N71b)）  
- [Sadtalker](https://github.com/OpenTalker/SadTalker)（gradio API，整合包：[夸克网盘](https://pan.quark.cn/s/936dcae8aba0#/list/share/56a79e143a8b4877a98a61854e07b229-AI%20Vtuber/741f94606e414157b8d0a021d3a9ca77-%E8%99%9A%E6%8B%9F%E8%BA%AB%E4%BD%93/6ea2ecc2b19e49c4b1eda383a6aab194-Sadtalker), [迅雷云盘](https://pan.xunlei.com/s/VNitDF0Y3l-qwTpE0A5Rh4DaA1)）
- [GeneFacePlusPlus](https://github.com/yerfor/GeneFacePlusPlus)（gradio API，使用的B站：眠NEON 提供的整合包：[视频传送门](https://www.bilibili.com/video/BV1vz421R7ot)）  
- [MuseTalk](https://github.com/TMElyralab/MuseTalk)（gradio API，整合包：）  
- [AniTalker](https://github.com/X-LANCE/AniTalker)（gradio API，使用的B站：刘悦的技术博客 提供的整合包：[下载](https://pan.quark.cn/s/936dcae8aba0#/list/share/56a79e143a8b4877a98a61854e07b229-AI%20Vtuber/741f94606e414157b8d0a021d3a9ca77-%E8%99%9A%E6%8B%9F%E8%BA%AB%E4%BD%93/d31da81a7d64488d812ead76d3bc9f9c-AniTalker), [视频传送门](https://www.bilibili.com/video/BV1rS421N71b)）  

## 环境  
python：3.10.10  

# 使用

## 安装依赖

`pip install -r requirements.txt`

## 修改配置文件

自行根据需求修改`config.json`

## 运行API

`python api_server.py`

# API

运行后，可以查看API文档：[http://127.0.0.1:8091/docs](http://127.0.0.1:8091/docs)  

## 播放视频

### 概述

- **请求地址:** `/show`
- **请求类型:** POST
- **描述:** 传入视频进行播放，可以选择插入索引。

### 请求参数

| 参数名        | 类型   | 是否必需  | 描述                 |
|--------      |--------|----------|--------------        |
| type         | string | 是       | 使用的视频合成技术类型(easy_wav2lip / sadtalker / genefaceplusplus / musetalk / local) |
| video_path   | string | 是       | 视频文件的绝对路径（在local模式下必填）     |
| audio_path   | string | 是       | 音频文件的绝对路径     |
| captions_printer | string | 否   | 字幕打印机显示文本内容，不传则不发送     |
| captions_printer_start_delay | int | 否   | 字幕打印机显示文本内容的延时显示时间，不传则不发送     |
| insert_index | int    | 是       | 插入索引值，队尾插入：-1，队首插入：0，其他自定义 |
| move_file    | bool   | 否       | 是否移动合成或指定的视频文件到项目路径内。默认True |

### 响应

| 参数名  | 类型    | 描述         |
|--------|-------- |--------------|
| code   | int     | 状态码，200为成功，小于0为错误代码，大于0为部分成功代码 |
| msg    | string  | 响应消息，描述请求的处理结果 |

## 跳过当前播放的视频，播放下一个视频

### 概述

- **请求地址:** `/stop_current_video`
- **请求类型:** POST
- **描述:** 跳过当前播放的视频，播放下一个视频。

### 请求参数

| 参数名        | 类型   | 是否必需  | 描述                 |
|--------      |--------|----------|--------------        |


### 响应

| 参数名  | 类型    | 描述         |
|--------|-------- |--------------|
| code   | int     | 状态码，200为成功，小于0为错误代码，大于0为部分成功代码 |
| msg    | string  | 响应消息，描述请求的处理结果 |

## 获取队列中非默认视频的个数

### 概述

- **请求地址:** `/get_non_default_video_count`
- **请求类型:** POST
- **描述:** 获取队列中非默认视频的个数

### 请求参数

| 参数名        | 类型   | 是否必需  | 描述                 |
|--------      |--------|----------|--------------        |

### 响应

| 参数名  | 类型    | 描述         |
|--------|-------- |--------------|
| code   | int     | 状态码，200为成功，小于0为错误代码，大于0为部分成功代码 |
| count  | int     | 队列中非默认视频的个数 |
| msg    | string  | 响应消息，描述请求的处理结果 |

## 获取视频播放列表数据

### 概述

- **请求地址:** `/get_video_queue`
- **请求类型:** POST
- **描述:** 获取视频播放列表数据。

### 请求参数

| 参数名        | 类型   | 是否必需  | 描述                 |
|--------      |--------|----------|--------------        |


### 响应

| 参数名  | 类型    | 描述         |
|--------|-------- |--------------|
| code   | int     | 状态码，200为成功，小于0为错误代码，大于0为部分成功代码 |
| msg    | string  | 响应消息，描述请求的处理结果 |

## 设置相关配置

### 概述

- **请求地址:** `/set_config`
- **请求类型:** POST
- **描述:** 用于设置相关配置

### 请求参数

| 参数名        | 类型   | 是否必需  | 描述                 |
|--------      |--------|----------|--------------        |
| captions_printer_api_url   | string | 否       | 前端 字幕打印机API请求地址，例如：http://127.0.0.1:5500/send_message     |

### 响应

| 参数名  | 类型    | 描述         |
|--------|-------- |--------------|
| code   | int     | 状态码，200为成功，小于0为错误代码，大于0为部分成功代码 |
| data   | list    | list数据，存储着转换为url路径的视频地址 |
| msg    | string  | 响应消息，描述请求的处理结果 |

# 更新日志
- v0.3.1
    - 新增接口 set_config，用于设置相关配置，暂时仅提供前端 字幕打印机API地址设置功能

- v0.3.0
    - show接口 新增参数 captions_printer 控制字幕打印机显示文本内容，不传则不发送 
    - show接口 新增参数 captions_printer_start_delay 字幕打印机显示文本内容的延时显示时间，不传则不发送

- v0.2.3
    - 新增接口 get_video_queue，获取获取视频播放列表数据。
    - 修复 move_file传参不能关闭的bug
    - 配置文件新增参数 auto_del_video，支持控制是否在播放完视频后删除视频

- v0.2.2
    - 对接 AniTalker gradio API（gradio_client版本要求1.2.0及以上）
    - 删除旧版quart库实现的版本

- v0.2.1
    - 规范化API实现

- v0.2.0
    - 更换Quart为FastAPI
    - 针对 gradio视频合成卡播放问题的解决（gradio同步请求阻塞了server的其他请求，而前端的视频加载是通过server的URL加载的，server被阻塞后无法处理URL请求，导致前端被卡视频加载导致卡顿。目前将请求通过线程池（10个）单独托管，避免阻塞）

- v0.1.9
    - easy_wav2lip文件传参改用gradio_client传递，可以支持本地文件传递到云API
    - 提高httpx日志等级到WARNING
    - 针对linux系统请求win的gradio时，路径解析不正常问题进行针对性修正

- v0.1.8
    - 支持接口 stop_current_video，跳过当前播放的视频，播放下一个视频
    - 支持接口 get_non_default_video_count，获取队列中非默认视频的个数
    - show接口新增参数 move_file，可以控制是否移动合成或指定的视频文件到项目路径内。默认True

- v0.1.7
    - 支持local类型，直接播放本地视频
    - 支持 MuseTalk 对接

- v0.1.6
    - 新增默认配置`default_video`，可以在配置文件定义默认视频，不需要改源码了

- v0.1.5
    - 生成的视频将在播放完毕后直接删除，节省存储

- v0.1.4
    - 支持local类型，可以直接传入本地视频进行播放

- v0.1.3
    - sadtalker新增参数`gradio_api_type`用于适配不同的接口传参（api_name/fn_index）
    - 补充测试图和视频

- v0.1.2
    - 对接GeneFacePlusPlus(未测试)

- v0.1.1
    - 对接sadtalker
    - API新增参数type
    - 优化视频播放逻辑，尝试解决视频过渡时的无效等待问题


- v0.1.0
    - 初版发布


