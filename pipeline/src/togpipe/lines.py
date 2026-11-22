"""Strekninger som kan bygges.

`fetch_bbox` er et grovt henteområde i WGS84 (lon_min, lat_min, lon_max, lat_max) med god margin, bare for
å avgrense nedlasting. Selve sporlinja kommer fra data (fase 1), aldri herfra.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LineDef:
    id: str
    name: str
    start_station: str
    end_station: str
    fetch_bbox: tuple[float, float, float, float]
    n50_county: str  # fylkeskode og navn slik det står i N50-filnavnet, f.eks. "46_Vestland"


LINES: dict[str, LineDef] = {
    "flam": LineDef(
        id="flam",
        name="Flåmsbana",
        start_station="Myrdal",
        end_station="Flåm",
        fetch_bbox=(7.04, 60.71, 7.22, 60.88),
        n50_county="46_Vestland",
    ),
}
