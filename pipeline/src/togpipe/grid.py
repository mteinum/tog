"""Spillets lokale rutenett: UTM-meter / cellestørrelse.  (Kopiert fra teinum-fly.)

Kontinuerlige rutenettkoordinater (x, y):
  x = (øst - vest) / celle      øker mot øst
  y = (nord_kant - nord) / celle  øker mot SØR (rasterkonvensjon, rad 0 = nord)
Heltall ligger på cellekanter; celle (kol, rad) har sentrum i (kol+0.5, rad+0.5).
"""

from __future__ import annotations

from dataclasses import dataclass

from affine import Affine


@dataclass(frozen=True)
class GridSpec:
    west: float
    north: float
    cell: float
    width: int
    height: int

    @property
    def east(self) -> float:
        return self.west + self.width * self.cell

    @property
    def south(self) -> float:
        return self.north - self.height * self.cell

    @property
    def transform(self) -> Affine:
        return Affine(self.cell, 0, self.west, 0, -self.cell, self.north)

    def utm_to_grid(self, east: float, north: float) -> tuple[float, float]:
        return (east - self.west) / self.cell, (self.north - north) / self.cell

    def grid_to_utm(self, x: float, y: float) -> tuple[float, float]:
        return self.west + x * self.cell, self.north - y * self.cell

    @staticmethod
    def centered(east: float, north: float, cell: float, size: int) -> "GridSpec":
        """Kvadratisk rutenett sentrert på punktet, snappet til hele celler."""
        half = size * cell / 2
        west = round((east - half) / cell) * cell
        top = round((north + half) / cell) * cell
        return GridSpec(west, top, cell, size, size)
