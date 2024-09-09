from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import os
import json
import logging
import traceback
import threading
from selenium import webdriver
from urllib.parse import unquote

from fastapi.middleware.cors import CORSMiddleware

from utils.config import Config
from utils.common import Common
from utils.logger import Configure_logger
from utils.video_generate import run_get_video
from utils.models import ShowMessage, DelVideoWithIndexMessage, GetNonDefaultVideoCountResult, GetVideoQueueResult, CommonResult, SetConfigMessage

# 获取 httpx 库的日志记录器
httpx_logger = logging.getLogger("httpx")
# 设置 httpx 日志记录器的级别为 WARNING
httpx_logger.setLevel(logging.WARNING)

common = Common()
# 日志文件路径
file_path = "./log/log-" + common.get_bj_time(1) + ".txt"
Configure_logger(file_path)
config = Config("config.json")

# 获取当前脚本的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 设置静态文件夹路径为相对于当前脚本目录的路径
static_folder = os.path.join(script_dir, 'static')
static_folder = os.path.abspath(static_folder)

logging.info(f"static_folder={static_folder}")

app = FastAPI()

# 添加 CORS 中间件，允许所有跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许发送带有凭据的请求
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# Mount static folder
app.mount("/static", StaticFiles(directory=static_folder), name="static")

connected_websockets = set()


# 队列中非默认视频个数
non_default_video_count = 0
# 视频播放队列数据
video_queue = []

@app.get("/")
async def home():
    return RedirectResponse(url="/static/index.html")

@app.get("/videos/{filename:path}")
async def load_video(filename: str):
    video_path = os.path.join(static_folder, 'video', filename)
    return await StaticFiles(directory=os.path.dirname(video_path)).get_response(os.path.basename(video_path))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global non_default_video_count, video_queue

    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                data_json = json.loads(data)
                logging.info(f"收到客户端数据: {data_json}")
                # 处理从客户端接收的数据的逻辑
                if data_json['type'] == "videoEnded":
                    non_default_video_count = data_json['count']
                    # 跳过默认视频
                    if common.get_filename_with_ext(config.get("default_video")) not in data_json['video_path']:
                        # 是否启用了自动删除视频配置（视频由于占用大，建议启用视频删除避免磁盘占满）
                        if config.get("auto_del_video"):
                            # 在这里添加删除视频文件的逻辑
                            await delete_video_file(data_json['video_path'])
                elif data_json['type'] == "get_default_video":
                    logging.info(f"发送默认配置 视频路径: {config.get('default_video')}")
                    # 在这里添加发送消息到客户端的逻辑
                    await send_to_all_websockets(json.dumps({"type": "set_default_video", "video_path": config.get("default_video")}))
                elif data_json['type'] == "show":
                    logging.info(f"队列中非默认视频个数: {data_json['count']}")
                    non_default_video_count = data_json['count']
                elif data_json['type'] == "get_non_default_video_count":
                    logging.info(f"队列中非默认视频个数: {data_json['count']}")
                    non_default_video_count = data_json['count']
                elif data_json['type'] == "get_video_queue":
                    logging.debug(f"视频队列: {data_json['data']}")
                    video_queue = data_json['data']
                elif data_json['type'] == "del_video_with_index":
                    logging.debug(f"视频队列: {data_json['data']}")
                    video_queue = data_json['data']
            except WebSocketDisconnect:
                logging.info("ws客户端连接已关闭")
                break
            except Exception as e:
                logging.error(traceback.format_exc())
    finally:
        connected_websockets.remove(websocket)

# 删除视频文件
async def delete_video_file(video_path: str):
    file_name_with_extension = os.path.basename(video_path)
    file_name_with_extension = unquote(file_name_with_extension, 'utf-8')
    relative_path = os.path.join(static_folder, "videos", file_name_with_extension)

    try:
        os.remove(relative_path)  # 删除视频文件
        logging.info(f"成功删除视频文件 {relative_path}。")
    except FileNotFoundError:
        logging.error(f"未找到视频文件 {relative_path}。")
    except Exception as e:
        logging.error(f"删除视频文件时发生错误：{str(e)}")

async def send_to_all_websockets(data):
    for ws in connected_websockets:
        await ws.send_text(data)

def extract_filename(video_path):
    import re
    if '=' in video_path:
        filepath = video_path.split('=')[1]
    else:
        filepath = video_path

    match = re.search(r'[^\\/:*?"<>|\r\n]+$', filepath)
    if match:
        return match.group()
    else:
        return common.get_filename_with_ext(filepath)

