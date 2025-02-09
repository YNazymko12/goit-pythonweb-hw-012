"""Mock settings for documentation generation."""

from typing import Any

class MockSettings:
    """Mock settings class for documentation."""
    DB_URL: str = "sqlite:///./test.db"
    JWT_SECRET: str = "test_secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    MAIL_USERNAME: str = "test@example.com"
    MAIL_PASSWORD: str = "test_password"
    MAIL_FROM: str = "test@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.example.com"
    MAIL_FROM_NAME: str = "Test System"
    CLOUDINARY_NAME: str = "test_cloud"
    CLOUDINARY_API_KEY: str = "test_key"
    CLOUDINARY_API_SECRET: str = "test_secret"

    def __getattr__(self, name: str) -> Any:
        """Handle any missing attributes by returning None."""
        return None

settings = MockSettings()
