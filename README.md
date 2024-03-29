# 前言
项目名：数字人视频播放器  
功能：可以通过HTTP API传入需要播放的视频，并排队在web页面自动播放  
目前支持的项目：  
- [Easy-Wav2Lip](https://github.com/anothermartz/Easy-Wav2Lip)（gradio API，使用的B站：眠NEON 提供的整合包：[视频传送门](https://www.bilibili.com/video/BV1rS421N71b)）  
- [Sadtalker](https://github.com/OpenTalker/SadTalker)（gradio API，整合包：[夸克网盘](https://pan.quark.cn/s/936dcae8aba0#/list/share/56a79e143a8b4877a98a61854e07b229-AI%20Vtuber/741f94606e414157b8d0a021d3a9ca77-%E8%99%9A%E6%8B%9F%E8%BA%AB%E4%BD%93/6ea2ecc2b19e49c4b1eda383a6aab194-Sadtalker), [迅雷云盘](https://pan.xunlei.com/s/VNitDF0Y3l-qwTpE0A5Rh4DaA1)）
- [GeneFacePlusPlus](https://github.com/yerfor/GeneFacePlusPlus)（gradio API，使用的B站：眠NEON 提供的整合包：[视频传送门](https://www.bilibili.com/video/BV1vz421R7ot)）  

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

## 播放视频

### 概述

- **请求地址:** `/show`
- **请求类型:** POST
- **描述:** 传入视频进行播放，可以选择插入索引。

### 请求参数

| 参数名        | 类型   | 是否必需  | 描述                 |
|--------      |--------|----------|--------------        |
| type         | string | 是       | 使用的视频合成技术类型(easy_wav2lip / sadtalker / genefaceplusplus) |
| audio_path   | string | 是       | 音频文件的绝对路径     |
| insert_index | int    | 是       | 插入索引值，队尾插入：-1，队首插入：0，其他自定义 |

### 响应

| 参数名  | 类型    | 描述         |
|--------|-------- |--------------|
| code   | int     | 状态码，200为成功，小于0为错误代码，大于0为部分成功代码 |
| msg    | string  | 响应消息，描述请求的处理结果 |

# 更新日志

- v0.1.0
    - 初版发布

- v0.1.1
    - 对接sadtalker
    - API新增参数type
    - 优化视频播放逻辑，尝试解决视频过渡时的无效等待问题

- v0.1.2
    - 对接GeneFacePlusPlus(未测试)
