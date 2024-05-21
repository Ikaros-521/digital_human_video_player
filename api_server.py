from quart import Quart, websocket, redirect, url_for, jsonify, request, send_from_directory 
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


def get_video(type: str, data: dict):
    from gradio_client import Client

    try:
        if type == "easy_wav2lip":
            client = Client(config.get("easy_wav2lip", "api_ip_port"))
            result = client.predict(
                config.get("easy_wav2lip", "video_file"),	# filepath  in '支持图片、视频格式' File component
                data['audio_path'],	# filepath  in '支持mp3、wav格式' Audio component
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
        elif type == "sadtalker":
            client = Client(config.get("sadtalker", "api_ip_port"))

            if config.get("sadtalker", "gradio_api_type") == "api_name":
                result = client.predict(
                    config.get("sadtalker", "img_file"),	# filepath  in 'Source image' Image component
                    data['audio_path'],	# filepath  in 'Input audio' Audio component
                    config.get("sadtalker", "preprocess"),	# Literal[crop, resize, full, extcrop, extfull]  in 'preprocess' Radio component
                    config.get("sadtalker", "still_mode"),	# bool  in 'Still Mode (fewer head motion, works with preprocess `full`)' Checkbox component
                    config.get("sadtalker", "GFPGAN"),	# bool  in 'GFPGAN as Face enhancer' Checkbox component
                    config.get("sadtalker", "batch_size"),	# float (numeric value between 0 and 10) in 'batch size in generation' Slider component
                    config.get("sadtalker", "face_model_resolution"),	# Literal[256, 512]  in 'face model resolution' Radio component
                    config.get("sadtalker", "pose_style"),	# float (numeric value between 0 and 46) in 'Pose style' Slider component
                    api_name="/test"
                )

                logging.info(f'{type}合成成功，生成在：{result["video"]}')

                return result["video"]
            else:
                result = client.predict(
                    config.get("sadtalker", "img_file"),	# filepath  in 'Source image' Image component
                    data['audio_path'],	# filepath  in 'Input audio' Audio component
                    config.get("sadtalker", "preprocess"),	# Literal[crop, resize, full, extcrop, extfull]  in 'preprocess' Radio component
                    config.get("sadtalker", "still_mode"),	# bool  in 'Still Mode (fewer head motion, works with preprocess `full`)' Checkbox component
                    config.get("sadtalker", "GFPGAN"),	# bool  in 'GFPGAN as Face enhancer' Checkbox component
                    config.get("sadtalker", "batch_size"),	# float (numeric value between 0 and 10) in 'batch size in generation' Slider component
                    config.get("sadtalker", "face_model_resolution"),	# Literal[256, 512]  in 'face model resolution' Radio component
                    config.get("sadtalker", "pose_style"),	# float (numeric value between 0 and 46) in 'Pose style' Slider component
                    fn_index=1
                )

                logging.info(f'{type}合成成功，生成在：{result}')

                return result
        elif type == "genefaceplusplus":
            client = Client(config.get("genefaceplusplus", "api_ip_port"))
            result = client.predict(
                data['audio_path'],	# filepath  in 'Input audio (required)' Audio component
                config.get("genefaceplusplus", "blink_mode"),	# Literal['none', 'period']  in '眨眼模式' Radio component
                config.get("genefaceplusplus", "temperature"),	# float (numeric value between 0.0 and 1.0) in 'temperature' Slider component
                config.get("genefaceplusplus", "lle_percent"),	# float (numeric value between 0.0 and 1.0) in 'lle_percent' Slider component
                config.get("genefaceplusplus", "mouth_amplitude"),	# float (numeric value between 0.0 and 1.0) in '嘴部幅度' Slider component
                config.get("genefaceplusplus", "ray_marching_end_threshold"),	# float (numeric value between 0.0 and 0.1) in 'ray marching end-threshold' Slider component
                config.get("genefaceplusplus", "fp16"),	# bool  in 'fp16模式：是否使用并加速推理' Checkbox component
                config.get("genefaceplusplus", "audio2secc_model"),	# List[List[str]]  in 'audio2secc model ckpt path or directory' Fileexplorer component
                config.get("genefaceplusplus", "pose_net_model"),	# List[List[str]]  in '(optional) pose net model ckpt path or directory' Fileexplorer component
                config.get("genefaceplusplus", "head_model"),	# List[List[str]]  in '(按需) 选择人物头部模型(如果选择了躯干模型，该选项将被忽略)' Fileexplorer component
                config.get("genefaceplusplus", "body_model"),	# List[List[str]]  in '选择人物躯干模型' Fileexplorer component
                config.get("genefaceplusplus", "low_memory_mode"),	# bool  in '低内存使用模式：以较低的推理速度为代价节省内存。在运行长音频合成视频时很有用。' Checkbox component
                api_name="/infer_once_args"
            )

            logging.info(f'{type}合成成功，生成在：{result[0]["video"]}')

            return result[0]["video"]
        elif type == "musetalk":
            # gradio_client-0.16.3
            from gradio_client import file

            client = Client(config.get("musetalk", "api_ip_port"))
            result = client.predict(
                audio_path=file(data['audio_path']),
                video_path={"video":file(config.get("musetalk", "video_path"))},
                bbox_shift=int(config.get("musetalk", "bbox_shift")),
                api_name="/inference"
            )

            logging.info(f'{type}合成成功，生成在：{result[0]["video"]}')

            return result[0]["video"]
        elif type == "local":
            return data['video_path']
    except Exception as e:
        logging.error(traceback.format_exc())
        return None


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


@app.route('/show', methods=['POST'])
async def show():
    try:
        data = await request.get_json()

        logging.info(f"收到数据：{data}")

        video_path = get_video(data["type"], data)

        if video_path:
            static_video_path = os.path.join(static_folder, "videos")
            logging.debug(f"视频文件移动到的路径：{static_video_path}")
            if "move_file" in data:
                ret = common.move_and_rename(video_path, static_video_path, move_file=data["move_file"])
            else:
                ret = common.move_and_rename(video_path, static_video_path)
            if ret == False:
                return jsonify({"code": 200, "message": "视频移动失败"})

            filename = common.get_filename_with_ext(video_path)
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
    browser_thread.stop()

    os._exit(0)
