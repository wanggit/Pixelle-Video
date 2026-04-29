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
History management schemas for API endpoints
"""

from typing import Optional
from pydantic import BaseModel, Field


class HistoryTaskSummary(BaseModel):
    """Summary of a history task for list view"""
    task_id: str
    title: str
    created_at: str
    completed_at: Optional[str] = None
    status: str
    thumbnail: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    n_frames: Optional[int] = None


class HistoryListResponse(BaseModel):
    """Paginated history list response"""
    tasks: list[HistoryTaskSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class HistoryTaskDetail(BaseModel):
    """Full task detail including storyboard"""
    task_id: str
    title: str
    created_at: str
    completed_at: Optional[str] = None
    status: str
    duration: Optional[float] = None
    file_size: Optional[int] = None
    n_frames: Optional[int] = None
    video_url: Optional[str] = None
    input_params: Optional[dict] = None
    storyboard: Optional[dict] = None


class HistoryStatisticsResponse(BaseModel):
    """History statistics"""
    total_tasks: int
    completed: int
    failed: int
    total_duration: float
    total_size: int


class DuplicateTaskResponse(BaseModel):
    """Response from task duplication"""
    success: bool
    message: str
    input_params: Optional[dict] = None


class DeleteTaskResponse(BaseModel):
    """Response from task deletion"""
    success: bool
    message: str
