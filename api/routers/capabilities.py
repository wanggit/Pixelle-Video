# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Service Capabilities Discovery Router

Reports which services are configured and available.
"""

from fastapi import APIRouter
from loguru import logger

from api.dependencies import PixelleVideoDep

router = APIRouter(tags=["Capabilities"])


@router.get("/api/capabilities")
async def get_capabilities(pixelle_video: PixelleVideoDep):
    """
    Report service capabilities - which services are configured and available.
    """
    from pixelle_video.config import config_manager

    llm_config = config_manager.config.llm
    comfyui_config = config_manager.config.comfyui

    capabilities = {
        "llm": {
            "configured": llm_config.is_llm_configured(),
            "model": llm_config.model,
            "base_url": llm_config.base_url,
        },
        "comfyui": {
            "local_url": comfyui_config.comfyui_url,
            "runninghub_enabled": bool(comfyui_config.runninghub_api_key),
            "workflows": {
                "tts": comfyui_config.tts.available,
                "image": comfyui_config.image.available if hasattr(comfyui_config.image, 'available') else True,
                "video": comfyui_config.video.available if hasattr(comfyui_config.video, 'available') else True,
            },
        },
        "edge_tts": {
            "enabled": comfyui_config.tts.inference_mode == "local",
            "default_voice": comfyui_config.tts.local.voice,
            "default_speed": comfyui_config.tts.local.speed,
        },
        "pipelines": {
            "standard": True,
            "asset_based": True,
            "digital_human": True,
            "image_to_video": True,
            "action_transfer": True,
        },
    }

    return capabilities
