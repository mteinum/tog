import numpy as np
import pytest

from togpipe.profile import GradeSection, Span, compare_sections, grade_permille, track_profile

S = np.arange(0, 2001, 10.0)


def test_constant_grade_survives_smoothing():
    # 55 promille over 2 km, som Flåmsbana på det bratteste
    ground = 100 + S * 0.055
    z = track_profile(S, ground, smooth_m=100)
    g = grade_permille(S, z)
    # Midt på er stigningen urørt; speiling i endene flater litt ut der
    assert g[20:-20] == pytest.approx(55, abs=1e-6)
    assert z[0] == pytest.approx(ground[0], abs=2.0)


def test_tunnel_is_straight_between_portals():
    ground = np.full_like(S, 200.0)
    mountain = (S > 500) & (S < 1500)
    ground[mountain] += 300 * np.sin(np.pi * (S[mountain] - 500) / 1000)  # fjellet over tunnelen
    z = track_profile(S, ground, [Span(500, 1500, "tunnel")], smooth_m=0)
    assert np.max(np.abs(z - 200)) < 1e-9


def test_tunnel_between_different_portal_heights():
    ground = np.where(S < 1000, 300.0, 250.0)
    ground[(S > 800) & (S < 1200)] = 900.0
    z = track_profile(S, ground, [Span(800, 1200, "tunnel")], smooth_m=0)
    inside = (S >= 800) & (S <= 1200)
    assert grade_permille(S[inside], z[inside]) == pytest.approx(-125, abs=1e-6)


def test_portal_median_ignores_single_bad_cell():
    ground = np.full_like(S, 100.0)
    ground[S == 790] = 160.0  # én støycelle like før portalen
    ground[(S > 800) & (S < 1000)] = 500.0
    z = track_profile(S, ground, [Span(800, 1000, "tunnel")], smooth_m=0)
    assert z[S == 900][0] == pytest.approx(100.0)


def test_bridge_ignores_valley_floor():
    ground = np.full_like(S, 50.0)
    ground[(S > 1000) & (S < 1100)] = 5.0  # elva under brua
    z = track_profile(S, ground, [Span(1000, 1100, "bridge")], smooth_m=0)
    assert z.min() == pytest.approx(50.0)


def test_non_uniform_s_rejected():
    with pytest.raises(ValueError):
        track_profile(np.array([0, 10, 25, 30.0]), np.zeros(4))


def test_bad_span_rejected():
    with pytest.raises(ValueError):
        Span(10, 10, "tunnel")
    with pytest.raises(ValueError):
        Span(0, 10, "viaduct")


def test_compare_sections():
    z = 100 + S * 0.020
    res = compare_sections(S, z, [GradeSection(0, 1000, 20.0), GradeSection(1000, 2000, 25.0)])
    assert res[0]["diff"] == pytest.approx(0)
    assert res[1]["model"] == pytest.approx(20)
    assert res[1]["diff"] == pytest.approx(-5)
