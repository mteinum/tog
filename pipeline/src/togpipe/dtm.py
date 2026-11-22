"""Høydedata: Kartverket DTM og DOM (Nasjonal høydemodell) via WCS.  (Kopiert fra teinum-fly.)

DTM (terreng):   https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25833, nhm_dtm_topo_25833
DOM (overflate): https://wcs.geonorge.no/skwms1/wcs.hoyde-dom-nhm-25833, nhm_dom_topo_25833
Begge: 1 m, EPSG:25833, høyder i NN2000. DOM har med bruer, bygninger og trær.

Tjenesten tillater maks 3840 x 2160 piksler per kall, så utsnittet hentes
som fliser og caches i data/raw/. Slett cachen for å hente på nytt.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
import requests

from . import USER_AGENT
from .grid import GridSpec

WCS_URL = "https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25833"
COVERAGE = "nhm_dtm_topo_25833"
DOM_URL = "https://wcs.geonorge.no/skwms1/wcs.hoyde-dom-nhm-25833"
DOM_COVERAGE = "nhm_dom_topo_25833"
MAX_COLS, MAX_ROWS = 3840, 2160
TILE_PX = 1280
# Målt mot blokkmiddel av 1 m-data: bilinear gir RMSE 0,25 m, standard
# (nearest) 0,92 m. Se docs/resampling.md.
INTERPOLATION = "bilinear"


def _fetch_tile(
    path: Path, west: float, south: float, east: float, north: float, w: int, h: int,
    url: str = WCS_URL, coverage: str = COVERAGE, interpolation: str | None = INTERPOLATION,
) -> None:
    params = {
        "SERVICE": "WCS",
        "VERSION": "1.0.0",
        "REQUEST": "GetCoverage",
        "COVERAGE": coverage,
        "CRS": "EPSG:25833",
        "BBOX": f"{west},{south},{east},{north}",
        "WIDTH": w,
        "HEIGHT": h,
        "FORMAT": "GeoTIFF",
    }
    if interpolation:
        params["INTERPOLATION"] = interpolation
    r = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=300)
    r.raise_for_status()
    if "tiff" not in r.headers.get("content-type", ""):
        raise RuntimeError(f"WCS svarte ikke med GeoTIFF: {r.text[:500]}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(r.content)


def load_source_dom(grid: GridSpec, res: float, raw_dir: Path) -> np.ndarray:
    """Som load_source_dtm, men overflatemodellen (med bygninger og trær)."""
    return load_source_dtm(grid, res, raw_dir, url=DOM_URL, coverage=DOM_COVERAGE, prefix="dom")


def load_source_dtm(
    grid: GridSpec, res: float, raw_dir: Path, url: str = WCS_URL, coverage: str = COVERAGE, prefix: str = "dtm"
) -> np.ndarray:
    """Hent DTM for rutenettets utstrekning med oppløsning `res` (m). Rad 0 = nord."""
    factor = grid.cell / res
    if factor != int(factor):
        raise ValueError("cellestørrelsen må være et helt multiplum av kildeoppløsningen")
    w, h = grid.width * int(factor), grid.height * int(factor)
    out = np.empty((h, w), dtype=np.float32)
    for r0 in range(0, h, TILE_PX):
        for c0 in range(0, w, TILE_PX):
            th, tw = min(TILE_PX, h - r0), min(TILE_PX, w - c0)
            t_west = grid.west + c0 * res
            t_north = grid.north - r0 * res
            path = raw_dir / f"{prefix}{res:g}m_r{r0}_c{c0}.tif"
            if path.exists():
                # Filnavnet sier rad og kolonne, ikke hvor i verden flisa ligger. Er utsnittet flyttet siden sist,
                # er den lagrede flisa for et annet sted: kast den og hent på nytt.
                with rasterio.open(path) as old:
                    stale = abs(old.transform.c - t_west) > 1e-6 or abs(old.transform.f - t_north) > 1e-6 or (old.width, old.height) != (tw, th)
                if stale:
                    print(f"  {path.name}: lagret for et annet utsnitt, hentes på nytt")
                    path.unlink()
            if not path.exists():
                print(f"  WCS: {path.name}")
                _fetch_tile(path, t_west, t_north - th * res, t_west + tw * res, t_north, tw, th, url=url, coverage=coverage)
            with rasterio.open(path) as src:
                # Stol ikke på at tjenesten leverte det vi ba om
                assert src.crs.to_epsg() == 25833, src.crs
                assert (src.width, src.height) == (tw, th), (src.width, src.height)
                t = src.transform
                assert abs(t.c - t_west) < 1e-6 and abs(t.f - t_north) < 1e-6, t
                assert abs(t.a - res) < 1e-9 and abs(t.e + res) < 1e-9, t
                out[r0 : r0 + th, c0 : c0 + tw] = src.read(1)
    return out


def load_dom_window(west: int, south: int, east: int, north: int, raw_dir: Path) -> tuple[np.ndarray, rasterio.Affine]:
    """DOM i full oppløsning (1 m, ingen resampling) for et lite vindu på hele meter."""
    w, h = east - west, north - south
    if w > MAX_COLS or h > MAX_ROWS:
        raise ValueError(f"DOM-vindu {w} x {h} er større enn tjenesten tillater")
    path = raw_dir / f"dom1m_{west}_{south}_{east}_{north}.tif"
    if not path.exists():
        _fetch_tile(path, west, south, east, north, w, h, url=DOM_URL, coverage=DOM_COVERAGE, interpolation=None)
    with rasterio.open(path) as src:
        assert src.crs.to_epsg() == 25833, src.crs
        assert (src.width, src.height) == (w, h), (src.width, src.height)
        t = src.transform
        assert abs(t.c - west) < 1e-6 and abs(t.f - north) < 1e-6 and abs(t.a - 1) < 1e-9, t
        return src.read(1), t
