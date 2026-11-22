import pytest

from togpipe.crs import utm32_to_utm33, utm33_to_wgs84, wgs84_to_utm33


def test_roundtrip_flam():
    # Flåm, grovt (lon, lat). Vest for sentralmeridianen, men på 60,9° N er østverdien fortsatt positiv
    # (ca. 72 km). Negative østverdier gjelder lenger vest/sør, f.eks. Sola og Flesland.
    e, n = wgs84_to_utm33(7.114, 60.863)
    assert 60_000 < e < 85_000 and 6_765_000 < n < 6_780_000
    lon, lat = utm33_to_wgs84(e, n)
    assert (lon, lat) == pytest.approx((7.114, 60.863), abs=1e-9)


def test_utm32_to_utm33_matches_via_wgs84():
    from pyproj import Transformer

    to32 = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)
    e32, n32 = to32.transform(7.114, 60.863)
    assert utm32_to_utm33(e32, n32) == pytest.approx(wgs84_to_utm33(7.114, 60.863), abs=0.01)
