"""Alle eksterne datakilder på ett sted.

status:
  verified  kalt og svaret kontrollert (her eller i teinum-fly)
  found     adressen står i offisiell metadata/dokumentasjon, ikke kalt herfra
  todo      endepunktet er ikke kjent; finnes via metadata i fase 0

Ikke legg inn adresser som ikke er funnet i en kilde. Se docs/datakilder.md for lisens og kreditering.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    status: str
    endpoint: str | None
    metadata: str | None
    license: str
    note: str = ""


SOURCES: list[Source] = [
    Source("dtm", "Nasjonal høydemodell DTM 1 m (Kartverket)", "verified",
           "https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25833", None, "CC BY 4.0",
           "dekning nhm_dtm_topo_25833; verifisert i teinum-fly"),
    Source("dom", "Nasjonal høydemodell DOM 1 m (Kartverket)", "verified",
           "https://wcs.geonorge.no/skwms1/wcs.hoyde-dom-nhm-25833", None, "CC BY 4.0",
           "dekning nhm_dom_topo_25833; verifisert i teinum-fly"),
    Source("n50", "N50 Kartdata (Kartverket)", "verified",
           "https://nedlasting.geonorge.no/geonorge/Basisdata/N50Kartdata/FGDB/Basisdata_{county}_25833_N50Kartdata_FGDB.zip",
           None, "CC BY 4.0", "filen verifisert i teinum-fly; jernbanelaget ikke lest ennå"),
    Source("banenettverk", "Jernbane – Banenettverk (Bane NOR)", "todo", None,
           "https://kartkatalog.geonorge.no/metadata/bane-nor-sf/jernbane-banenettverk/c3da3591-cded-4584-a4b1-bc61b7d1f4f2",
           "NLOD", "WFS-metadata: uuid 05cb3f1b-51e7-455f-9c4c-b21f5d99cce2"),
    Source("banenettverk_lr", "Jernbane – Banenettverk – Lineære referanser (Bane NOR)", "todo", None,
           "uuid dc4b671f-f354-4e1f-a23b-dd717ae48e1b", "NLOD", "FGDB, UTM 32"),
    Source("fkb_bane", "FKB-Bane (Geovekst)", "found",
           "http://nedlasting2.geonorge.no/geonorge/ATOM-feeds/FKB_Bane_AtomFeedGML.xml",
           "uuid 3165138f-1461-44fe-8b10-eac44e08a10a", "sjekkes", "ATOM-feed oppgitt i metadata"),
    Source("rinf", "RINF / ERA Knowledge Graph", "found",
           "https://graph.data.era.europa.eu/repositories/rinf-plus", None, "sjekkes",
           "SPARQL; hvor detaljert norsk stigningsprofil er, er ukjent"),
]


def by_id(source_id: str) -> Source:
    for s in SOURCES:
        if s.id == source_id:
            return s
    raise KeyError(source_id)
