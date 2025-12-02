from typing import List, Literal, Dict, Any, Optional
from pydantic import BaseModel, SecretStr, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# --- 1. Sub-Configuration Models (BaseModel) ---

class AppSettings(BaseModel):
    name: str = Field("Sentinel Quiz Leaderboard", description="Application Name / অ্যাপ্লিকেশনের নাম")
    environment: Literal["dev", "staging", "prod"] = Field("dev", description="Environment / পরিবেশ")
    debug: bool = Field(False, description="Debug Mode / ডিবাগ মোড")

class FacebookSettings(BaseModel):
    cookies_file_path: str = Field("cookies.json", description="Path to cookies file / কুকিজ ফাইলের পাথ")
    user_data_dir: str = Field("./user_data", description="Chrome user data dir / ক্রোম ইউজার ডাটা ডিরেক্টরি")
    max_comments: int = Field(100, description="Max comments to process / সর্বোচ্চ কতগুলো কমেন্ট প্রসেস হবে")

class ScraperSettings(BaseModel):
    headless: bool = Field(True, description="Run browser in background / ব্রাউজার ব্যাকগ্রাউন্ডে চলবে কিনা")
    slow_mo_min: int = 50
    slow_mo_max: int = 200
    scroll_pause_min: float = 1.0
    scroll_pause_max: float = 3.0
    
class APISettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    api_key: SecretStr = Field(SecretStr(""), description="Admin API Key / অ্যাডমিন API চাবি")
    allowed_origins: List[str] = ["http://localhost:3000"]

class DatabaseSettings(BaseModel):
    sqlite_path: str = "leaderboard.db"
    backup_enabled: bool = True

class RateLimitSettings(BaseModel):
    requests_per_minute: int = 20

class LoggingSettings(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    json_logs: bool = False

# --- 2. Main Settings Class (BaseSettings) ---

class Settings(BaseSettings):
    """
    Global Configuration.
    Loads from .env file and environment variables with '__' delimiter.
    Example: FACEBOOK__COOKIES_FILE overrides facebook.cookies_file_path
    """
    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        # preventing frozen=True here to allow proper loading of nested env vars
    )

    app: AppSettings = AppSettings()
    facebook: FacebookSettings = FacebookSettings()
    scraper: ScraperSettings = ScraperSettings()
    api: APISettings = APISettings()
    database: DatabaseSettings = DatabaseSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    logging: LoggingSettings = LoggingSettings()

    def validate_and_freeze(self):
        """
        Validates critical configuration and makes the object immutable.
        Raises ValueError with Bengali messages if validation fails.
        """
        errors = []

        # 1. Critical Validation (Bilingual)
        if not self.api.api_key.get_secret_value():
            errors.append("API__API_KEY is missing (API কি পাওয়া যায়নি)")
        
        # Check if environment is prod but debug is on (Warning/Error)
        if self.app.environment == "prod" and self.app.debug:
            print("WARNING: Running in PROD with DEBUG=True (সতর্কতা: প্রোডাকশনে ডিবাগ মোড চালু আছে)")

        if errors:
            raise ValueError("\n".join(errors))

        # 2. Make Immutable (Runtime Lock)
        # We recursively patch __setattr__ and __delattr__ to block changes
        self._make_immutable_recursive(self)

    def _make_immutable_recursive(self, obj: Any):
        if isinstance(obj, BaseModel):
            for field_name in obj.model_fields.keys():
                val = getattr(obj, field_name)
                self._make_immutable_recursive(val)
            
            # Patch the instance to prevent modification
            object.__setattr__(obj, "__setattr__", self._frozen_setattr)
            object.__setattr__(obj, "__delattr__", self._frozen_delattr)

    @staticmethod
    def _frozen_setattr(self, name, value):
        raise TypeError(f"Configuration is frozen. Cannot set '{name}'. (কনফিগারেশন পরিবর্তন করা যাবে না)")

    @staticmethod
    def _frozen_delattr(self, name):
        raise TypeError(f"Configuration is frozen. Cannot delete '{name}'. (কনফিগারেশন ডিলিট করা যাবে না)")

    def get_safe_dump(self) -> Dict[str, Any]:
        """
        Returns a dictionary safe for logging (Secrets redacted).
        """
        data = self.model_dump()
        # Manually redact specific secret paths if model_dump didn't handle them via SecretStr context
        # In Pydantic v2, SecretStr dumps as string by default in model_dump unless customized.
        # We explicitly mask the known secret field.
        if 'api' in data and 'api_key' in data['api']:
            data['api']['api_key'] = "**********"
        return data

# Singleton Instance
_settings_instance: Optional[Settings] = None

def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance