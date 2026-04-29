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
SSE Progress Streaming Router

Server-Sent Events endpoint for real-time task progress monitoring.
"""

import asyncio
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from api.dependencies import PixelleVideoDep

router = APIRouter(tags=["Progress Streaming"])

# In-memory store for progress events (keyed by task_id)
_progress_subscribers: dict[str, list] = {}


async def progress_event_stream(task_id: str):
    """SSE stream generator for task progress events"""
    queue = asyncio.Queue()

    # Register subscriber
    if task_id not in _progress_subscribers:
        _progress_subscribers[task_id] = []
    _progress_subscribers[task_id].append(queue)

    try:
        # Send initial event
        yield f"event: connected\ndata: {json.dumps({'task_id': task_id, 'message': 'Connected to progress stream'})}\n\n"

        # Stream events
        while True:
            event = await queue.get()
            if event is None:  # Sentinel for stream end
                yield f"event: done\ndata: {json.dumps({'task_id': task_id, 'message': 'Stream ended'})}\n\n"
                break
            yield f"event: progress\ndata: {json.dumps(event)}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        # Unregister subscriber
        if task_id in _progress_subscribers and queue in _progress_subscribers[task_id]:
            _progress_subscribers[task_id].remove(queue)


def broadcast_progress(task_id: str, event: dict):
    """Broadcast a progress event to all subscribers for a task"""
    if task_id in _progress_subscribers:
        dead_queues = []
        for queue in _progress_subscribers[task_id]:
            try:
                queue.put_nowait(event)
            except Exception:
                dead_queues.append(queue)
        for q in dead_queues:
            _progress_subscribers[task_id].remove(q)


@router.get("/api/tasks/{task_id}/stream")
async def stream_task_progress(task_id: str, pixelle_video: PixelleVideoDep):
    """
    SSE endpoint for real-time task progress streaming.

    Connect to this endpoint to receive progress events for a specific task.
    Events are sent as Server-Sent Events (SSE) with the format:

    ```
    event: progress
    data: {"step": "generating_narrations", "progress": 0.2, "message": "..."}
    ```
    """
    # Check if task exists
    from api.tasks import task_manager
    task = task_manager.get_task(task_id)
    if not task:
        # Also check history
        try:
            detail = await pixelle_video.history.get_task_detail(task_id)
            if not detail:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        except Exception:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return StreamingResponse(
        progress_event_stream(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
