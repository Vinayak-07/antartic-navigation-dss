from backend.wind import WindFieldService, WindGridRequest, WindProviderError, meteorological_to_uv


class FixedWindProvider:
    name = "Test weather model"
    model = "test model"

    def __init__(self):
        self.calls = 0

    def fetch(self, points):
        self.calls += 1
        return [
            {"current": {"wind_speed_10m": 10.0, "wind_direction_10m": 0.0, "time": "2026-01-01T00:00"}}
            for _ in points
        ]


class FailingWindProvider(FixedWindProvider):
    def fetch(self, points):
        self.calls += 1
        raise WindProviderError("provider down")


def test_meteorological_direction_conversion_has_correct_cardinal_vectors():
    assert meteorological_to_uv(10.0, 0.0) == (0.0, -10.0)
    east_u, east_v = meteorological_to_uv(10.0, 90.0)
    assert round(east_u, 8) == -10.0
    assert round(east_v, 8) == 0.0


def test_wind_field_is_north_to_south_and_has_matching_component_lengths():
    provider = FixedWindProvider()
    field = WindFieldService(provider=provider).get_field(
        WindGridRequest(south=-70, north=-66, west=10, east=14, spacing=2)
    )
    u_record, v_record = field["field"]
    assert u_record["header"]["la1"] == -66
    assert u_record["header"]["la2"] == -70
    assert u_record["header"]["nx"] == 3
    assert u_record["header"]["ny"] == 3
    assert len(u_record["data"]) == 9
    assert len(v_record["data"]) == 9
    assert all(value == 0.0 for value in u_record["data"])
    assert all(value == -10.0 for value in v_record["data"])
    assert field["metadata"]["row_order"] == "north_to_south"
    assert field["metadata"]["cached"] is False


def test_wind_field_cache_avoids_a_second_provider_request():
    provider = FixedWindProvider()
    service = WindFieldService(provider=provider)
    request = WindGridRequest(south=-70, north=-66, west=10, east=14, spacing=2)
    service.get_field(request)
    cached = service.get_field(request)
    assert provider.calls == 1
    assert cached["metadata"]["cached"] is True


def test_provider_failure_returns_the_last_cached_field_as_stale():
    provider = FixedWindProvider()
    service = WindFieldService(provider=provider)
    request = WindGridRequest(south=-70, north=-66, west=10, east=14, spacing=2)
    service.get_field(request)
    provider.fetch = FailingWindProvider().fetch
    stale = service.get_field(request, refresh=True)
    assert stale["metadata"]["stale"] is True
    assert stale["metadata"]["cached"] is True


def test_invalid_wind_grid_is_rejected_before_provider_request():
    provider = FixedWindProvider()
    service = WindFieldService(provider=provider)
    try:
        service.get_field(WindGridRequest(south=-40, north=-70, west=10, east=14, spacing=2))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid bounds should fail")
    assert provider.calls == 0
