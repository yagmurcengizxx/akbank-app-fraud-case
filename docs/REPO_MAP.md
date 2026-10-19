# Repository Map

## Main'de mevcut olanlar
- CLAUDE.md: ekip ve AI için başlangıç (bu PR'da kısaltılmıştır; orijinal docs/legacy-case-plan.md).
- webapp/index.html: tek dosyalık müşteri+SRE UI, şimdilik demo kaynağı.
- demo/fraud_detection_demo.py: bağımsız simülatör ve eski risk mantığı.
- demo/build_deck.js, APP_Fraud_Case_Sunum.pptx: sunum kaynak ve çıktı.
- demo/ornek_cikti.txt: sentetik çalışmanın eski örnek çıktısı.

## Bu PR ile kurulan koordinasyon altyapısı
- AGENTS.md: Codex/diğer coding agent giriş dosyası.
- .claude/rules/: yol bazlı çalışma talimatları.
- .claude/skills/: rol özel tekrar kullanılabilir görev akışı.
- contracts/: v1 şema ve örnek fixture'lar.
- mobile/, backend/, fraud_engine/, ops/: ekiplerin açılış sayfaları; **uygulama kodu değil**.
- .github/workflows/ci.yml: mevcut Python test/demo ve JSON format smoke.
- tests/: risk temel davranışı ve örnek contract paritesi.

## Hedef — ilk uygulama PR'larından sonra
- mobile/: Android öncelikli prototype; isteğe bağlı iOS feasibility notları.
- backend/: yerel JSON endpoint server, demo data.
- fraud_engine/: ortak score/rules + opsiyonel AI text features.
- webapp/: API adapter + fallback UI; mevcut vanilla HTML korunabilir.
- ops/: monitoring/runbook/fixtures; demo/ ve sunum ile senkron.

Bu aşamada bir sürü framework veya boş mikroservis üretmeyin. Ekipler contract fixture ile doğrudan kodlamaya başlayabilir.

