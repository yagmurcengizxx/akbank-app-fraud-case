# Jury Demo Script — 4 Dakikalık Güvenilir Akış

## Hazırlık
- Önce mevcut statik demo: webapp/index.html'i tarayıcıda aç.
- Python smoke: python demo/fraud_detection_demo.py.
- AI ve mobile henüz bağlı değilse iki ekranı da açıkça "SIMULATED SIGNAL / DEMO MODE" işaretle.
- Herhangi bir internet, mikrofon veya gerçek banka hesabı zorunlu olmamalı.

## Akış (önerilen)
0:00-0:30 — APP fraud: mağdur kendi OTP'si ile havale yaptığından geleneksel kontrol kaçırabilir.
0:30-1:10 — "Bankadan arıyorum" temalı **sentetik** gelen arama. Numara UNKNOWN; kullanıcı gerçek banka içi doğrulamaya yönlendirilir.
1:10-1:50 — Simüle konuşma özellikleri: "güvenli hesaba gönder", "acil", "OTP isteği". AI risk ipuçlarını göster, bunun gerçek GSM dinlemesi olmadığını söyle.
1:50-2:40 — Önce 2.500 TRY kayıtlı alıcıya gönder: ALLOW. Sonra yeni alıcı M901, 50.000 TRY ve aktif arama: 30+25+25=80 -> HOLD.
2:40-3:20 — SRE paneli: JSON log, riskli işlem oranı alarmı (>=%2), sentetik kurtarılan tutar, olay ID'si.
3:20-4:00 — Sonrası: hesap/işlem gözden geçirme, müşteri doğrulaması, postmortem, alarm kuralı iyileştirme.

## Soru-cevap
- "Ses nereden geliyor?" -> MVP'de metin simülasyonu; stock Android/iOS üçüncü parti GSM sesine tam erişim sağlamaz.
- "Arayan numara güvenliyse?" -> Numara spoofing olabilir; tek başına allowlist bypass yok.
- "Yanlış alarm?" -> HOLD + bankanın resmi kanalında step-up verification; false-positive metriği.
- "SRE nerede?" -> log parse / metrik / eşik alarm / otomasyon / CI / postmortem.
- "Gerçek Akbank API'sı mı?" -> Hayır; bağımsız kurgusal prototip, gerçek entegrasyon yok.

