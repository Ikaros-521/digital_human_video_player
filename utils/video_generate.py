import logging, traceback, asyncio
from concurrent.futures import ThreadPoolExecutor

# 线程池
executor = ThreadPoolExecutor(max_workers=10)

def get_video(type: str, data: dict, config: dict):
    from gradio_client import Client
    import gradio_client

    try:
        if type == "easy_wav2lip":
            client = Client(config.get("easy_wav2lip", "api_ip_port"))
            result = client.predict(
                gradio_client.file(config.get("easy_wav2lip", "video_file")),	# filepath  in '支持图片、视频格式' File component
                gradio_client.file(data['audio_path']),	# filepath  in '支持mp3、wav格式' Audio component
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
        elif type == "anitalker":
            # gradio_client-1.2.0
            from gradio_client import handle_file

            client = Client(config.get("anitalker", "api_ip_port"))
            result = client.predict(
                face=handle_file(config.get("anitalker", "img_file")), # 图片路径，1:1像素比
                audio=handle_file(data['audio_path']),
                is_mor=config.get("anitalker", "is_mor"), # 视频超分，0为关闭，1为开启
                face_d=config.get("anitalker", "face_d"), # 面部朝向,0为正面,0.25为侧面
                api_name="/do_cloth"
            )

            logging.info(f'{type}合成成功，生成在：{result["video"]}')

            return result["video"]
        elif type == "local":
            return data['video_path']
    except Exception as e:
        logging.error(traceback.format_exc())
        return None


async def run_get_video(type: str, data: dict, config: dict) -> str:
    # 将同步请求委托给线程池执行，从而避免阻塞事件循环
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, get_video, type, data, config)
    return result
