"""Pydantic schemas for launch listing and detail data."""

from pydantic import BaseModel


class LaunchSummary(BaseModel):
    id: str
    name: str
    date_utc: str
    success: bool | None = None
    upcoming: bool
    rocket_id: str
    rocket_name: str | None = None
    details: str | None = None
    patch_small: str | None = None


class LaunchAggregate(BaseModel):
    year: int
    total: int
    successes: int
    failures: int


# --- Detail schemas ---


class PayloadSummary(BaseModel):
    id: str
    name: str
    type: str | None = None
    customers: list[str] = []
    mass_kg: float | None = None
    orbit: str | None = None
    regime: str | None = None


class CoreDetail(BaseModel):
    serial: str | None = None
    flight: int | None = None
    reused: bool | None = None
    landing_attempt: bool | None = None
    landing_success: bool | None = None
    landing_type: str | None = None


class CrewMember(BaseModel):
    id: str
    name: str
    agency: str | None = None
    image: str | None = None
    role: str | None = None


class LaunchLinks(BaseModel):
    webcast: str | None = None
    article: str | None = None
    wikipedia: str | None = None
    presskit: str | None = None
    reddit_campaign: str | None = None
    flickr_original: list[str] = []
    patch_small: str | None = None
    patch_large: str | None = None


class LaunchFailure(BaseModel):
    time: int | None = None
    altitude: float | None = None
    reason: str | None = None


class LaunchDetail(BaseModel):
    id: str
    flight_number: int
    name: str
    date_utc: str
    success: bool | None = None
    upcoming: bool
    details: str | None = None
    rocket_id: str
    rocket_name: str | None = None
    launchpad_name: str | None = None
    cores: list[CoreDetail] = []
    payloads: list[PayloadSummary] = []
    crew: list[CrewMember] = []
    links: LaunchLinks | None = None
    failures: list[LaunchFailure] = []
    fairings_recovered: bool | None = None
    fairings_reused: bool | None = None
    static_fire_date_utc: str | None = None