@app.post("/show")
async def show(msg: ShowMessage):
    try:
        data = msg.model_dump()

        logging.info(f"收到数据：{data}")

        video_path = await run_get_video(data["type"], data, config)

        if video_path:
            static_video_path = os.path.join(static_folder, "videos")
            logging.debug(f"视频文件移动到的路径：{static_video_path}")

            filename = ""
            move_file = data.get("move_file")
            is_linux = common.detect_os() == "Linux"

            if move_file:
                if is_linux:
                    filename = extract_filename(video_path)
                    ret = common.move_and_rename(video_path, static_video_path, new_filename=filename, move_file=move_file)
                else:
                    ret = common.move_and_rename(video_path, static_video_path, move_file=move_file)
                    filename = common.get_filename_with_ext(video_path)
            else:
                if is_linux:
                    filename = extract_filename(video_path)
                    ret = common.move_and_rename(video_path, static_video_path, new_filename=filename, move_file=False)
                else:
                    ret = common.move_and_rename(video_path, static_video_path, move_file=False)
                    filename = common.get_filename_with_ext(video_path)
            if not ret:
                return CommonResult(code=200, message="视频移动失败")

            file_url = f"http://127.0.0.1:{config.get('server_port')}/static/videos/{filename}"

            if "audio_path" not in data:
                data["audio_path"] = None

            if "insert_index" not in data:
                data["insert_index"] = -1

            if "captions_printer" not in data:
                await send_to_all_websockets(
                    json.dumps(
                        {
                            "type": "show",
                            "video_path": file_url,
                            "audio_path": data["audio_path"],
                            "insert_index": data["insert_index"]
                        }
                    )
                )
            else:
                await send_to_all_websockets(
                    json.dumps(
                        {
                            "type": "show",
                            "video_path": file_url,
                            "audio_path": data["audio_path"],
                            "captions_printer": data["captions_printer"],
                            "insert_index": data["insert_index"]
                        }
                    )
                )

            return CommonResult(code=200, message="操作成功")
        return CommonResult(code=200, message="视频合成失败")
    except Exception as e:
        logging.error(traceback.format_exc())
        return CommonResult(code=-1, message=f"操作失败: {str(e)}")

@app.post("/stop_current_video")
async def stop_current_video():
    try:
        await send_to_all_websockets(
            json.dumps(
                {
                    "type": "stop_current_video"
                }
            )
        )
        return CommonResult(code=200, message="操作成功")
    except Exception as e:
        logging.error(traceback.format_exc())
        return CommonResult(code=-1, message=f"操作失败: {str(e)}")

@app.post("/get_non_default_video_count")
async def get_non_default_video_count():
    try:
        await send_to_all_websockets(
            json.dumps(
                {
                    "type": "get_non_default_video_count"
                }
            )
        )
        await asyncio.sleep(0.5)
        return GetNonDefaultVideoCountResult(code=200, count=non_default_video_count, message="操作成功")
    except Exception as e:
        logging.error(traceback.format_exc())
        return CommonResult(code=-1, message=f"操作失败: {str(e)}")

# 获取视频队列
@app.post("/get_video_queue")
async def get_video_queue():
    try:
        await send_to_all_websockets(
            json.dumps(
                {
                    "type": "get_video_queue"
                }
            )
        )
        await asyncio.sleep(0.5)
        return GetVideoQueueResult(code=200, data=video_queue, message="操作成功")
    except Exception as e:
        logging.error(traceback.format_exc())
        return CommonResult(code=-1, message=f"操作失败: {str(e)}")

# 删除指定索引的视频
@app.post("/del_video_with_index")
async def del_video_with_index(msg: DelVideoWithIndexMessage):
    try:
        await send_to_all_websockets(
            json.dumps(
                {
                    "type": "del_video_with_index",
                    "index": msg.index
                }
            )
        )
        await asyncio.sleep(0.5)
        return GetVideoQueueResult(code=200, data=video_queue, message="操作成功")
    except Exception as e:
        logging.error(traceback.format_exc())
        return CommonResult(code=-1, message=f"操作失败: {str(e)}")

# 设置配置
@app.post("/set_config")
async def set_config(msg: SetConfigMessage):
    try:
        await send_to_all_websockets(
            json.dumps(
                {
                    "type": "set_config",
                    "data": msg.dict()
                }
            )
        )
        await asyncio.sleep(0.5)
        return CommonResult(code=200, message="操作成功")
    except Exception as e:
        logging.error(traceback.format_exc())
        return CommonResult(code=-1, message=f"操作失败: {str(e)}")

def start_browser(stop_event):
    options = webdriver.ChromeOptions()
    # 设置为开发者模式，避免被浏览器识别为自动化程序
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--autoplay-policy=no-user-gesture-required')
    driver = webdriver.Chrome(options=options)

    # 火狐
    # options = webdriver.FirefoxOptions()
    # # 设置为开发者模式，避免被浏览器识别为自动化程序
    # options.set_preference('dom.webdriver.enabled', False)
    # options.set_preference('media.autoplay.default', 0)  # 设置自动播放策略
    # driver = webdriver.Firefox(options=options)

    driver.get(f'http://127.0.0.1:{config.get("server_port")}')
    stop_event.wait()

class StoppableThread(threading.Thread):
    def __init__(self, target=None, stop_event=None):
        super().__init__()
        self._stop_event = stop_event
        self._target = target

    def run(self):
        if self._target:
            self._target(self._stop_event)
        self._stop_event.wait()
        logging.info("Thread is stopping")

    def stop(self):
        self._stop_event.set()

if __name__ == "__main__":
    stop_event = threading.Event()
    browser_thread = StoppableThread(target=start_browser, stop_event=stop_event)
    browser_thread.start()

    uvicorn.run(app, host=config.get("server_ip"), port=config.get("server_port"))

    browser_thread.stop()
    os._exit(0)
