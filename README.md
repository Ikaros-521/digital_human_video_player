# 前言
项目名：数字人视频播放器  
功能：可以通过HTTP API传入需要播放的视频，并排队在web页面自动播放  
目前支持的项目：  
- Easy-Wav2Lip（gradio API，使用的B站：眠NEON 提供的整合包：[视频传送门](https://www.bilibili.com/video/BV1rS421N71b)）

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

| 参数名        | 类型   | 是否必需  | 描述         |
|--------      |--------|----------|--------------|
| audio_path   | string | 是       | 音频文件的绝对路径 |
| insert_index | int    | 是       | 插入索引值，队尾插入：-1，队首插入：0，其他自定义 |

### 响应

| 参数名  | 类型    | 描述         |
|--------|-------- |--------------|
| code   | int     | 状态码，200为成功，小于0为错误代码，大于0为部分成功代码 |
| msg    | string  | 响应消息，描述请求的处理结果 |
