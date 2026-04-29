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
Configuration schemas for API endpoints
"""

from typing import Optional
from pydantic import BaseModel, Field


class LLMConfigRequest(BaseModel):
    """Request to update LLM configuration"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


class ComfyUIConfigRequest(BaseModel):
    """Request to update ComfyUI configuration"""
    comfyui_url: Optional[str] = None
    comfyui_api_key: Optional[str] = None
    runninghub_api_key: Optional[str] = None
    runninghub_concurrent_limit: Optional[int] = Field(default=None, ge=1, le=10)
    runninghub_instance_type: Optional[str] = None


class LLMTestRequest(BaseModel):
    """Request to test LLM connection"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


class ComfyUITestRequest(BaseModel):
    """Request to test ComfyUI connection"""
    comfyui_url: Optional[str] = None
    comfyui_api_key: Optional[str] = None


class LLMTestResponse(BaseModel):
    """Response from LLM connection test"""
    success: bool
    message: str
    models: list[str] = Field(default_factory=list)


class ComfyUITestResponse(BaseModel):
    """Response from ComfyUI connection test"""
    success: bool
    message: str
    system_stats: Optional[dict] = None


class ConfigResponse(BaseModel):
    """Current configuration (sanitized)"""
    llm: dict
    comfyui: dict
    template: dict


class SaveConfigResponse(BaseModel):
    """Response from config save"""
    success: bool
    message: str


class LLMModelsResponse(BaseModel):
    """Available LLM models"""
    success: bool
    models: list[str] = Field(default_factory=list)
