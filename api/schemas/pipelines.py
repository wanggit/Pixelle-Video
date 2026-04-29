"""
API Schemas for Pipeline Endpoints

Request/Response schemas for CustomMedia, ImageToVideo, ActionTransfer, and DigitalHuman pipelines.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ==========================================
# Custom Media (Asset-Based) Pipeline
# ==========================================

class CustomMediaRequest(BaseModel):
    assets: list[str] = Field(..., description="List of uploaded asset file paths")
    video_title: Optional[str] = Field(None, description="Custom video title")
    intent: Optional[str] = Field(None, description="Creative intent or description")
    duration: int = Field(30, ge=15, le=120, description="Target duration in seconds")
    source: str = Field("runninghub", description="Workflow source: runninghub or selfhost")
    voice_id: Optional[str] = Field(None, description="TTS voice ID")
    tts_speed: float = Field(1.2, ge=0.5, le=2.0, description="TTS speed multiplier")
    bgm_path: Optional[str] = Field(None, description="Background music path")
    bgm_volume: float = Field(0.2, ge=0.0, le=1.0, description="BGM volume")


class CustomMediaAsyncResponse(BaseModel):
    success: bool
    message: str
    task_id: str


# ==========================================
# Image to Video Pipeline
# ==========================================

class ImageToVideoRequest(BaseModel):
    image: str = Field(..., description="Uploaded image file path")
    prompt: str = Field(..., description="Text prompt for video generation")
    workflow: str = Field(..., description="Workflow key (e.g., runninghub/i2v_basic.json)")
    source: str = Field("runninghub", description="Workflow source: runninghub or selfhost")


class ImageToVideoAsyncResponse(BaseModel):
    success: bool
    message: str
    task_id: str


# ==========================================
# Action Transfer Pipeline
# ==========================================

class ActionTransferRequest(BaseModel):
    video: str = Field(..., description="Reference video file path")
    image: str = Field(..., description="Target character image file path")
    prompt: str = Field(..., description="Text prompt")
    workflow: str = Field(..., description="Workflow key (e.g., runninghub/af_basic.json)")
    source: str = Field("runninghub", description="Workflow source: runninghub or selfhost")
    duration: int = Field(10, ge=1, le=30, description="Duration in seconds (extracted from video)")


class ActionTransferAsyncResponse(BaseModel):
    success: bool
    message: str
    task_id: str


# ==========================================
# Digital Human Pipeline
# ==========================================

class DigitalHumanRequest(BaseModel):
    character_assets: list[str] = Field(..., description="Character image file paths")
    goods_assets: Optional[list[str]] = Field(None, description="Product/goods image paths")
    goods_title: Optional[str] = Field(None, description="Product title")
    goods_text: str = Field(..., description="Script text for the digital human to speak")
    mode: str = Field("digital", description="Processing mode: digital or customize")
    workflow_path: dict[str, str] = Field(..., description="Workflow paths: first/second/third_workflow_path")
    tts_inference_mode: str = Field("local", description="TTS mode: local or comfyui")
    tts_voice: Optional[str] = Field(None, description="TTS voice ID for local mode")
    tts_speed: float = Field(1.0, ge=0.5, le=2.0, description="TTS speed multiplier")
    tts_workflow: Optional[str] = Field(None, description="TTS workflow key for ComfyUI mode")
    ref_audio: Optional[str] = Field(None, description="Reference audio for voice cloning")


class DigitalHumanAsyncResponse(BaseModel):
    success: bool
    message: str
    task_id: str
