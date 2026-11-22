"""Sporet som 1D-akse.

En strekning er en polyline i UTM 33. Posisjonen langs den er s: meter fra første punkt, målt i
UTM-planet (ikke i terrenget, se CRS-regel 5 i CLAUDE.md). Alt langs sporet lagres som funksjon av s.

Sideavstand (offset) er positiv til HØYRE i økende s-retning.
"""

from __future__ import annotations

import math

import numpy as np


class Polyline:
    def __init__(self, points: np.ndarray | list[tuple[float, float]]):
        xy = np.asarray(points, dtype=np.float64)
        if xy.ndim != 2 or xy.shape[1] != 2 or len(xy) < 2:
            raise ValueError("trenger minst to punkter (øst, nord)")
        seg = np.hypot(*np.diff(xy, axis=0).T)
        if np.any(seg == 0):
            # Like punkter etter hverandre gir null-segmenter og deling på null i retning og projeksjon
            keep = np.concatenate([[True], seg > 0])
            xy = xy[keep]
            seg = seg[seg > 0]
            if len(xy) < 2:
                raise ValueError("alle punktene er like")
        self.xy = xy
        self.s = np.concatenate([[0.0], np.cumsum(seg)])

    @property
    def length(self) -> float:
        return float(self.s[-1])

    def _segment(self, s: np.ndarray) -> np.ndarray:
        """Indeks til segmentet som inneholder s (siste segment for s == lengden)."""
        return np.clip(np.searchsorted(self.s, s, side="right") - 1, 0, len(self.s) - 2)

    def point_at(self, s: float | np.ndarray) -> np.ndarray:
        """(øst, nord) i posisjon s. s utenfor [0, lengde] klemmes til endepunktene."""
        sa = np.clip(np.asarray(s, dtype=np.float64), 0.0, self.length)
        i = self._segment(sa)
        t = (sa - self.s[i]) / (self.s[i + 1] - self.s[i])
        return self.xy[i] + (self.xy[i + 1] - self.xy[i]) * t[..., None]

    def heading_at(self, s: float | np.ndarray) -> np.ndarray:
        """Rutenettretning i grader (0 = rutenett-nord, med klokka) for segmentet i posisjon s."""
        i = self._segment(np.clip(np.asarray(s, dtype=np.float64), 0.0, self.length))
        d = self.xy[i + 1] - self.xy[i]
        return np.degrees(np.arctan2(d[..., 0], d[..., 1])) % 360.0

    def project(self, east: float, north: float) -> tuple[float, float]:
        """Nærmeste punkt på linja: (s, sideavstand). Sideavstand positiv til høyre."""
        p = np.array([east, north])
        a, b = self.xy[:-1], self.xy[1:]
        ab = b - a
        seg_len2 = np.einsum("ij,ij->i", ab, ab)
        t = np.clip(np.einsum("ij,ij->i", p - a, ab) / seg_len2, 0.0, 1.0)
        foot = a + ab * t[:, None]
        d2 = np.einsum("ij,ij->i", p - foot, p - foot)
        k = int(np.argmin(d2))
        s = float(self.s[k] + t[k] * math.sqrt(seg_len2[k]))
        # Kryssprodukt: retning x (punkt - fot). Negativt = punktet ligger til høyre for retningen.
        cross = ab[k, 0] * (p[1] - foot[k, 1]) - ab[k, 1] * (p[0] - foot[k, 0])
        dist = math.sqrt(d2[k])
        return s, (-dist if cross > 0 else dist)

    def resample(self, step: float) -> tuple[np.ndarray, np.ndarray]:
        """Jevne prøver hver `step` meter, med siste punkt (s = lengden) alltid med. Gir (s, punkter)."""
        if step <= 0:
            raise ValueError("step må være positiv")
        s = np.arange(0.0, self.length, step)
        s = np.append(s, self.length)
        return s, self.point_at(s)
