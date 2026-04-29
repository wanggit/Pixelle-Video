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
File Upload Router

Handles multipart file uploads for reference audio, character images,
video assets, and other user-provided files.
"""

import uuid
import mimetypes
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from loguru import logger

from api.schemas.upload import FileUploadResponse
from api.config import api_config

router = APIRouter(tags=["File Upload"])

# Allowed file types by category
ALLOWED_AUDIO = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}
ALLOWED_IMAGE = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_VIDEO = {".mp4", ".avi", ".mov", ".webm", ".mkv"}
ALLOWED_EXTENSIONS = ALLOWED_AUDIO | ALLOWED_IMAGE | ALLOWED_VIDEO

# Maximum file sizes (bytes)
MAX_AUDIO_SIZE = 50 * 1024 * 1024    # 50MB
MAX_IMAGE_SIZE = 20 * 1024 * 1024    # 20MB
MAX_VIDEO_SIZE = 200 * 1024 * 1024   # 200MB

# Upload directories
UPLOAD_BASE_DIR = Path("temp/uploads")


def _get_upload_dir(file_type: str) -> Path:
    """Get upload directory for a given file type"""
    dir_map = {
        "ref_audio": "ref_audio",
        "image": "images",
        "video": "videos",
        "asset": "assets",
        "bgm": "bgm",
    }
    subdir = dir_map.get(file_type, "misc")
    upload_dir = UPLOAD_BASE_DIR / subdir
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _validate_file(filename: str, file_type: str, file_size: int):
    """Validate uploaded file"""
    suffix = Path(filename).suffix.lower()

    # Check extension
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{suffix}' not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Check type-specific constraints
    if file_type == "ref_audio" and suffix not in ALLOWED_AUDIO:
        raise HTTPException(
            status_code=400,
            detail=f"Reference audio must be one of: {', '.join(sorted(ALLOWED_AUDIO))}",
        )

    if file_type == "image" and suffix not in ALLOWED_IMAGE:
        raise HTTPException(
            status_code=400,
            detail=f"Image must be one of: {', '.join(sorted(ALLOWED_IMAGE))}",
        )

    if file_type == "video" and suffix not in ALLOWED_VIDEO:
        raise HTTPException(
            status_code=400,
            detail=f"Video must be one of: {', '.join(sorted(ALLOWED_VIDEO))}",
        )

    # Check file size
    max_size = {
        "ref_audio": MAX_AUDIO_SIZE,
        "image": MAX_IMAGE_SIZE,
        "video": MAX_VIDEO_SIZE,
        "asset": MAX_VIDEO_SIZE,
        "bgm": MAX_AUDIO_SIZE,
    }.get(file_type, MAX_IMAGE_SIZE)

    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds limit ({max_size / 1024 / 1024:.0f}MB)",
        )


@router.post("/api/files/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(default="misc", description="Type of file: ref_audio, image, video, asset, bgm"),
):
    """
    Upload a file (audio, image, video).

    Supported file types:
    - Audio: .mp3, .wav, .ogg, .m4a, .flac (for reference audio, BGM)
    - Image: .jpg, .jpeg, .png, .gif, .webp (for character images, assets)
    - Video: .mp4, .avi, .mov, .webm, .mkv (for reference videos, assets)

    Returns the file path that can be used in subsequent API calls.
    """
    # Validate file type category
    valid_types = ["ref_audio", "image", "video", "asset", "bgm", "misc"]
    if file_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file_type. Must be one of: {', '.join(valid_types)}",
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate
    try:
        _validate_file(file.filename, file_type, file_size)
    except HTTPException:
        raise

    # Generate unique filename
    suffix = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{suffix}"

    # Save file
    upload_dir = _get_upload_dir(file_type)
    file_path = upload_dir / unique_filename

    try:
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"File uploaded: {file_path} ({file_size} bytes)")

        # Build API-accessible URL
        relative_path = file_path.relative_to(Path("."))
        file_url = f"/api/files/{relative_path}"

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))

        return FileUploadResponse(
            success=True,
            message=f"File uploaded successfully: {file.filename}",
            file_path=str(file_path),
            file_url=file_url,
            file_type=mime_type or "application/octet-stream",
            file_size=file_size,
        )
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        # Cleanup on failure
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
