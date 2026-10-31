"""Configuration settings and environment management for aidy.AI."""

import os
from typing import Optional, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Product Metadata
    APP_NAME: str = "aidy.AI"
    APP_SUBTITLE: str = "Research intelligently. Verify rigorously. Report confidently."
    VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "production", "testing"] = "development"

    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API Key for primary CrewAI LLM")
    OPENAI_MODEL_NAME: str = Field("gpt-4o-mini", description="Model identifier for OpenAI")
    ANTHROPIC_API_KEY: Optional[str] = Field(None, description="Anthropic API Key if using Claude")
    GEMINI_API_KEY: Optional[str] = Field(None, description="Google Gemini API Key if using Gemini")

    # Search Providers
    SERPAPI_API_KEY: Optional[str] = Field(None, description="SerpAPI Key for live search")
    TAVILY_API_KEY: Optional[str] = Field(None, description="Tavily API Key as secondary search")
    SEARCH_PROVIDER: Literal["serpapi", "duckduckgo", "mock"] = "serpapi"

    # Execution Budgets & Timeouts
    REQUEST_TIMEOUT_S: int = 15
    MAX_SEARCH_RESULTS: int = 5
    MAX_AGENT_ITERATIONS: int = 3
    MAX_TOKENS_PER_RUN: int = 25000
    OFFLINE_DEMO_MODE: bool = False

    # Persistence
    DATABASE_URL: str = "sqlite:///data/aidy.db"

    # Export paths
    REPORTS_DIR: str = "data/reports"
    GENERATED_DATA_DIR: str = "data/generated"

    @property
    def has_live_llm_credentials(self) -> bool:
        """Determines if valid LLM credentials are configured."""
        return bool(self.OPENAI_API_KEY or self.ANTHROPIC_API_KEY or self.GEMINI_API_KEY)

    @property
    def has_live_search_credentials(self) -> bool:
        """Determines if live search API key is configured."""
        return bool(self.SERPAPI_API_KEY or self.TAVILY_API_KEY)


settings = Settings()
