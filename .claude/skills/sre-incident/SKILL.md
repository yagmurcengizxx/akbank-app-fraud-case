---
name: sre-incident
description: Build the SRE side of the hackathon case: log parsing, observability, incident response, CI and offline demo.
---
# SRE workflow
1. İlk case maddeleri ve docs/legacy-case-plan.md içindeki 4a/4b/4c + 3a/3b haritasını koru.
2. Sentetik transfer event -> parser -> metric -> alert -> HOLD -> postmortem akışını test et.
3. P0 metrics: total, held_count, held_ratio, false_positive_rate, saved_amount_demo, MTTD_demo. MTTD ve gerçek vaka metriklerini karıştırma.
4. Threshold (held_ratio >=2%) ve 70 score HOLD, artı false alarm senaryosu testlerini ekle.
5. CI test/demo smoke ve incident runbook üret, sunumla senkron tut.
6. Offline fallback ve jüri anlatımı yaz; PR'ı integration owner'a gönder.
Scope: ops/, demo/, existing deck and approved CI.

