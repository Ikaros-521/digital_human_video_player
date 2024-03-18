from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
		"C:\\Users\\Administrator\\Pictures\\test\\2.mp3",	# filepath  in 'Input audio (required)' Audio component
		"period",	# Literal['none', 'period']  in '眨眼模式' Radio component
		0,	# float (numeric value between 0.0 and 1.0) in 'temperature' Slider component
		0,	# float (numeric value between 0.0 and 1.0) in 'lle_percent' Slider component
		0.4,	# float (numeric value between 0.0 and 1.0) in '嘴部幅度' Slider component
		0.01,	# float (numeric value between 0.0 and 0.1) in 'ray marching end-threshold' Slider component
		False,	# bool  in 'fp16模式：是否使用并加速推理' Checkbox component
		[["checkpoints", "audio2motion_vae", "model_ckpt_steps_400000.ckpt"]],	# List[List[str]]  in 'audio2secc model ckpt path or directory' Fileexplorer component
		[],	# List[List[str]]  in '(optional) pose net model ckpt path or directory' Fileexplorer component
		[],	# List[List[str]]  in '(按需) 选择人物头部模型(如果选择了躯干模型，该选项将被忽略)' Fileexplorer component
		[["checkpoints", "motion2video_nerf", "May_torso", "model_ckpt_steps_250000.ckpt"]],	# List[List[str]]  in '选择人物躯干模型' Fileexplorer component
		False,	# bool  in '低内存使用模式：以较低的推理速度为代价节省内存。在运行长音频合成视频时很有用。' Checkbox component
		api_name="/infer_once_args"
)
print(result)