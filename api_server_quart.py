from quart import Quart, websocket, redirect, url_for, jsonify, request, send_from_directory 
import asyncio, threading, time, os
import json, logging, traceback
from selenium import webdriver
import re

from utils.config import Config
from utils.common import Common
from utils.logger import Configure_logger
from utils.video_generate import get_video

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

print(f"static_folder={static_folder}")

app = Quart(__name__, static_folder=static_folder)
connected_websockets = set()

# 队列中非默认视频个数
non_default_video_count = 0



@app.route('/')
async def home():
    return redirect(url_for('static', filename='index.html'))

@app.route('/videos/<path:filename>')
async def load_video(filename):
    video_path = os.path.join(app.static_folder, 'video', filename)
    return await send_from_directory(os.path.dirname(video_path), os.path.basename(video_path))


@app.websocket('/ws')
async def ws():
    global non_default_video_count

    connected_websockets.add(websocket._get_current_object())
    try:
        while True:
            try:
                data = await websocket.receive()
                data_json = json.loads(data)
                logging.info(f"收到客户端数据: {data_json}")
                # 处理从客户端接收的数据的逻辑
                if data_json['type'] == "videoEnded":
                    non_default_video_count = data_json['count']
                    # 跳过默认视频
                    if common.get_filename_with_ext(config.get("default_video")) not in data_json['video_path']:
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
            except Exception as e:
                logging.error(traceback.format_exc())
    finally:
        connected_websockets.remove(websocket)


# 删除视频文件
async def delete_video_file(video_path: str):
    from urllib.parse import unquote

    # 根据你的逻辑来获取要删除的视频文件路径
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
        await ws.send(data)

def extract_filename(video_path):
    if '=' in video_path:
        filepath = video_path.split('=')[1]
    else:
        filepath = video_path

    match = re.search(r'[^\\/:*?"<>|\r\n]+$', filepath)
    if match:
        return match.group()
    else:
        return common.get_filename_with_ext(filepath)

@app.route('/show', methods=['POST'])
async def show():
    try:
        data = await request.get_json()

        logging.info(f"收到数据：{data}")

        video_path = await get_video(data["type"], data, config)

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
                    ret = common.move_and_rename(video_path, static_video_path, new_filename=filename)
                else:
                    ret = common.move_and_rename(video_path, static_video_path)
                    filename = common.get_filename_with_ext(video_path)
            if ret == False:
                return jsonify({"code": 200, "message": "视频移动失败"})

            file_url = f"http://127.0.0.1:{config.get('server_port')}/static/videos/{filename}"

            if "audio_path" not in data:
                data["audio_path"] = None

            if "insert_index" not in data:
                data["insert_index"] = -1

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

            return jsonify({"code": 200, "message": "操作成功"})
        
        return jsonify({"code": 200, "message": "视频合成失败"})
    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({"code": -1, "message": f"操作失败: {str(e)}"})


# 停止当前播放的视频，跳转到下一个
@app.route('/stop_current_video', methods=['POST'])
async def stop_current_video():
    try:
        #data = await request.get_json()

        #logging.info(f"收到数据：{data}")

        await send_to_all_websockets(
            json.dumps(
                {
                    "type": "stop_current_video"
                }
            )
        )

        return jsonify({"code": 200, "message": "操作成功"})
    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({"code": -1, "message": f"操作失败: {str(e)}"})

# 获取非默认视频个数
@app.route('/get_non_default_video_count', methods=['POST'])
async def get_non_default_video_count():
    try:
        await send_to_all_websockets(
            json.dumps(
                {
                    "type": "get_non_default_video_count"
                }
            )
        )
        # 等待ws返回后对数据的更新
        await asyncio.sleep(0.5)
        return jsonify({"code": 200, "count": non_default_video_count, "message": "操作成功"})
    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({"code": -1, "message": f"操作失败: {str(e)}"})

async def main():
    # 使用 Quart 提供的 run_task 方法来启动异步的 Web 应用
    await app.run_task(host=config.get("server_ip"), port=config.get("server_port"))


class StoppableThread(threading.Thread):
    def __init__(self, target=None, stop_event=None):
        super().__init__()
        self._stop_event = stop_event
        self._target = target  # 保存目标函数引用

    def run(self):
        if self._target:  # 如果有目标函数，调用它
            self._target(self._stop_event)
        self._stop_event.wait()  # 等待事件被设置
        logging.info("Thread is stopping")

    def stop(self):
        self._stop_event.set()

if __name__ == '__main__':
    def start_browser(stop_event):
        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被浏览器识别为自动化程序
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--autoplay-policy=no-user-gesture-required')

        # 使用`options`而不是`chrome_options`作为参数
        driver = webdriver.Chrome(options=options)
        driver.get(f'http://127.0.0.1:{config.get("server_port")}')

        stop_event.wait()  # 等待事件被设置

    # 创建一个停止事件实例
    stop_event = threading.Event()

    # 创建一个可停止的线程实例
    browser_thread = StoppableThread(target=start_browser, stop_event=stop_event)

    # 启动线程
    browser_thread.start()

    asyncio.run(main())

    # 在某个时刻停止线程
    # browser_thread.stop()

    os._exit(0)
