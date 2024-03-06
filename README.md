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
