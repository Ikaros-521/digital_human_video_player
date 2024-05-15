# gradio_client-0.16.3
from gradio_client import Client, file

client = Client("http://127.0.0.1:7860/")
result = client.predict(
    audio_path=file('F:\\MuseTalk\\data\\audio\\yongen.wav'),
    video_path={"video":file('F:\\MuseTalk\data\\video\\yongen.mp4')},
    bbox_shift=0,
    api_name="/inference"
)
print(result)