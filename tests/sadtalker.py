from gradio_client import Client

#client = Client("http://127.0.0.1:7860/")
# result = client.predict(
# 		"C:\\Users\\Administrator\\Pictures\\test\\1.png",	# filepath  in 'Source image' Image component
# 		"C:\\Users\\Administrator\\Pictures\\test\\2.mp3",	# filepath  in 'Input audio' Audio component
# 		"crop",	# Literal[crop, resize, full, extcrop, extfull]  in 'preprocess' Radio component
# 		True,	# bool  in 'Still Mode (fewer head motion, works with preprocess `full`)' Checkbox component
# 		True,	# bool  in 'GFPGAN as Face enhancer' Checkbox component
# 		2,	# float (numeric value between 0 and 10) in 'batch size in generation' Slider component
# 		256,	# Literal[256, 512]  in 'face model resolution' Radio component
# 		0,	# float (numeric value between 0 and 46) in 'Pose style' Slider component
# 		api_name="/test"
# )

client = Client("https://--.westc.gpuhub.com:8443/")
result = client.predict(
		"C:\\Users\\Administrator\\Pictures\\test\\1.png",	# filepath  in 'Source image' Image component
		"C:\\Users\\Administrator\\Pictures\\test\\2.mp3",	# filepath  in 'Input audio' Audio component
		"crop",	# Literal[crop, resize, full, extcrop, extfull]  in 'preprocess' Radio component
		True,	# bool  in 'Still Mode (fewer head motion, works with preprocess `full`)' Checkbox component
		True,	# bool  in 'GFPGAN as Face enhancer' Checkbox component
		2,	# float (numeric value between 0 and 10) in 'batch size in generation' Slider component
		256,	# Literal[256, 512]  in 'face model resolution' Radio component
		0,	# float (numeric value between 0 and 46) in 'Pose style' Slider component
		fn_index=1
)
print(result)