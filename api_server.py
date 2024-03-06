from quart import Quart, websocket, redirect, url_for, jsonify, request  
import asyncio, threading, time, os
import json, logging, traceback
from selenium import webdriver

from utils.config import Config
from utils.common import Common
from utils.logger import Configure_logger


common = Common()
# 日志文件路径
file_path = "./log/log-" + common.get_bj_time(1) + ".txt"
Configure_logger(file_path)
config = Config("config.json")


app = Quart(__name__, static_folder='./static')
connected_websockets = set()

def get_video(audio_path: str):
    from gradio_client import Client

    try:
        client = Client("http://127.0.0.1:7860/")
        result = client.predict(
            config.get("easy_wav2lip", "video_file"),	# filepath  in '支持图片、视频格式' File component
            audio_path,	# filepath  in '支持mp3、wav格式' Audio component
            config.get("easy_wav2lip", "quality"),	# Literal['Fast', 'Improved', 'Enhanced', 'Experimental']  in '视频质量选项' Radio component
            config.get("easy_wav2lip", "output_height"),	# Literal['full resolution', 'half resolution']  in '分辨率选项' Radio component
            config.get("easy_wav2lip", "wav2lip_version"),	# Literal['Wav2Lip', 'Wav2Lip_GAN']  in 'Wav2Lip版本选项' Radio component
            config.get("easy_wav2lip", "use_previous_tracking_data"),	# Literal['True', 'False']  in '启用追踪旧数据' Radio component
            config.get("easy_wav2lip", "nosmooth"),	# Literal['True', 'False']  in '启用脸部平滑' Radio component
            config.get("easy_wav2lip", "u"),	# float (numeric value between -100 and 100) in '嘴部mask上边缘' Slider component
            config.get("easy_wav2lip", "d"),	# float (numeric value between -100 and 100) in '嘴部mask下边缘' Slider component
            config.get("easy_wav2lip", "l"),	# float (numeric value between -100 and 100) in '嘴部mask左边缘' Slider component
            config.get("easy_wav2lip", "r"),	# float (numeric value between -100 and 100) in '嘴部mask右边缘' Slider component
            config.get("easy_wav2lip", "size"),	# float (numeric value between -10 and 10) in 'mask尺寸' Slider component
            config.get("easy_wav2lip", "feathering"),	# float (numeric value between -100 and 100) in 'mask羽化' Slider component
            config.get("easy_wav2lip", "mouth_tracking"),	# Literal['True', 'False']  in '启用mask嘴部跟踪' Radio component
            config.get("easy_wav2lip", "debug_mask"),	# Literal['True', 'False']  in '启用mask调试' Radio component
            config.get("easy_wav2lip", "batch_process"),	# Literal['False']  in '批量处理多个视频' Radio component
            api_name="/execute_pipeline"
        )

        logging.info(f'合成成功，生成在：{result[0]["video"]}')

        return result[0]["video"]
    except Exception as e:
        logging.error(traceback.format_exc())
        return None

@app.route('/')
async def home():
    return redirect(url_for('static', filename='index.html'))

@app.websocket('/ws')
async def ws():
    connected_websockets.add(websocket._get_current_object())
    try:
        while True:
            data = await websocket.receive()
            print(f"Received message from client: {data}")
            # 在这里添加处理从客户端接收的数据的逻辑
    finally:
        connected_websockets.remove(websocket._get_current_object())

async def send_to_all_websockets(data):
    for ws in connected_websockets:
        await ws.send(data)

@app.route('/show', methods=['POST'])
async def show():
    try:
        data = await request.get_json()

        logging.info(f"收到数据：{data}")

        video_path = get_video(data["audio_path"])

        if video_path:
            common.move_and_rename(video_path, "static/videos")
            filename = common.get_filename_with_ext(video_path)
            file_url = f"http://127.0.0.1:8091/static/videos/{filename}"

            await send_to_all_websockets(json.dumps({"type": "show", "video_path": file_url}))

        return jsonify({"code": 200, "message": "操作成功"})
    except Exception as e:
        return jsonify({"code": -1, "message": f"操作失败: {str(e)}"})

async def main():
    # 使用 Quart 提供的 run_task 方法来启动异步的 Web 应用
    await app.run_task(host="127.0.0.1", port=8091)


class StoppableThread(threading.Thread):
    def __init__(self, target=None):
        super().__init__()
        self._stop_event = threading.Event()
        self._target = target  # 保存目标函数引用

    def run(self):
        if self._target:  # 如果有目标函数，调用它
            self._target()
        while not self._stop_event.is_set():
            logging.info("Thread is running")
            time.sleep(1)
        logging.info("Thread is stopping")

    def stop(self):
        self._stop_event.set()

if __name__ == '__main__':
    def start_browser():
        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被浏览器识别为自动化程序
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--autoplay-policy=no-user-gesture-required')

        # 使用`options`而不是`chrome_options`作为参数
        driver = webdriver.Chrome(options=options)
        driver.get('http://127.0.0.1:8091')

        while True:
            time.sleep(1)  # 简单的循环等待，避免CPU占用过高

    # 创建一个可停止的线程实例
    browser_thread = StoppableThread(target=start_browser)

    # 启动线程
    browser_thread.start()

    asyncio.run(main())

    # 在某个时刻停止线程
    browser_thread.stop()

    os._exit(0)
