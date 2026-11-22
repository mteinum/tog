"""Korridorfliser: terreng bare i et bånd rundt sporet.

Strekningen deles i biter på `chunk_m` meter langs s. Hver bit får et eget aksejustert rutenett
(GridSpec) som dekker sporet i biten pluss `half_width_m` til hver side, snappet til hele celler.
Nabobiter overlapper; spillet laster bitene etter hvert som toget nærmer seg.

Aksejusterte bokser er enkle og passer rett inn i fly-koden, men koster plass der sporet går på skrå
(opptil ca. 1,4x for diagonale strekninger, mer i krappe kurver). Om det lønner seg å dreie rutenettet
etter sporet, avgjøres i fase 2 med tall fra `chunk_overhead`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .chainage import Polyline
from .grid import GridSpec


@dataclass(frozen=True)
class Chunk:
    line_id: str
    index: int
    s0: float
    s1: float
    grid: GridSpec


def chunks(line_id: str, line: Polyline, chunk_m: float = 1000.0, half_width_m: float = 1500.0,
           cell: float = 10.0, sample_m: float = 10.0) -> list[Chunk]:
    out = []
    n = max(1, math.ceil(line.length / chunk_m))
    for i in range(n):
        s0, s1 = i * chunk_m, min((i + 1) * chunk_m, line.length)
        s = np.append(np.arange(s0, s1, sample_m), s1)
        p = line.point_at(s)
        west = math.floor((p[:, 0].min() - half_width_m) / cell) * cell
        east = math.ceil((p[:, 0].max() + half_width_m) / cell) * cell
        south = math.floor((p[:, 1].min() - half_width_m) / cell) * cell
        north = math.ceil((p[:, 1].max() + half_width_m) / cell) * cell
        grid = GridSpec(west, north, cell, int(round((east - west) / cell)), int(round((north - south) / cell)))
        out.append(Chunk(line_id, i, s0, s1, grid))
    return out


def chunk_overhead(cs: list[Chunk], half_width_m: float) -> float:
    """Celler i bitene delt på cellene et ideelt bånd (lengde x 2 x halvbredde) ville trengt."""
    if not cs:
        return 0.0
    cell = cs[0].grid.cell
    used = sum(c.grid.width * c.grid.height for c in cs)
    ideal = sum(c.s1 - c.s0 for c in cs) * 2 * half_width_m / cell**2
    return used / ideal


def estimate_bytes(length_km: float, rings: list[tuple[float, float]] = ((10.0, 1500.0), (50.0, 10000.0)),
                   bytes_per_cell: int = 2 + 3 + 1) -> int:
    """Grovt anslag for datamengde, uten overlapp og komprimering.

    rings: (cellestørrelse, halvbredde). Hver ring dekker båndet utenfor ringen innenfor.
    bytes_per_cell: høyde (uint16) + farge (RGB) + overflateklasse (uint8).
    """
    total, inner = 0.0, 0.0
    for cell, half in rings:
        total += length_km * 1000 * 2 * (half - inner) / cell**2 * bytes_per_cell
        inner = half
    return int(total)
