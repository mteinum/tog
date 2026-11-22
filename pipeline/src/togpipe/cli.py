"""togpipe: kommandolinje."""

from __future__ import annotations

import argparse

from .corridor import estimate_bytes
from .lines import LINES
from .sources import SOURCES


def _lines(_args) -> None:
    for ln in LINES.values():
        print(f"{ln.id:10} {ln.name} ({ln.start_station} - {ln.end_station}), N50 {ln.n50_county}")


def _sources(_args) -> None:
    for s in SOURCES:
        print(f"[{s.status:8}] {s.id:16} {s.name}")
        print(f"           {s.endpoint or '(endepunkt ukjent)'}")
        if s.note:
            print(f"           {s.note}")


def _estimate(args) -> None:
    b = estimate_bytes(args.km)
    print(f"{args.km:g} km korridor (10 m ±1,5 km, 50 m ±10 km): ca. {b / 1e6:.0f} MB ukomprimert")


def main() -> None:
    p = argparse.ArgumentParser(prog="togpipe")
    sub = p.add_subparsers(required=True)
    sub.add_parser("lines", help="strekninger som er definert").set_defaults(func=_lines)
    sub.add_parser("sources", help="endepunkter og verifiseringsstatus").set_defaults(func=_sources)
    e = sub.add_parser("estimate", help="datamengde for N km korridor")
    e.add_argument("km", type=float)
    e.set_defaults(func=_estimate)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
