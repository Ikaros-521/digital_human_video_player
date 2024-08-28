from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
    
class ShowMessage(BaseModel):
    type: str
    video_path: str
    audio_path: str
    insert_index: int
    move_file: Optional[bool] = Field(None)
    
class GetNonDefaultVideoCountResult(BaseModel):
    code: int
    message: str
    count: int

class GetVideoQueueResult(BaseModel):
    code: int
    data: list
    message: str
    

"""
通用
""" 
class CommonResult(BaseModel):
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None
