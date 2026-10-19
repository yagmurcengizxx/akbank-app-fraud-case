---
name: backend-contract
description: Implement v1 localhost mock API, caller reputation and event persistence without breaking shared risk contracts.
---
# Backend workflow
1. docs/API_CONTRACTS.md ve contracts/*.schema.json oku; sample request/response parse et.
2. Basit localhost API sunucusu seç (tek servis, minimal dependencies), gerçek banka veya prod hesap bağlama.
3. Endpoint'lere validation, eventId idempotency, errors ve local-only CORS ekle.
4. Fraud skorunu fraud_engine/ üzerinden çağır; ayrı kural kopyası üretme. AI yoksa deterministik fallback.
5. GET alerts ve incident action yalnızca sentetik kayıtlara dokunsun; audit log olay ID'leriyle.
6. README çalıştırma komutları + smoke/curl örnekleri + testlerle PR hazırla.
Scope: backend/. Contract edit için ayrı review.

