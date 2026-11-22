import math

import numpy as np
import pytest

from togpipe.chainage import Polyline

# L-formet linje: 100 m nordover, så 50 m østover. Østverdier negative som på Vestlandet.
L = Polyline([(-40000, 6700000), (-40000, 6700100), (-39950, 6700100)])


def test_length_and_points():
    assert L.length == pytest.approx(150)
    assert L.point_at(0) == pytest.approx([-40000, 6700000])
    assert L.point_at(50) == pytest.approx([-40000, 6700050])
    assert L.point_at(125) == pytest.approx([-39975, 6700100])
    assert L.point_at(150) == pytest.approx([-39950, 6700100])


def test_point_at_clamps():
    assert L.point_at(-10) == pytest.approx(L.point_at(0))
    assert L.point_at(999) == pytest.approx(L.point_at(150))


def test_heading_is_grid_bearing():
    assert L.heading_at(50) == pytest.approx(0)
    assert L.heading_at(120) == pytest.approx(90)


def test_project_offset_positive_to_the_right():
    # Kjøreretning nordover på første segment: øst er til høyre
    s, off = L.project(-39990, 6700040)
    assert s == pytest.approx(40)
    assert off == pytest.approx(10)
    s, off = L.project(-40010, 6700040)
    assert off == pytest.approx(-10)
    # Andre segment går østover: sør er til høyre
    s, off = L.project(-39970, 6700090)
    assert s == pytest.approx(130)
    assert off == pytest.approx(10)


def test_project_roundtrip():
    for s in [0, 33.3, 100, 140]:
        e, n = L.point_at(s)
        s2, off = L.project(e, n)
        assert s2 == pytest.approx(s) and off == pytest.approx(0, abs=1e-9)


def test_duplicate_points_are_dropped():
    p = Polyline([(0, 0), (0, 0), (3, 4), (3, 4)])
    assert p.length == pytest.approx(5)
    assert len(p.xy) == 2


def test_resample_includes_end():
    s, pts = L.resample(40)
    assert list(s) == [0, 40, 80, 120, 150]
    assert pts[-1] == pytest.approx([-39950, 6700100])


def test_vectorised_point_at():
    pts = L.point_at(np.array([0, 100, 150]))
    assert pts.shape == (3, 2)
    assert math.hypot(*(pts[1] - pts[0])) == pytest.approx(100)
