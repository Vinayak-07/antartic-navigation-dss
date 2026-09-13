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
    south_u, south_v = meteorological_to_uv(10.0, 180.0)
    assert round(south_u, 8) == 0.0
    assert round(south_v, 8) == 10.0
    west_u, west_v = meteorological_to_uv(10.0, 270.0)
    assert round(west_u, 8) == 10.0
    assert round(west_v, 8) == 0.0


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


def test_grid_rows_are_uniform_and_last_row_lands_exactly_on_the_south_bound():
    # The renderer derives every row as la1 - j*dy with one uniform dy and never
    # reads la2: an uneven final row (e.g. the 47-degree operational span stepped
    # at 5 degrees) distorts all interpolation in the southern band.
    request = WindGridRequest(south=-75, north=-28, west=10, east=42, spacing=2)
    latitudes, longitudes, dx, dy = request.grid_axes()
    assert latitudes[0] == -28
    assert abs(latitudes[-1] - (-75)) < 1e-6
    expected_dy = 47.0 / 24.0
    assert abs(dy - expected_dy) < 1e-9
    for index in range(len(latitudes)):
        assert abs(latitudes[index] - (-28 - index * dy)) < 1e-5
    assert abs(longitudes[-1] - 42) < 1e-6
    for index in range(len(longitudes)):
        assert abs(longitudes[index] - (10 + index * dx)) < 1e-5


def test_field_header_covers_exactly_the_requested_bounds():
    # Same size as the map: the declared grid must span the full requested
    # rectangle under the renderer's la1 - j*dy / lo1 + i*dx cell math, with the
    # effective spacing raised only as far as the provider call budget demands.
    provider = FixedWindProvider()
    field = WindFieldService(provider=provider).get_field(
        WindGridRequest(south=-75, north=-28, west=10, east=90, spacing=2)
    )
    u_record, v_record = field["field"]
    header = u_record["header"]
    ny = header["ny"]
    nx = header["nx"]
    assert abs(header["la1"] - (header["la2"] + (ny - 1) * header["dy"])) < 1e-4
    assert abs(header["lo1"] + (nx - 1) * header["dx"] - header["lo2"]) < 1e-4
    assert header["la1"] == -28
    assert abs(header["la2"] - (-75)) < 1e-4
    assert header["lo1"] == 10
    assert abs(header["lo2"] - 90) < 1e-4
    assert nx * ny <= 550  # every grid location is one provider call per minute
    assert len(u_record["data"]) == nx * ny
    assert len(v_record["data"]) == nx * ny
    metadata = field["metadata"]
    assert metadata["bounds"]["south"] == -75
    assert metadata["bounds"]["east"] == 90
    assert metadata["requested_spacing_deg"] == 2.0


def test_oversized_visible_extent_coarsens_instead_of_failing():
    # A large visible map extent must still resolve: the builder raises the
    # effective spacing within the call budget rather than rejecting the view.
    request = WindGridRequest(south=-89, north=-20, west=-180, east=180, spacing=1)
    latitudes, longitudes, dx, dy = request.grid_axes()
    assert len(latitudes) * len(longitudes) <= 550
    assert request.effective_spacing() > 1.0
    assert abs(latitudes[0] - (-20)) < 1e-6
    assert abs(latitudes[-1] - (-89)) < 1e-6
    assert abs(longitudes[0] - (-180)) < 1e-6
    assert abs(longitudes[-1] - 180) < 1e-6
