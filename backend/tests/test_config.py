"""Tests for application configuration."""

from unittest.mock import patch

from app.config import Settings


class TestSettings:
    def test_default_values(self):
        s = Settings()
        assert s.spacex_api_base == "https://api.spacexdata.com"
        assert s.redis_url == "redis://localhost:6379/0"
        assert s.spacex_timeout == 10
        assert s.spacex_retries == 2
        assert s.groq_model == "llama-3.3-70b-versatile"
        assert s.groq_api_key == ""

    def test_ttl_defaults(self):
        s = Settings()
        assert s.rockets_ttl == 86400
        assert s.launches_ttl == 120
        assert s.starlink_ttl == 300
        assert s.dashboard_ttl == 300
        assert s.cores_ttl == 86400
        assert s.launchpads_ttl == 86400
        assert s.history_ttl == 86400
        assert s.landing_ttl == 86400
        assert s.roadster_ttl == 86400
        assert s.economics_ttl == 300
        assert s.emissions_ttl == 300

    def test_cors_origins_default(self):
        s = Settings()
        assert "quadsci.juantoledo.com.mx" in s.cors_origins
        assert "localhost:5173" in s.cors_origins

    def test_env_override(self):
        with patch.dict(
            "os.environ",
            {"SPACEX_TIMEOUT": "30", "SPACEX_RETRIES": "5"},
        ):
            s = Settings()
            assert s.spacex_timeout == 30
            assert s.spacex_retries == 5
