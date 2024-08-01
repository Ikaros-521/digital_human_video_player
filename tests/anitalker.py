# gradio_client==1.2.0
from gradio_client import Client, handle_file

client = Client("http://127.0.0.1:7860/")
result = client.predict(
    face=handle_file('C:\\Users\\Administrator\\Pictures\\test\\1.png'),
    audio=handle_file('C:\\Users\\Administrator\\Pictures\\test\\2.mp3'),
    is_mor=False,
    face_d="0",
    api_name="/do_cloth"
)
print(result["video"])