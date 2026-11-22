# KI-logg

Feil som er funnet og rettet underveis, særlig akseretning, fortegn, CRS og s mot kilometrering.
Nyeste øverst.

## 2026-11-22: Flåm har positiv østverdi i UTM 33

Første CRS-test antok at Flåm (7,11° Ø) har negativ østverdi i UTM 33, slik Sola og Flesland har i fly.
Den er ca. +72 000 m: på 60,9° N er 7,9 lengdegrader vest for sentralmeridianen bare ca. 430 km. Testen
sjekker nå et intervall i stedet for fortegn. Regelen i CLAUDE.md (koden må tåle negative østverdier) står.
