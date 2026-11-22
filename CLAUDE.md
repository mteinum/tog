# tog

Togsimulator (WebGL) langs det norske jernbanenettet, bygget på åpne norske data.
Søsterprosjekt til [teinum-fly](https://github.com/mteinum/fly): samme stil, samme CRS-regler,
samme krav til ryddig og reproduserbar GIS. Inspirasjon for følelsen: slowroads.io.

Pitchen er at alt er ekte: hver kurve, tunnel, stigning og fartsgrense kommer fra data.
Det som ikke er det, merkes som syntetisk.

## Arkitektur

```
pipeline/   Python 3.12 + uv. Henter og prosesserer data -> web/public/data/<strekning>/
  src/togpipe/
    crs.py        ALL koordinattransformasjon (WGS84 <-> UTM 33), konvergens. Kopiert fra fly
    grid.py       GridSpec: UTM-meter <-> rutenettceller. Kopiert fra fly
    dtm.py        Kartverket DTM og DOM via WCS, cache i data/raw/. Kopiert fra fly
    lines.py      definisjon av strekninger (id, navn, endestasjoner, grovt henteområde, N50-fylke)
    sources.py    alle eksterne endepunkter på ett sted, med verifiseringsstatus
    chainage.py   Polyline: sporet som 1D-akse. s (meter fra start) <-> (øst, nord), retning, projeksjon
    profile.py    sporets høydeprofil: DTM langs sporet, tunneler og bruer interpolert, glatting, stigning i promille
    corridor.py   korridorfliser: strekningen delt i biter langs s, hver med eget rutenett
    cli.py        `togpipe ...`
web/        (fase 3) Vite + TypeScript + three.js, rendereren hentes fra fly
docs/       datakilder.md, ai-logg.md
data/raw/   cache av nedlastede rådata (ikke i git)
```

## Kjernebegreper

- **Strekning** (`lines.py`): en sammenhengende linje som spilles, f.eks. `flam` (Flåmsbana).
- **s**: avstand langs sporet i meter fra strekningens start, målt i UTM-planet. Alt langs sporet
  (høyde, stigning, fartsgrense, tunneler, stasjoner) lagres som funksjon av s.
- **Kilometrering**: Bane NORs km-verdier (fra Oslo S) er ikke det samme som s. Koblingen går via
  Bane NORs lineære referanser og lagres som en egen tabell. Bland dem aldri.
- **Sideavstand**: positiv til HØYRE i økende s-retning.
- **Korridor**: terreng lagres bare i et bånd rundt sporet. 10 m-celler ±1,5 km, grovere lenger ut.

## CRS-regler (som i fly)

1. Arbeidsprojeksjon er EUREF89 UTM 33, EPSG:25833. Alt internt er (øst, nord) i meter.
   Bane NOR leverer Banenettverk i UTM 32; det transformeres i `crs.py` og bare der.
2. WGS84-kilder transformeres KUN i `crs.py`, med pyproj og `always_xy=True`. Alltid (lon, lat).
3. Rutenett: `x = (øst - west) / celle`, `y = (north - nord) / celle`. **y øker mot sør**.
4. Rutenett-nord er ikke sann nord. Konvergensen varierer langs en lang strekning og må regnes
   per korridorbit, ikke én gang per strekning.
5. Målestokkfaktoren er 1,0016-1,0032 i Sør-Norge. s er målt i UTM-planet og er derfor litt lengre
   enn sporlengden i terrenget. Sammenlign aldri s direkte med Bane NORs km uten å ta hensyn til det.
6. Høyder er NN2000. Øst-koordinater er NEGATIVE på Vestlandet; koden må tåle det.

## Konvensjoner

- Kode og identifikatorer på engelsk, kommentarer og dokumentasjon på norsk.
- ALL tekst spilleren ser er på engelsk.
- Ikke finn på API-endepunkter. Alle står i `sources.py` med status; et endepunkt blir «verifisert»
  først når det er kalt og svaret kontrollert. Oppdater docs/datakilder.md samtidig.
- Pipeline skal være reproduserbar: ingen manuelle steg, deterministisk utdata, rådata caches i data/raw/.
- Stol ikke på at en tjeneste leverte det du ba om: sjekk CRS, størrelse og georeferering.
- Nye datakilder: lisens og kreditering inn i docs/datakilder.md og i `attribution` i metadata.
- Hver gang noe viser seg å være feil og må rettes (særlig akseretning, fortegn, CRS, s mot km):
  før det i docs/ai-logg.md.
- Høydekartet er rent terreng. Sporets høyde er en egen profil (profile.py), ikke lest av kartet i spillet.
  Skjæringer og fyllinger lages ved å forme terrenget etter profilen, aldri omvendt.
- Sporets høyde i tunneler og på bruer kan ikke leses av DTM. Den interpoleres og kontrolleres mot
  stigningsprofilen fra Bane NOR/RINF. Avvik rapporteres, de skjules ikke.
- Skill mellom ekte og syntetisk, i koden og i docs/datakilder.md.
- Sann målestokk, ingen vertikal overdrivelse. three.js brukes bare til tegning; fysikk og
  sporoppslag er ren TypeScript og testes uten nettleser.
- API-nøkler leses fra miljøet og skrives aldri til fil, logg eller nettleser.
- Commit per logisk steg, uten Co-Authored-By.
- Arbeidet går i faser (se README.md). Gjør én fase, stopp for gjennomgang.

## Kommandoer

```bash
cd pipeline && uv run pytest
cd pipeline && uv run togpipe lines          # strekninger som er definert
cd pipeline && uv run togpipe sources        # endepunkter og verifiseringsstatus
cd pipeline && uv run togpipe estimate 4000  # datamengde for N km korridor
```
