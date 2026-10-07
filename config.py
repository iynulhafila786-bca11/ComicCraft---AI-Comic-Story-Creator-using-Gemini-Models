from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    gemini_api_key: str = ""
    hf_token: str = ""
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"
    image_provider: str = "hf"
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"
    local_image_model: str = "runwayml/stable-diffusion-v1-5"
    panels_count: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def static_dir(self):
        return BASE_DIR / "static"

    @property
    def panels_dir(self):
        path = self.static_dir / "panels"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def exports_dir(self):
        path = self.static_dir / "exports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def templates_dir(self):
        return BASE_DIR / "templates"

@lru_cache
def get_settings():
    return Settings()
