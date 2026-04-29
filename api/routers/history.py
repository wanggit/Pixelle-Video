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
History Management Router

API endpoints for managing generation history (persistent tasks).
Wraps HistoryManager which uses PersistenceService (filesystem-based).
"""

import os
import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from api.schemas.history import (
    HistoryTaskSummary,
    HistoryListResponse,
    HistoryTaskDetail,
    HistoryStatisticsResponse,
    DuplicateTaskResponse,
    DeleteTaskResponse,
)
from api.dependencies import PixelleVideoDep

router = APIRouter(tags=["History"])


def _task_summary_from_metadata(task_id: str, metadata: dict) -> HistoryTaskSummary:
    """Convert metadata dict to HistoryTaskSummary"""
    input_data = metadata.get("input", {})
    result = metadata.get("result", {})

    # Build thumbnail URL from frames
    thumbnail = None
    frames = metadata.get("frames", [])
    if frames:
        first_frame = frames[0] if isinstance(frames, list) else None
        if first_frame and isinstance(first_frame, dict):
            thumbnail = first_frame.get("image_path")

    return HistoryTaskSummary(
        task_id=task_id,
        title=metadata.get("title", input_data.get("title", "Untitled")),
        created_at=metadata.get("created_at", ""),
        completed_at=metadata.get("completed_at"),
        status=metadata.get("status", "unknown"),
        thumbnail=thumbnail,
        duration=result.get("duration"),
        file_size=result.get("file_size"),
        n_frames=result.get("n_frames"),
    )


@router.get("/api/history/tasks", response_model=HistoryListResponse)
async def list_history_tasks(
    pixelle_video: PixelleVideoDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str = Query(None, description="Filter by status (completed/failed)"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
):
    """List history tasks with pagination, filtering, and sorting"""
    try:
        result = await pixelle_video.history.get_task_list(
            page=page,
            page_size=page_size,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        tasks = []
        for task_data in result.get("tasks", []):
            task_id = task_data.get("task_id", task_data.get("id", ""))
            summary = _task_summary_from_metadata(task_id, task_data)
            tasks.append(summary)

        return HistoryListResponse(
            tasks=tasks,
            total=result.get("total", 0),
            page=result.get("page", page),
            page_size=result.get("page_size", page_size),
            total_pages=result.get("total_pages", 1),
        )
    except Exception as e:
        logger.error(f"Failed to list history tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/history/tasks/{task_id}", response_model=HistoryTaskDetail)
async def get_history_task_detail(task_id: str, pixelle_video: PixelleVideoDep):
    """Get detailed information about a specific history task"""
    try:
        detail = await pixelle_video.history.get_task_detail(task_id)
        if not detail:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        metadata = detail.get("metadata", {})
        storyboard = detail.get("storyboard")

        input_data = metadata.get("input", {})
        result = metadata.get("result", {})

        # Build video URL
        video_path = result.get("video_path")
        video_url = None
        if video_path and Path(video_path).exists():
            video_url = f"/api/files/{video_path}"

        return HistoryTaskDetail(
            task_id=task_id,
            title=metadata.get("title", input_data.get("title", "Untitled")),
            created_at=metadata.get("created_at", ""),
            completed_at=metadata.get("completed_at"),
            status=metadata.get("status", "unknown"),
            duration=result.get("duration"),
            file_size=result.get("file_size"),
            n_frames=result.get("n_frames"),
            video_url=video_url,
            input_params=input_data,
            storyboard=storyboard,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task detail for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/history/tasks/{task_id}", response_model=DeleteTaskResponse)
async def delete_history_task(task_id: str, pixelle_video: PixelleVideoDep):
    """Delete a history task and its associated files"""
    try:
        success = await pixelle_video.history.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return DeleteTaskResponse(success=True, message=f"Task {task_id} deleted")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/history/tasks/{task_id}/duplicate", response_model=DuplicateTaskResponse)
async def duplicate_history_task(task_id: str, pixelle_video: PixelleVideoDep):
    """Duplicate a history task's input parameters for re-generation"""
    try:
        input_params = await pixelle_video.history.duplicate_task(task_id)
        if not input_params:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return DuplicateTaskResponse(
            success=True,
            message=f"Input parameters extracted from task {task_id}",
            input_params=input_params,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to duplicate task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/history/statistics", response_model=HistoryStatisticsResponse)
async def get_history_statistics(pixelle_video: PixelleVideoDep):
    """Get aggregate statistics for all history tasks"""
    try:
        stats = await pixelle_video.history.get_statistics()
        return HistoryStatisticsResponse(
            total_tasks=stats.get("total_tasks", 0),
            completed=stats.get("completed", 0),
            failed=stats.get("failed", 0),
            total_duration=stats.get("total_duration", 0),
            total_size=stats.get("total_size", 0),
        )
    except Exception as e:
        logger.error(f"Failed to get history statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
