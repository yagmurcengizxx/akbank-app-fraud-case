---
paths:
  - "fraud_engine/**"
---
# AI / fraud rules
- Deterministik baseline skor: 30/25/25/20/30, HOLD >=70.
- AI transcript text -> sınıflandırılmış ipuçları. Model sonucu raw log'a veya skoruna izinsiz eklenmez.
- Gereken testler: normal allow, yeni alıcı+yüksek+arama hold, eşik sınırı, mule fan-in, missing fields, AI service offline.
- Sentetik veri ve açıklanabilir reasonCodes; no LLM required for MVP.

