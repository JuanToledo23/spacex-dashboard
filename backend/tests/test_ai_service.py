"""Tests for the AI service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai_service import (
    _is_available,
    chat,
    generate_ai_insights,
    generate_fun_fact,
)


class TestBuildDataContext:
    @pytest.mark.asyncio
    async def test_builds_context_string(self):
        rockets = [
            MagicMock(
                name="Falcon 9",
                launch_count=100,
                success_rate_pct=98.0,
                active=True,
            ),
        ]
        fleet = MagicMock(
            active_cores=10,
            total_landings=200,
            landing_success_rate=95.0,
        )
        launches = [
            {"success": True, "upcoming": False},
            {"success": False, "upcoming": False},
            {"success": None, "upcoming": True},
        ]
        starlink_stats = {"total": 5000}

        with (
            patch(
                "app.services.ai_service.rocket_service.get_rockets",
                new_callable=AsyncMock,
                return_value=rockets,
            ),
            patch(
                "app.services.ai_service.launch_service.get_all_launches",
                new_callable=AsyncMock,
                return_value=launches,
            ),
            patch(
                "app.services.ai_service.starlink_service.get_starlink_stats",
                new_callable=AsyncMock,
                return_value=starlink_stats,
            ),
            patch(
                "app.services.ai_service.core_service.get_fleet_stats",
                new_callable=AsyncMock,
                return_value=fleet,
            ),
            patch(
                "app.services.ai_service.emissions_service.get_emissions_data",
                new_callable=AsyncMock,
                side_effect=Exception("skip"),
            ),
            patch(
                "app.services.ai_service.economics_service.get_economics_data",
                new_callable=AsyncMock,
                side_effect=Exception("skip"),
            ),
            patch(
                "app.services.ai_service.history_service.get_history",
                new_callable=AsyncMock,
                side_effect=Exception("skip"),
            ),
            patch(
                "app.services.ai_service.landing_service.get_landing_data",
                new_callable=AsyncMock,
                side_effect=Exception("skip"),
            ),
            patch(
                "app.services.ai_service.launchpad_service.get_launchpads",
                new_callable=AsyncMock,
                side_effect=Exception("skip"),
            ),
            patch(
                "app.services.ai_service.roadster_service.get_roadster_data",
                new_callable=AsyncMock,
                side_effect=Exception("skip"),
            ),
        ):
            from app.services.ai_service import _build_data_context

            result = await _build_data_context()
            assert "SpaceX Program Data" in result
            assert "Missions" in result
            assert "Fleet" in result
            assert "Starlink" in result
            assert "Rockets" in result

    @pytest.mark.asyncio
    async def test_builds_context_with_all_sections(self):
        """Test _build_data_context when all optional services succeed."""
        rockets = [
            MagicMock(
                name="Falcon 9",
                launch_count=100,
                success_rate_pct=98.0,
                active=True,
            ),
        ]
        fleet = MagicMock(
            active_cores=10,
            total_landings=200,
            landing_success_rate=95.0,
        )
        launches = [{"success": True, "upcoming": False}]
        starlink_stats = {"total": 5000}

        emissions = MagicMock(
            total_co2_tonnes=1000,
            total_fuel_tonnes=2000,
            co2_per_launch=500,
            reuse_co2_saved_tonnes=60,
            total_reuses=1,
            emissions_by_vehicle=[
                MagicMock(
                    rocket_name="F9",
                    total_co2_tonnes=900,
                    launches=100,
                    fuel_type="RP-1",
                )
            ],
        )
        economics = MagicMock(
            total_estimated_spend=1e9,
            avg_cost_per_launch=5e7,
            lowest_cost_per_kg=2700,
            lowest_cost_vehicle="F9",
            total_payloads=100,
            total_mass_launched_kg=1e6,
            cost_by_vehicle=[
                MagicMock(
                    rocket_name="F9",
                    cost_per_launch=5e7,
                    launches=100,
                    total_spend=5e9,
                )
            ],
        )
        history = MagicMock(
            total=5,
            events=[
                MagicMock(event_date_utc="2020-01-01", title="Event 1"),
            ],
        )
        landing = MagicMock(
            stats=MagicMock(
                total_attempts=100,
                total_successes=90,
                overall_success_rate=90.0,
                rtls_successes=30,
                rtls_attempts=33,
                asds_successes=60,
                asds_attempts=67,
            ),
            landpads=[
                MagicMock(
                    full_name="LZ-1",
                    type="RTLS",
                    status="active",
                    landing_successes=30,
                    landing_attempts=33,
                    success_rate=90.9,
                )
            ],
        )
        launchpads = [
            MagicMock(
                full_name="LC-39A",
                locality="Florida",
                region="US",
                launch_successes=49,
                launch_attempts=50,
                status="active",
            ),
        ]
        roadster = MagicMock(
            launch_date_utc="2018-02-06T00:00:00Z",
            speed_kph=9521,
            earth_distance_km=3e8,
            mars_distance_km=1.5e8,
            orbit_type="heliocentric",
            period_days=557.2,
            apoapsis_au=1.664,
            periapsis_au=0.986,
        )

        with (
            patch(
                "app.services.ai_service.rocket_service.get_rockets",
                new_callable=AsyncMock,
                return_value=rockets,
            ),
            patch(
                "app.services.ai_service.launch_service.get_all_launches",
                new_callable=AsyncMock,
                return_value=launches,
            ),
            patch(
                "app.services.ai_service.starlink_service.get_starlink_stats",
                new_callable=AsyncMock,
                return_value=starlink_stats,
            ),
            patch(
                "app.services.ai_service.core_service.get_fleet_stats",
                new_callable=AsyncMock,
                return_value=fleet,
            ),
            patch(
                "app.services.ai_service.emissions_service.get_emissions_data",
                new_callable=AsyncMock,
                return_value=emissions,
            ),
            patch(
                "app.services.ai_service.economics_service.get_economics_data",
                new_callable=AsyncMock,
                return_value=economics,
            ),
            patch(
                "app.services.ai_service.history_service.get_history",
                new_callable=AsyncMock,
                return_value=history,
            ),
            patch(
                "app.services.ai_service.landing_service.get_landing_data",
                new_callable=AsyncMock,
                return_value=landing,
            ),
            patch(
                "app.services.ai_service.launchpad_service.get_launchpads",
                new_callable=AsyncMock,
                return_value=launchpads,
            ),
            patch(
                "app.services.ai_service.roadster_service.get_roadster_data",
                new_callable=AsyncMock,
                return_value=roadster,
            ),
        ):
            from app.services.ai_service import _build_data_context

            result = await _build_data_context()
            assert "Emissions" in result
            assert "Economics" in result
            assert "History" in result
            assert "Landing Operations" in result
            assert "Launch Sites" in result
            assert "Starman" in result


class TestIsAvailable:
    def test_available_when_key_set(self):
        with patch("app.services.ai_service.settings") as mock_settings:
            mock_settings.groq_api_key = "key123"
            assert _is_available() is True

    def test_unavailable_when_empty(self):
        with patch("app.services.ai_service.settings") as mock_settings:
            mock_settings.groq_api_key = ""
            assert _is_available() is False


class TestChat:
    @pytest.mark.asyncio
    async def test_returns_message_when_unavailable(self):
        with patch("app.services.ai_service._is_available", return_value=False):
            result = await chat("hello", [])
            assert "not configured" in result

    @pytest.mark.asyncio
    async def test_chat_success(self):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="SpaceX has 200+ missions"))]
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with (
            patch("app.services.ai_service._is_available", return_value=True),
            patch(
                "app.services.ai_service._build_data_context",
                new_callable=AsyncMock,
                return_value="context data",
            ),
            patch(
                "app.services.ai_service._get_client",
                return_value=mock_client,
            ),
        ):
            result = await chat("how many missions?", [])
            assert result == "SpaceX has 200+ missions"

    @pytest.mark.asyncio
    async def test_chat_includes_history(self):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="response"))]
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        history = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ]

        with (
            patch("app.services.ai_service._is_available", return_value=True),
            patch(
                "app.services.ai_service._build_data_context",
                new_callable=AsyncMock,
                return_value="ctx",
            ),
            patch(
                "app.services.ai_service._get_client",
                return_value=mock_client,
            ),
        ):
            await chat("follow up", history)
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args.kwargs["messages"]
            # system + 2 history + 1 user = 4
            assert len(messages) == 4

    @pytest.mark.asyncio
    async def test_chat_error_handling(self):
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=RuntimeError("API down"))

        with (
            patch("app.services.ai_service._is_available", return_value=True),
            patch(
                "app.services.ai_service._build_data_context",
                new_callable=AsyncMock,
                return_value="ctx",
            ),
            patch(
                "app.services.ai_service._get_client",
                return_value=mock_client,
            ),
        ):
            result = await chat("test", [])
            assert "trouble connecting" in result


class TestGenerateFunFact:
    @pytest.mark.asyncio
    async def test_returns_none_when_unavailable(self):
        with patch("app.services.ai_service._is_available", return_value=False):
            result = await generate_fun_fact()
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_fact(self):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Falcon 9 has landed 200+ times"))
        ]
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with (
            patch("app.services.ai_service._is_available", return_value=True),
            patch(
                "app.services.ai_service._build_data_context",
                new_callable=AsyncMock,
                return_value="ctx",
            ),
            patch(
                "app.services.ai_service._get_client",
                return_value=mock_client,
            ),
        ):
            result = await generate_fun_fact()
            assert result == "Falcon 9 has landed 200+ times"

    @pytest.mark.asyncio
    async def test_returns_none_on_error(self):
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=RuntimeError("fail"))

        with (
            patch("app.services.ai_service._is_available", return_value=True),
            patch(
                "app.services.ai_service._build_data_context",
                new_callable=AsyncMock,
                return_value="ctx",
            ),
            patch(
                "app.services.ai_service._get_client",
                return_value=mock_client,
            ),
        ):
            result = await generate_fun_fact()
            assert result is None


class TestGenerateAiInsights:
    @pytest.mark.asyncio
    async def test_returns_none_when_unavailable(self):
        with patch("app.services.ai_service._is_available", return_value=False):
            result = await generate_ai_insights()
            assert result is None

    @pytest.mark.asyncio
    async def test_parses_structured_json_response(self):
        items = [
            '{"text":"Rec 1.","action_type":"optimize",'
            '"priority":"high","domains":["fleet","economics"]}',
            '{"text":"Rec 2.","action_type":"investigate",'
            '"priority":"medium","domains":["landing","emissions"]}',
            '{"text":"Rec 3.","action_type":"scale",'
            '"priority":"low","domains":["missions","starlink"]}',
            '{"text":"Rec 4.","action_type":"reduce",'
            '"priority":"high","domains":["emissions","fleet"]}',
            '{"text":"Rec 5.","action_type":"monitor",'
            '"priority":"medium","domains":["starlink","economics"]}',
        ]
        json_content = "[" + ",".join(items) + "]"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json_content))]
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with (
            patch("app.services.ai_service._is_available", return_value=True),
            patch(
                "app.services.ai_service._build_data_context",
                new_callable=AsyncMock,
                return_value="ctx",
            ),
            patch(
                "app.services.ai_service._get_client",
                return_value=mock_client,
            ),
        ):
            result = await generate_ai_insights()
            assert result is not None
            assert len(result) == 5
            assert result[0].id == "ai_action_1"
            assert result[0].type == "ai_summary"
            assert result[0].action_type == "optimize"
            assert result[0].priority == "high"
            assert result[0].domains == ["fleet", "economics"]

    @pytest.mark.asyncio
    async def test_handles_plain_string_fallback(self):
        """LLM may return plain strings instead of objects; should still parse."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='```json\n["A", "B", "C", "D", "E"]\n```'))
        ]
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with (
            patch("app.services.ai_service._is_available", return_value=True),
            patch(
                "app.services.ai_service._build_data_context",
                new_callable=AsyncMock,
                return_value="ctx",
            ),
            patch(
                "app.services.ai_service._get_client",
                return_value=mock_client,
            ),
        ):
            result = await generate_ai_insights()
            assert result is not None
            assert len(result) == 5
            assert result[0].action_type == "monitor"

    @pytest.mark.asyncio
    async def test_returns_none_on_error(self):
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=RuntimeError("fail"))

        with (
            patch("app.services.ai_service._is_available", return_value=True),
            patch(
                "app.services.ai_service._build_data_context",
                new_callable=AsyncMock,
                return_value="ctx",
            ),
            patch(
                "app.services.ai_service._get_client",
                return_value=mock_client,
            ),
        ):
            result = await generate_ai_insights()
            assert result is None
