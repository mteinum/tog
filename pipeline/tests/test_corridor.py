import pytest

from togpipe.chainage import Polyline
from togpipe.corridor import chunk_overhead, chunks, estimate_bytes


def test_straight_line_north():
    line = Polyline([(-40000, 6700000), (-40000, 6702500)])
    cs = chunks("t", line, chunk_m=1000, half_width_m=1500, cell=10)
    assert [c.index for c in cs] == [0, 1, 2]
    assert cs[-1].s1 == pytest.approx(2500)
    g = cs[0].grid
    assert g.west == -41500 and g.east == -38500
    assert g.south == 6698500 and g.north == 6702500
    assert (g.width, g.height) == (300, 400)


def test_grid_snapped_to_cells():
    line = Polyline([(-40003.7, 6700001.2), (-39001.1, 6700998.9)])
    for c in chunks("t", line, cell=10):
        for v in (c.grid.west, c.grid.north):
            assert v % 10 == pytest.approx(0, abs=1e-9)


def test_track_inside_every_chunk_with_margin():
    line = Polyline([(0, 0), (800, 600), (800, 2000), (-300, 2600)])
    for c in chunks("t", line, half_width_m=1500):
        for s in (c.s0, (c.s0 + c.s1) / 2, c.s1):
            e, n = line.point_at(s)
            assert c.grid.west + 1500 <= e <= c.grid.east - 1500
            assert c.grid.south + 1500 <= n <= c.grid.north - 1500


def test_diagonal_costs_more_than_straight():
    straight = chunks("a", Polyline([(0, 0), (0, 10000)]))
    diagonal = chunks("b", Polyline([(0, 0), (7071, 7071)]))
    assert chunk_overhead(diagonal, 1500) > chunk_overhead(straight, 1500)


def test_estimate_whole_network_order_of_magnitude():
    # 4000 km: 10 m-ring 3 km bred (120 mill. celler) + 50 m-ring ut til 10 km (6,8 mill. celler), 6 byte per celle
    b = estimate_bytes(4000)
    assert b == pytest.approx(4000e3 * 3000 / 100 * 6 + 4000e3 * 17000 / 2500 * 6)
    assert 0.5e9 < b < 1.0e9
