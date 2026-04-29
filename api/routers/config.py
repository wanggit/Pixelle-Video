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
Configuration Management Router

API endpoints for managing LLM and ComfyUI configuration.
"""

import asyncio
import httpx
from fastapi import APIRouter, HTTPException
from loguru import logger
from openai import AsyncOpenAI

from api.schemas.config import (
    LLMConfigRequest,
    ComfyUIConfigRequest,
    LLMTestRequest,
    ComfyUITestRequest,
    LLMTestResponse,
    ComfyUITestResponse,
    ConfigResponse,
    SaveConfigResponse,
    LLMModelsResponse,
)
from api.dependencies import PixelleVideoDep

router = APIRouter(tags=["Configuration"])


def _mask_secret(value: str) -> str:
    """Mask sensitive config values"""
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return value[:4] + "****" + value[-4:]


@router.get("/api/config", response_model=ConfigResponse)
async def get_config(pixelle_video: PixelleVideoDep):
    """Get current configuration (secrets masked)"""
    try:
        from pixelle_video.config import config_manager
        config_manager.reload()

        llm_config = config_manager.get_llm_config()
        comfyui_config = config_manager.get_comfyui_config()
        template_config = {"default_template": config_manager.config.template.default_template}

        # Mask secrets
        if llm_config.get("api_key"):
            llm_config["api_key"] = _mask_secret(llm_config["api_key"])
        if comfyui_config.get("comfyui_api_key"):
            comfyui_config["comfyui_api_key"] = _mask_secret(comfyui_config["comfyui_api_key"])
        if comfyui_config.get("runninghub_api_key"):
            comfyui_config["runninghub_api_key"] = _mask_secret(comfyui_config["runninghub_api_key"])

        return ConfigResponse(
            llm=llm_config,
            comfyui=comfyui_config,
            template=template_config,
        )
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/config/llm", response_model=SaveConfigResponse)
async def save_llm_config(request: LLMConfigRequest, pixelle_video: PixelleVideoDep):
    """Save LLM configuration"""
    try:
        from pixelle_video.config import config_manager

        config_manager.set_llm_config(
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.model,
        )
        config_manager.save()

        return SaveConfigResponse(success=True, message="LLM configuration saved")
    except Exception as e:
        logger.error(f"Failed to save LLM config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/config/comfyui", response_model=SaveConfigResponse)
async def save_comfyui_config(request: ComfyUIConfigRequest, pixelle_video: PixelleVideoDep):
    """Save ComfyUI configuration"""
    try:
        from pixelle_video.config import config_manager

        config_manager.set_comfyui_config(
            comfyui_url=request.comfyui_url,
            comfyui_api_key=request.comfyui_api_key,
            runninghub_api_key=request.runninghub_api_key,
            runninghub_concurrent_limit=request.runninghub_concurrent_limit,
            runninghub_instance_type=request.runninghub_instance_type,
        )
        config_manager.save()

        return SaveConfigResponse(success=True, message="ComfyUI configuration saved")
    except Exception as e:
        logger.error(f"Failed to save ComfyUI config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/config/reset", response_model=SaveConfigResponse)
async def reset_config(pixelle_video: PixelleVideoDep):
    """Reset configuration to defaults"""
    try:
        from pixelle_video.config import config_manager, load_config_dict
        import yaml

        # Load example config as defaults
        example_path = "config.example.yaml"
        defaults = load_config_dict(example_path)
        if defaults:
            config_manager.update(defaults)
            config_manager.save()
            return SaveConfigResponse(success=True, message="Configuration reset to defaults")
        else:
            raise HTTPException(status_code=404, detail="config.example.yaml not found")
    except Exception as e:
        logger.error(f"Failed to reset config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/llm/test-connection", response_model=LLMTestResponse)
async def test_llm_connection(request: LLMTestRequest, pixelle_video: PixelleVideoDep):
    """Test LLM connectivity and list available models"""
    from pixelle_video.config import config_manager

    api_key = request.api_key or config_manager.config.llm.api_key
    base_url = request.base_url or config_manager.config.llm.base_url
    model = request.model or config_manager.config.llm.model or "gpt-3.5-turbo"

    try:
        client = AsyncOpenAI(api_key=api_key or "dummy-key", base_url=base_url or None)

        # Test with a simple chat request
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10,
        )

        # Try to list available models
        models = []
        try:
            models_response = await client.models.list()
            models = [m.id for m in models_response.data][:20]
        except Exception:
            models = [model]

        return LLMTestResponse(
            success=True,
            message=f"Connection successful. Model: {model}",
            models=models,
        )
    except Exception as e:
        logger.error(f"LLM connection test failed: {e}")
        return LLMTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}",
            models=[],
        )


@router.get("/api/llm/models", response_model=LLMModelsResponse)
async def list_llm_models(pixelle_video: PixelleVideoDep):
    """List available LLM models from configured provider"""
    from pixelle_video.config import config_manager

    api_key = config_manager.config.llm.api_key
    base_url = config_manager.config.llm.base_url

    try:
        client = AsyncOpenAI(api_key=api_key or "dummy-key", base_url=base_url or None)
        models_response = await client.models.list()
        models = [m.id for m in models_response.data]
        return LLMModelsResponse(success=True, models=models)
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return LLMModelsResponse(success=False, models=[])


@router.post("/api/comfyui/test-connection", response_model=ComfyUITestResponse)
async def test_comfyui_connection(request: ComfyUITestRequest, pixelle_video: PixelleVideoDep):
    """Test ComfyUI connectivity"""
    from pixelle_video.config import config_manager

    url = request.comfyui_url or config_manager.config.comfyui.comfyui_url

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{url}/system_stats")
            response.raise_for_status()
            stats = response.json()

        return ComfyUITestResponse(
            success=True,
            message=f"ComfyUI connection successful at {url}",
            system_stats=stats.get("system", {}),
        )
    except Exception as e:
        logger.error(f"ComfyUI connection test failed: {e}")
        return ComfyUITestResponse(
            success=False,
            message=f"Connection failed: {str(e)}",
            system_stats=None,
        )
