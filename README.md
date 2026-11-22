# tog

Togsimulator langs det norske jernbanenettet, bygget på ekte data: sporgeometri fra Bane NOR og
Kartverket, terreng fra Nasjonal høydemodell, fartsgrenser og stigninger fra infrastrukturregisteret,
avganger og tog i sanntid fra Entur. Ingen mål, ingen poengjag: bare deg, sporet og utsikten.

Søsterprosjekt til [fly.teinum.no](https://fly.teinum.no) ([kode](https://github.com/mteinum/fly)).

## Status

Fase 0. Ingenting å spille ennå.

## Faser

Hver fase avsluttes med gjennomgang før neste starter.

| Fase | Innhold | Ferdig når |
|---|---|---|
| 0 | **Datasjekk for Flåmsbana.** Verifiser endepunktene i `sources.py` (Banenettverk, FKB-Bane, N50 jernbane, RINF, Entur NSR). Skriv docs/datasjekk-flam.md: hva hver kilde har langs Flåmsbana, nøyaktighet, tunneler og bruer, hva RINF har av stigning og fart for Norge. | Hver kilde er verifisert eller forkastet med begrunnelse |
| 1 | **Sporlinje og høydeprofil, Flåmsbana.** Polyline fra beste kilde, tunneler og bruer som s-intervaller, høydeprofil (profile.py), sammenligning mot kjente tall og RINF. Utdata: `line.json` og et profilplott. | Profilen treffer endestasjonenes høyde og største stigning innen avtalt toleranse |
| 2 | **Korridorfliser.** 10 m ±1,5 km og 50 m ±10 km rundt sporet, arealdekke fra N50, skjæringer og fyllinger etter profilen. | Flisene kan åpnes i QGIS og sporet ligger riktig i dem |
| 3 | **Kjør langs sporet.** Web: renderer fra fly, toget som 1D-fysikk langs s, fartsgrenser, kamera i førerhus, utvendig og vindusplass. | Myrdal-Flåm kan kjøres i nettleseren |
| 4 | **Bergensbanen, så hele nettet.** Generaliser pipelinen til alle strekninger i Banenettverk. | Én kommando bygger hele nettet |
| 5 | **Entur.** Ekte avganger (kjør etter ruta) og tog i sanntid (møt det motgående toget på kryssingsstasjonen). | |

## Kjøre

Forutsetninger: [uv](https://docs.astral.sh/uv/).

```bash
cd pipeline
uv run pytest
uv run togpipe lines
uv run togpipe sources
```

## Lisens

Koden er MIT. Data har egne vilkår, se [docs/datakilder.md](docs/datakilder.md).
