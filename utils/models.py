from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
    
class ShowMessage(BaseModel):
    type: str
    video_path: str
    audio_path: str
    captions_printer: Optional[dict] = Field(None)
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
    
class SetConfigMessage(BaseModel):
    captions_printer_api_url: Optional[str] = Field(None)

"""
通用
""" 
class CommonResult(BaseModel):
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None
