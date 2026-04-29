"""
Pipeline Endpoints

API routes for CustomMedia, ImageToVideo, ActionTransfer, and DigitalHuman pipelines.
Each pipeline calls the pixelle_video core library directly (same pattern as Streamlit UI).
"""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.tasks import task_manager, TaskType
from api.schemas.pipelines import (
    CustomMediaRequest,
    CustomMediaAsyncResponse,
    ImageToVideoRequest,
    ImageToVideoAsyncResponse,
    ActionTransferRequest,
    ActionTransferAsyncResponse,
    DigitalHumanRequest,
    DigitalHumanAsyncResponse,
)

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


def path_to_url(request: Request, file_path: str) -> str:
    """Convert file path to accessible URL."""
    file_path = file_path.replace("\\", "/")
    is_absolute = os.path.isabs(file_path) or Path(file_path).is_absolute()
    if is_absolute:
        parts = file_path.split("/")
        try:
            output_idx = parts.index("output")
            relative_parts = parts[output_idx + 1:]
            file_path = "/".join(relative_parts)
        except ValueError:
            file_path = Path(file_path).name
    else:
        if file_path.startswith("output/"):
            file_path = file_path[7:]
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}/api/files/{file_path}"


# ==========================================
# Custom Media (Asset-Based) Pipeline
# ==========================================

