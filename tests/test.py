from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
		"C:\\Users\\Administrator\\Pictures\\test\\1.png",	# filepath  in '支持图片、视频格式' File component
		"C:\\Users\\Administrator\\Pictures\\test\\2.mp3",	# filepath  in '支持mp3、wav格式' Audio component
		"Enhanced",	# Literal['Fast', 'Improved', 'Enhanced', 'Experimental']  in '视频质量选项' Radio component
		"full resolution",	# Literal['full resolution', 'half resolution']  in '分辨率选项' Radio component
		"Wav2Lip",	# Literal['Wav2Lip', 'Wav2Lip_GAN']  in 'Wav2Lip版本选项' Radio component
		"True",	# Literal['True', 'False']  in '启用追踪旧数据' Radio component
		"True",	# Literal['True', 'False']  in '启用脸部平滑' Radio component
		0,	# float (numeric value between -100 and 100) in '嘴部mask上边缘' Slider component
		10,	# float (numeric value between -100 and 100) in '嘴部mask下边缘' Slider component
		20,	# float (numeric value between -100 and 100) in '嘴部mask左边缘' Slider component
		0,	# float (numeric value between -100 and 100) in '嘴部mask右边缘' Slider component
		2.05,	# float (numeric value between -10 and 10) in 'mask尺寸' Slider component
		5,	# float (numeric value between -100 and 100) in 'mask羽化' Slider component
		"True",	# Literal['True', 'False']  in '启用mask嘴部跟踪' Radio component
		"False",	# Literal['True', 'False']  in '启用mask调试' Radio component
		"False",	# Literal['False']  in '批量处理多个视频' Radio component
		api_name="/execute_pipeline"
)
print(result)