---
name: frontend-fraud-demo
description: Extend the existing static banking and SRE demo with caller labels, risk reasons, API/mock adapter and safe fallback.
---
# Frontend workflow
1. webapp/index.html'i kaybetmeden önce çalıştır; docs/DEMO_PLAN.md ve API contract oku.
2. Normal transfer + şüpheli yeni alıcı / 50.000 TRY / çağrı = HOLD görsel akışı korunmalı.
3. Fraud engine'e /api/v1/risk/evaluate ile bağlan; backend hazır değilse contracts/examples/ mock moduna dön ve DEMO MODE yaz.
4. Görüşme transcript sinyallerini metin özellikleri olarak göster; gerçek konuşma dinleme iddia etme.
5. XSS erişilebilirlik, mobil responsive, hata/fallback ve dar ekran testi yap.
6. UI ekran görüntüsü, demo adımları, test sonuçlarıyla PR aç.
Scope: webapp/.

