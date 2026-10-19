---
paths:
  - "backend/**"
  - "contracts/**"
---
# Backend and contract rules
- Şema-first ve statik örneklerle uyumlu cevap üret; eventId idempotent olmalı.
- Veriyi normalize/validate et; JSON body size, rate limit, CORS ve timeout risklerini yaz.
- Gerçek kişisel veri depolama; risk algoritmasının ikinci kopyasını yazma.
- Breaking changes için integrasyon review zorunlu.

