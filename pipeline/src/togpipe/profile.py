"""Sporets høydeprofil.

Sporet følger ikke terrenget: det går i skjæringer, på fyllinger, i tunneler og over bruer. Profilen
bygges slik:

1. Terrenghøyde (DTM) samplet langs sporet med jevn avstand i s.
2. I tunneler og på bruer sier DTM ingenting om sporet (fjelloverflate eller elvebunn). Der erstattes
   høyden med en rett linje mellom portalene/landkarene. Portalhøyden tas som medianen av DTM like utenfor,
   så en enkelt dårlig celle ved portalen ikke gir et hopp.
3. Glidende middel over `smooth_m` meter. Sporet kan ikke følge 10 m-støy i terrenget.

Resultatet er en modell, ikke en måling. Den kontrolleres mot Bane NORs/RINFs stigningsprofil
(`compare_sections`), og avvik rapporteres.

Lineær interpolasjon i lange tunneler er en forenkling: mange tunneler har et toppunkt (drenering mot
begge ender). Der RINF har stigningen inne i tunnelen, skal den brukes i stedet (fase 1).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Span:
    """Et s-intervall der DTM ikke gjelder for sporet."""

    start: float
    end: float
    kind: str  # "tunnel" eller "bridge"

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError(f"tomt intervall {self.start}-{self.end}")
        if self.kind not in ("tunnel", "bridge"):
            raise ValueError(f"ukjent type {self.kind}")


@dataclass(frozen=True)
class GradeSection:
    """Stigning i promille over et s-intervall, fra en ekstern kilde (RINF, Bane NOR)."""

    start: float
    end: float
    permille: float


def _check_uniform(s: np.ndarray) -> float:
    step = np.diff(s)
    if len(step) == 0 or not np.allclose(step[:-1], step[0], rtol=1e-6) or step[-1] > step[0] * (1 + 1e-6):
        raise ValueError("s må ha jevn avstand (siste steg kan være kortere)")
    return float(step[0])


def _portal_height(s: np.ndarray, ground: np.ndarray, at: float, outward: int, window: float) -> float:
    """Median av terrenget i `window` meter utenfor portalen (outward = -1 før, +1 etter)."""
    lo, hi = (at - window, at) if outward < 0 else (at, at + window)
    m = (s >= lo) & (s <= hi)
    if not m.any():
        return float(np.interp(at, s, ground))
    return float(np.median(ground[m]))


def track_profile(
    s: np.ndarray, ground: np.ndarray, spans: list[Span] = (), smooth_m: float = 50.0, portal_window_m: float = 30.0
) -> np.ndarray:
    """Sporets høyde (NN2000) i hvert punkt i s."""
    s = np.asarray(s, dtype=np.float64)
    ground = np.asarray(ground, dtype=np.float64)
    if s.shape != ground.shape:
        raise ValueError("s og ground må ha samme form")
    step = _check_uniform(s)
    z = ground.copy()
    for sp in sorted(spans, key=lambda x: x.start):
        z0 = _portal_height(s, ground, sp.start, -1, portal_window_m)
        z1 = _portal_height(s, ground, sp.end, +1, portal_window_m)
        m = (s >= sp.start) & (s <= sp.end)
        z[m] = np.interp(s[m], [sp.start, sp.end], [z0, z1])
    n = int(round(smooth_m / step))
    if n >= 2:
        # Glidende middel med speiling i endene, så endestasjonenes høyde ikke trekkes mot null
        pad = n // 2
        zp = np.pad(z, (pad, n - 1 - pad), mode="reflect")
        z = np.convolve(zp, np.ones(n) / n, mode="valid")
    return z


def grade_permille(s: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Stigning i promille mellom nabopunkter (lengde len(s) - 1). Positiv = oppover i økende s."""
    return np.diff(z) / np.diff(s) * 1000.0


def compare_sections(s: np.ndarray, z: np.ndarray, sections: list[GradeSection]) -> list[dict]:
    """Gjennomsnittlig stigning i modellen over hver seksjon, mot oppgitt verdi."""
    out = []
    for sec in sections:
        z0, z1 = np.interp([sec.start, sec.end], s, z)
        model = (z1 - z0) / (sec.end - sec.start) * 1000.0
        out.append({"start": sec.start, "end": sec.end, "given": sec.permille,
                    "model": round(float(model), 2), "diff": round(float(model - sec.permille), 2)})
    return out
