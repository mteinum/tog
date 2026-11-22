# Datakilder

Status per 2026-11-22 (fase 0 ikke startet). «Verifisert» betyr at endepunktet er kalt og svaret
kontrollert i dette prosjektet eller i fly. «Funnet» betyr at adressen står i offisiell metadata eller
dokumentasjon, men ikke er kalt herfra. Maskinlesbar utgave: `pipeline/src/togpipe/sources.py`.

## Sporgeometri og struktur

### Jernbane – Banenettverk – Bane NOR

| | |
|---|---|
| Innhold | Referanselinjer for strekningene i statens jernbaneinfrastruktur (og museumsbaner), noder i et topologisk nettverk, kilometrering etter Bane NORs lineære referanser. Én linje per strekning, ikke per spor |
| Metadata | Geonorge kartkatalog, uuid `c3da3591-cded-4584-a4b1-bc61b7d1f4f2` (datasett), `05cb3f1b-51e7-455f-9c4c-b21f5d99cce2` (WFS). Lineære referanser: `dc4b671f-f354-4e1f-a23b-dd717ae48e1b` |
| Format | SOSI, GML 3.2.1, FGDB, PostGIS; WFS og WMS. Lineære referanser kun FGDB, UTM 32 |
| Lisens | NLOD. Kreditering: «Inneheld data under Norsk lisens for offentlige data (NLOD) gjort tilgjengeleg av Bane NOR SF» |
| Brukt til | Strekningenes struktur, rekkefølge og kilometrering |
| Status | Funnet. WFS-adressen må hentes fra metadata i fase 0 |

### FKB-Bane – Geovekst/Kartverket

| | |
|---|---|
| Innhold | Overbygningen: spor (enkeltspor, sporveksler) og plattformkanter. Bane NOR viser hit for enkeltspor |
| Metadata | uuid `3165138f-1461-44fe-8b10-eac44e08a10a`. ATOM-feed oppgitt i metadata: `http://nedlasting2.geonorge.no/geonorge/ATOM-feeds/FKB_Bane_AtomFeedGML.xml` |
| Lisens | Åpne data (FKB). Sjekk eksakt lisens i fase 0 |
| Merknad | Dekning og detaljnivå varierer mellom områder. Må sjekkes langs hele nettet |
| Status | Funnet |

### N50 Kartdata – Kartverket (jernbane)

| | |
|---|---|
| Fil | `https://nedlasting.geonorge.no/geonorge/Basisdata/N50Kartdata/FGDB/Basisdata_<fylke>_25833_N50Kartdata_FGDB.zip` |
| Innhold | Jernbane i `N50_Samferdsel_senterlinje`, med `medium` (U = tunnel, L = bru). Objekttype for jernbane må leses ut i fase 0 |
| Lisens | CC BY 4.0, © Kartverket |
| Brukt til | Reserve for sporlinje, og tunneler og bruer som s-intervaller |
| Status | Filen er verifisert i fly (46_Vestland m.fl.). Jernbanelaget er ikke lest ennå |

## Egenskaper langs sporet

### RINF – ERAs register over jernbaneinfrastruktur

| | |
|---|---|
| Innhold | Strekninger, driftspunkter, spor, tunneler, plattformer, energiforsyning, signalsystem, største tillatte hastighet, stigningsprofil |
| Tilgang | ERA Knowledge Graph (SPARQL). Endepunkt funnet: `https://graph.data.era.europa.eu/repositories/rinf-plus` |
| Merknad | Bane NOR planlegger å bruke RINF som hovedkilde i Network Statement fra R27. Hvor detaljert den norske stigningsprofilen er, er ukjent: hovedspørsmålet i fase 0 |
| Lisens | Sjekkes i fase 0 |
| Status | Funnet |

### Network Statement – Bane NOR

Vedlegg med linjehastighet og strekningsbeskrivelser
(`https://oppslagsverk.banenor.no/en/network-statement/annexes-2026/line-speed/`). Kart og PDF, ikke
maskinlesbart. Brukes som fasit for kontroll, ikke som datakilde.

### OpenStreetMap / OpenRailwayMap

Signaler, planoverganger, kontaktledning, `maxspeed`. ODbL. Reserve der RINF mangler noe. Hentes for
hånd til data/osm/ som i fly (`flypipe rails` viser hvordan).

## Terreng (som i fly, verifisert der)

- DTM 1 m: WCS `https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25833`, dekning `nhm_dtm_topo_25833`. CC BY 4.0, © Kartverket
- DOM 1 m: WCS `https://wcs.geonorge.no/skwms1/wcs.hoyde-dom-nhm-25833`, dekning `nhm_dom_topo_25833`. CC BY 4.0, © Kartverket
- N50 arealdekke og stedsnavn, Matrikkelen: se fly/docs/datakilder.md

## Trafikk (fase 5)

Entur: stoppestedsregisteret (NSR, med plattformer), rutedata (NeTEx) og sanntid (SIRI). NLOD.
fly bruker allerede Entur for tog og busser i sanntid (`web/public/transit/`).

## Kjente tall til kontroll (Flåmsbana)

Myrdal ca. 867 moh, Flåm ca. 2 moh, lengde ca. 20 km, største stigning 55 ‰. Fra allmenn kunnskap,
skal bekreftes mot Bane NOR i fase 0 før de brukes som fasit i tester.