@router.post("/custom-media/async", response_model=CustomMediaAsyncResponse)
async def custom_media_async(
    request_body: CustomMediaRequest,
    pixelle_video: PixelleVideoDep,
    request: Request,
):
    """Submit a custom media (asset-based) video generation task."""
    try:
        from pixelle_video.pipelines.asset_based import AssetBasedPipeline

        task = task_manager.create_task(
            task_type=TaskType.VIDEO_GENERATION,
            request_params=request_body.model_dump(),
        )

        async def execute():
            pipeline = AssetBasedPipeline(pixelle_video)
            result = await pipeline(
                assets=request_body.assets,
                video_title=request_body.video_title,
                intent=request_body.intent,
                duration=request_body.duration,
                source=request_body.source,
                bgm_path=request_body.bgm_path,
                bgm_volume=request_body.bgm_volume,
                bgm_mode="loop",
                voice_id=request_body.voice_id or "zh-CN-YunjianNeural",
                tts_speed=request_body.tts_speed,
                progress_callback=None,
            )
            file_size = os.path.getsize(result.video_path) if os.path.exists(result.video_path) else 0
            video_url = path_to_url(request, result.video_path)
            return {
                "video_url": video_url,
                "duration": result.duration,
                "file_size": file_size,
            }

        await task_manager.execute_task(task_id=task.task_id, coro_func=execute)

        return CustomMediaAsyncResponse(task_id=task.task_id, success=True, message="任务已提交")
    except Exception as e:
        logger.error(f"Custom media async error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Image to Video Pipeline
# ==========================================

@router.post("/image-to-video/async", response_model=ImageToVideoAsyncResponse)
async def image_to_video_async(
    request_body: ImageToVideoRequest,
    pixelle_video: PixelleVideoDep,
    request: Request,
):
    """Submit an image-to-video generation task."""
    try:
        task = task_manager.create_task(
            task_type=TaskType.VIDEO_GENERATION,
            request_params=request_body.model_dump(),
        )

        async def execute():
            kit = await pixelle_video._get_or_create_comfykit()

            # Determine workflow input
            if request_body.source == "runninghub":
                workflow_input = request_body.workflow  # e.g., "runninghub/i2v_basic.json"
            else:
                workflow_path = Path(_project_root()) / "workflows" / "selfhost" / Path(request_body.workflow).name
                workflow_input = str(workflow_path)

            workflow_params = {
                "image": request_body.image,
                "prompt": request_body.prompt,
            }

            result = await kit.execute(workflow_input, workflow_params)

            # Download result video
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(result.video_url)
                resp.raise_for_status()
                output_dir = Path(_project_root()) / "output" / task.task_id
                output_dir.mkdir(parents=True, exist_ok=True)
                video_path = output_dir / "final.mp4"
                video_path.write_bytes(resp.content)

            file_size = video_path.stat().st_size if video_path.exists() else 0
            video_url = path_to_url(request, str(video_path))
            return {
                "video_url": video_url,
                "duration": 0,
                "file_size": file_size,
            }

        await task_manager.execute_task(task_id=task.task_id, coro_func=execute)

        return ImageToVideoAsyncResponse(task_id=task.task_id, success=True, message="任务已提交")
    except Exception as e:
        logger.error(f"Image-to-video async error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Action Transfer Pipeline
# ==========================================

@router.post("/action-transfer/async", response_model=ActionTransferAsyncResponse)
async def action_transfer_async(
    request_body: ActionTransferRequest,
    pixelle_video: PixelleVideoDep,
    request: Request,
):
    """Submit an action transfer task."""
    try:
        task = task_manager.create_task(
            task_type=TaskType.VIDEO_GENERATION,
            request_params=request_body.model_dump(),
        )

        async def execute():
            kit = await pixelle_video._get_or_create_comfykit()

            if request_body.source == "runninghub":
                workflow_input = request_body.workflow
            else:
                workflow_path = Path(_project_root()) / "workflows" / "selfhost" / Path(request_body.workflow).name
                workflow_input = str(workflow_path)

            workflow_params = {
                "video": request_body.video,
                "image": request_body.image,
                "prompt": request_body.prompt,
                "second": request_body.duration,
            }

            result = await kit.execute(workflow_input, workflow_params)

            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(result.video_url)
                resp.raise_for_status()
                output_dir = Path(_project_root()) / "output" / task.task_id
                output_dir.mkdir(parents=True, exist_ok=True)
                video_path = output_dir / "final.mp4"
                video_path.write_bytes(resp.content)

            file_size = video_path.stat().st_size if video_path.exists() else 0
            video_url = path_to_url(request, str(video_path))
            return {
                "video_url": video_url,
                "duration": request_body.duration,
                "file_size": file_size,
            }

        await task_manager.execute_task(task_id=task.task_id, coro_func=execute)

        return ActionTransferAsyncResponse(task_id=task.task_id, success=True, message="任务已提交")
    except Exception as e:
        logger.error(f"Action transfer async error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Digital Human Pipeline
# ==========================================

@router.post("/digital-human/async", response_model=DigitalHumanAsyncResponse)
async def digital_human_async(
    request_body: DigitalHumanRequest,
    pixelle_video: PixelleVideoDep,
    request: Request,
):
    """Submit a digital human video generation task."""
    try:
        task = task_manager.create_task(
            task_type=TaskType.VIDEO_GENERATION,
            request_params=request_body.model_dump(),
        )

        async def execute():
            import tempfile
            import uuid

            kit = await pixelle_video._get_or_create_comfykit()

            # Resolve workflow paths
            def resolve_workflow_path(wp: str) -> str:
                if not wp:
                    return ""
                if wp.startswith("runninghub"):
                    return wp
                full = Path(_project_root()) / "workflows" / "selfhost" / Path(wp).name
                return str(full)

            character_image = request_body.character_assets[0]

            if request_body.mode == "customize":
                # 2-step: TTS + lip-sync
                audio_path = Path(tempfile.gettempdir()) / f"tts_{uuid.uuid4().hex}.mp3"
                await pixelle_video.tts(
                    text=request_body.goods_text,
                    output_path=str(audio_path),
                    inference_mode=request_body.tts_inference_mode,
                    **({"voice": request_body.tts_voice, "speed": request_body.tts_speed} if request_body.tts_inference_mode == "local" else {}),
                    **({"workflow": request_body.tts_workflow, "ref_audio": request_body.ref_audio} if request_body.tts_inference_mode == "comfyui" else {}),
                )

                second_workflow = resolve_workflow_path(request_body.workflow_path.get("second_workflow_path", ""))
                result = await kit.execute(second_workflow, {
                    "videoimage": character_image,
                    "audio": str(audio_path),
                })
            else:
                # Digital mode: 3-step (image synthesis -> TTS -> lip-sync)
                audio_path = Path(tempfile.gettempdir()) / f"tts_{uuid.uuid4().hex}.mp3"
                await pixelle_video.tts(
                    text=request_body.goods_text,
                    output_path=str(audio_path),
                    inference_mode=request_body.tts_inference_mode,
                    **({"voice": request_body.tts_voice, "speed": request_body.tts_speed} if request_body.tts_inference_mode == "local" else {}),
                    **({"workflow": request_body.tts_workflow, "ref_audio": request_body.ref_audio} if request_body.tts_inference_mode == "comfyui" else {}),
                )

                # Use third workflow for image combination if goods assets exist
                generated_image = character_image
                if request_body.goods_assets:
                    goods_image = request_body.goods_assets[0]
                    third_workflow = resolve_workflow_path(request_body.workflow_path.get("third_workflow_path", ""))
                    if third_workflow:
                        img_result = await kit.execute(third_workflow, {
                            "firstimage": character_image,
                            "secondimage": goods_image,
                        })
                        generated_image = img_result.get("image_url", character_image)

                second_workflow = resolve_workflow_path(request_body.workflow_path.get("second_workflow_path", ""))
                result = await kit.execute(second_workflow, {
                    "videoimage": generated_image,
                    "audio": str(audio_path),
                })

            # Download result
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(result.video_url)
                resp.raise_for_status()
                output_dir = Path(_project_root()) / "output" / task.task_id
                output_dir.mkdir(parents=True, exist_ok=True)
                video_path = output_dir / "final.mp4"
                video_path.write_bytes(resp.content)

            file_size = video_path.stat().st_size if video_path.exists() else 0
            video_url = path_to_url(request, str(video_path))
            return {
                "video_url": video_url,
                "duration": 0,
                "file_size": file_size,
            }

        await task_manager.execute_task(task_id=task.task_id, coro_func=execute)

        return DigitalHumanAsyncResponse(task_id=task.task_id, success=True, message="任务已提交")
    except Exception as e:
        logger.error(f"Digital human async error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent.parent
