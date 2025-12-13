"""
Upload service for handling file uploads to cloud storage (Cloudinary).
"""

import cloudinary
import cloudinary.uploader
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException, status
import mimetypes
from app.core.config import settings
from app.models.file import FileType


class UploadService:
    """Service for handling file uploads to Cloudinary"""

    # Maximum file size (default: 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

    # Allowed MIME types
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg", "image/jpg", "image/png", "image/gif",
        "image/webp", "image/svg+xml", "image/bmp"
    }
    ALLOWED_VIDEO_TYPES = {
        "video/mp4", "video/mpeg", "video/quicktime",
        "video/x-msvideo", "video/webm"
    }
    ALLOWED_DOCUMENT_TYPES = {
        "application/pdf", "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain", "text/csv"
    }
    ALLOWED_AUDIO_TYPES = {
        "audio/mpeg", "audio/wav", "audio/ogg",
        "audio/mp4", "audio/webm"
    }

    def __init__(self):
        """Initialize Cloudinary configuration"""
        self._configured = False

        if settings.is_cloudinary_configured:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True
            )
            self._configured = True

    def _ensure_configured(self):
        """Ensure Cloudinary is configured before operations"""
        if not self._configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File upload service is not configured. Please configure Cloudinary credentials."
            )

    def _determine_file_type(self, mime_type: Optional[str]) -> FileType:
        """Determine FileType enum from MIME type"""
        if not mime_type:
            return FileType.OTHER

        if mime_type in self.ALLOWED_IMAGE_TYPES:
            return FileType.IMAGE
        elif mime_type in self.ALLOWED_VIDEO_TYPES:
            return FileType.VIDEO
        elif mime_type in self.ALLOWED_DOCUMENT_TYPES:
            return FileType.DOCUMENT
        elif mime_type in self.ALLOWED_AUDIO_TYPES:
            return FileType.AUDIO
        else:
            return FileType.OTHER

    def _validate_file(self, file: UploadFile) -> None:
        """Validate file before upload"""
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024 * 1024)}MB"
            )

        # Determine MIME type
        mime_type = file.content_type
        if not mime_type:
            # Guess from filename
            guessed_type, _ = mimetypes.guess_type(file.filename)
            mime_type = guessed_type

        # Check if MIME type is allowed
        all_allowed_types = (
            self.ALLOWED_IMAGE_TYPES |
            self.ALLOWED_VIDEO_TYPES |
            self.ALLOWED_DOCUMENT_TYPES |
            self.ALLOWED_AUDIO_TYPES
        )

        if mime_type and mime_type not in all_allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type '{mime_type}' is not supported"
            )

    async def upload_file(
        self,
        file: UploadFile,
        folder: str = "notion-clone",
        workspace_id: Optional[str] = None,
        public_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Cloudinary and return metadata

        Args:
            file: The file to upload
            folder: Cloudinary folder to store the file (default: "notion-clone")
            workspace_id: Optional workspace ID to organize files
            public_id: Optional custom public ID for the file

        Returns:
            Dict containing:
                - filename: Original filename
                - file_type: FileType enum value
                - mime_type: MIME type of the file
                - size_bytes: File size in bytes
                - storage_url: Full URL to access the file
                - storage_id: Cloudinary public_id
                - thumbnail_url: Optional thumbnail URL for images/videos

        Raises:
            HTTPException: If file validation fails or upload fails
        """
        # Ensure Cloudinary is configured
        self._ensure_configured()

        # Validate file
        self._validate_file(file)

        # Determine MIME type
        mime_type = file.content_type
        if not mime_type:
            guessed_type, _ = mimetypes.guess_type(file.filename)
            mime_type = guessed_type

        # Determine file type
        file_type = self._determine_file_type(mime_type)

        # Get file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        # Build folder path
        if workspace_id:
            folder = f"{folder}/{workspace_id}"

        try:
            # Prepare upload options
            upload_options = {
                "folder": folder,
                "resource_type": "auto",  # Let Cloudinary detect the type
                "use_filename": True,
                "unique_filename": True,
            }

            if public_id:
                upload_options["public_id"] = public_id

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file.file,
                **upload_options
            )

            # Generate thumbnail for images and videos
            thumbnail_url = None
            if file_type in [FileType.IMAGE, FileType.VIDEO]:
                # For images, use a transformation
                if file_type == FileType.IMAGE:
                    thumbnail_url = cloudinary.CloudinaryImage(result['public_id']).build_url(
                        transformation=[
                            {'width': 200, 'height': 200, 'crop': 'fill'},
                            {'quality': 'auto', 'fetch_format': 'auto'}
                        ]
                    )
                # For videos, Cloudinary automatically generates thumbnails
                elif file_type == FileType.VIDEO:
                    thumbnail_url = result.get('thumbnail_url') or cloudinary.CloudinaryVideo(result['public_id']).build_url(
                        transformation=[
                            {'width': 200, 'height': 200, 'crop': 'fill'},
                            {'quality': 'auto'}
                        ],
                        format='jpg'
                    )

            return {
                "filename": file.filename,
                "file_type": file_type,
                "mime_type": mime_type,
                "size_bytes": file_size,
                "storage_url": result['secure_url'],
                "storage_id": result['public_id'],
                "thumbnail_url": thumbnail_url,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )

    async def delete_file(self, storage_id: str, resource_type: str = "auto") -> bool:
        """
        Delete file from Cloudinary

        Args:
            storage_id: Cloudinary public_id of the file
            resource_type: Type of resource (image, video, raw, auto)

        Returns:
            True if deletion was successful

        Raises:
            HTTPException: If deletion fails
        """
        # Ensure Cloudinary is configured
        self._ensure_configured()

        try:
            result = cloudinary.uploader.destroy(
                storage_id,
                resource_type=resource_type
            )
            return result.get('result') == 'ok'
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )

    def get_file_url(
        self,
        storage_id: str,
        transformation: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get URL for a file with optional transformations

        Args:
            storage_id: Cloudinary public_id
            transformation: Optional transformation parameters

        Returns:
            Full URL to the file
        """
        # Ensure Cloudinary is configured
        self._ensure_configured()

        if transformation:
            return cloudinary.CloudinaryImage(storage_id).build_url(
                transformation=transformation
            )
        return cloudinary.CloudinaryImage(storage_id).build_url()


# Singleton instance
upload_service = UploadService()
