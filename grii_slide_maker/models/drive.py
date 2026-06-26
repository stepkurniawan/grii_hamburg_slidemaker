from io import BytesIO

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


GOOGLE_DRIVE_FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


class DriveItem(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True, populate_by_name=True)

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    mime_type: str = Field(
        alias="mimeType",
        min_length=1,
        description="The MIME type of the Google Drive item.",
        examples=["application/vnd.google-apps.folder", "image/png"],
    )

    @property
    def is_folder(self) -> bool:
        return self.mime_type == GOOGLE_DRIVE_FOLDER_MIME_TYPE

    @property
    def is_image(self) -> bool:
        return self.mime_type.startswith("image/")


class DriveFolder(DriveItem):
    @model_validator(mode="after")
    def validate_folder(self) -> "DriveFolder":
        if not self.is_folder:
            raise ValueError(f"Drive item '{self.name}' is not a folder")
        return self


class DriveImageFile(DriveItem):
    @model_validator(mode="after")
    def validate_image(self) -> "DriveImageFile":
        if not self.is_image:
            raise ValueError(f"Drive item '{self.name}' is not an image")
        return self


class SongImageSet(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    images: dict[str, BytesIO]

    @field_validator("images")
    @classmethod
    def validate_images(cls, value: dict[str, BytesIO]) -> dict[str, BytesIO]:
        if not value:
            raise ValueError("No image files were found for this song or announcement folder")
        for name, image_bytes in value.items():
            if not name.strip():
                raise ValueError("Image filename cannot be empty")
            if not isinstance(image_bytes, BytesIO):
                raise ValueError(f"Image '{name}' must be stored as BytesIO")
        return value
