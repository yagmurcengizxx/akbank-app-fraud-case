# Akbank APP Fraud Case — Project instructions

Bu repository 17 Ekim 2026 Akbank hackathon/case çalışması içindir. Her AI agent ve ekip üyesi bu dosyayı okuyarak başlamalıdır. Hedef: telefonla başlayan sosyal mühendislik (APP fraud) ile para transferi risk sinyallerini birleştiren **savunma odaklı, dürüstçe etiketlenmiş MVP**.

## Önce oku
1. docs/ARCHITECTURE.md — sistem sınırları ve tek yönlü veri akışı
2. docs/API_CONTRACTS.md — modüller arası değişmez v1 sözleşmesi
3. docs/TEAM_WORKFLOW.md — beş kişinin sahip olduğu dosyalar, branch/PR akışı
4. docs/PLATFORM_FEASIBILITY.md — Android/iOS gerçekte neye izin veriyor
5. docs/SECURITY_PRIVACY.md — sentetik veri, izin, log redaksiyonu
6. docs/DEMO_PLAN.md — jüri için çalıştırılabilir hikâye
7. docs/legacy-case-plan.md — ilk CLAUDE.md; orijinal case yol haritası arşivi

## Mevcut çalışan temel
- demo/fraud_detection_demo.py: Python standart kütüphanesiyle sentetik işlem, puan, HOLD, metrik.
- demo/risk_models.py: lojistik regresyon ve gradient boosting dahil üç yaklaşım karşılaştırması; deney kodudur, prod karar motoru değildir. Çalıştırmak için pip install -r demo/requirements.txt.
- demo/paysim_models.py: aynı üç yaklaşım açık veri seti PaySim üzerinde (CSV demo/data/ altına konur, repoya girmez). Fraud'ların ~%96'sı tüm bakiyeyi gönderdiği için sonuç iyimserdir; bu sinyal olmadan yakalama %27-28. Çıktı: demo/paysim_cikti.txt.
- webapp/index.html: eski müşteri + SRE paneli demosu (yedek; SRE paneli artık phone-demo içinde, sunum buna link vermez).
- phone-demo/index.html: docs/sahne-senaryosu.txt akışını oynatır. Üstte operatör anahtarı: "Korumasız · Sahne 1" (risk paneli gizli, 85.000 TL gider) / "Korumalı · Sahne 2" (canlı risk puanı tıklandıkça artar; Gönder → tek soru → "Hayır" dense de "PARA GÖNDERİLMEDİ" → "Bankamı ara" ile doğrulanmış güvenlik hattı ve olay no). `?mod=korumasiz` ile Sahne 1 modunda açılır. Bakiye 100.000 TL, normal transfer 5.000 TL, alıcı "Kalkınma Fonu Tahsilat"; ekranda banka adı "Örnek Banka". Üç sütun: telefon | risk motoru (tek işlem) | SRE paneli (bütün işlemler: log, metrik, %2 alarmı, otomatik HOLD, katır hesap tespiti 30 dk'da ≥4 yeni gönderici, olay zaman çizelgesi, "Saldırı simüle et"; arka plan trafiği PaySim'in 140 normal işlemi). Sahne 1'de iki panel gizli. iPhone çerçeveli bankacılık uygulaması (solda; telefon içi Guvenli-An-Demo.html tasarımını kullanır: ana sayfa, 1 Bilgiler / 2 Güvenlik / 3 Onay transfer akışı, ek doğrulamada iki soru) ve her tıklamada risk motorunun adımlarını gösteren canlı panel (sağda). Gelen arama / uzaktan erişim simülasyonu, PaySim'den etiketli işlem oynatma. Üç seviye paralel puanlar, karar sıralı tabloyla verilir: 1) kural skoru ≥ 70 → HOLD, 2) lojistik regresyon eşiği → ek doğrulama, 3) müşteri yanıtı / aktif çağrı → HOLD, 4) diğer → onay. Gradient boosting (60 ağaç) gölge modda puanlar, karara etki etmez, loglanır. Veri ve modeller phone-demo/data.js içinde, `python demo/export_app_data.py` ile yeniden üretilir (betik JS ağaç yürüyüşünü sklearn ile doğrular).
- presentation/index.html: kaydırarak ilerleyen, animasyonlu web sunumu (asıl sunum). Tarayıcıda aç; j/k bölüm, ←/→ saldırı zinciri adımı. Etkileşimli risk skoru hesaplayıcısı ve "Seviyeler birlikte" karar tablosu içerir. Uygulama gömülü değildir; "Canlı demo" bölümündeki butonlar phone-demo'yu ayrı sekmede açar (sunum ve uygulama iki ayrı dosya/sekme).
- demo/build_deck.js ve APP_Fraud_Case_Sunum.pptx: PowerPoint sunum (yedek).
- Bunları silme veya habersiz yeniden yazma. Yeni sistem eski demonun üzerine **kademeli** inşa edilir.

## V1 risk sözleşmesi
Yeni alıcı +30; tutar >= 20.000 TRY +25; aktif görüşme +25; uzaktan erişim +20; katır hesap sinyali +30. HOLD eşiği >=70. Katır sinyali: 30 dakikada aynı alıcıya >=4 ayrı yeni gönderici, yüksek tutar. Bu ağırlıklar ilk demolarda referanstır, gerçek bankacılık doğruluğu iddiası değildir.
- V1 API sözleşmesi docs/API_CONTRACTS.md ve contracts/*.schema.json içinde.
- Risk skorunun tek kaynağı hedefte fraud_engine/ olacaktır. Mevcut Python ve HTML iki ayrı implementasyondur; bu bir teknik borçtur. Yeni kural eklerken parity testi ve entegrasyon onayı gerekir.
- AI yalnızca yardımcı risk ipucu ve açıklama üretir; tek başına, doğrulanmamış model çıktısı bankacılık HOLD kararı vermemelidir.

## Ortak çalışma sınırları
- Her kişi yalnızca docs/TEAM_WORKFLOW.md içindeki modülünde çalışır. Ortak dosyalar (contracts/, CLAUDE.md, .claude/, root config, sunum) için entegrasyon sahibinden onay al.
- main doğrudan geliştirme alanı değil; feature/<alan>-<is> branch, küçük PR, en az bir başka ekip üyesi incelemesi.
- Bir API alanını değiştirmeden önce v1 sözleşmesini güncellemeyi **öner**, tüketicileri uyumlu hale getirmeden breaking change yapma.
- Bağımlılık ve framework ekleme kararı gerekçelendirilsin. Hackathon MVP için yeni mikroservis, Kafka, Kubernetes zorunlu değildir.
- Gerçek banka entegrasyonu, telefon konuşması yakalama, iOS sistem araması kaydı veya Play Store izni verilmiş gibi iddialarda bulunma.
- Gerçek müşteri bilgisi, IBAN, ses kaydı, OTP, anahtar, .env ve erişim tokenlarını commitleme.

## Hızlı kontrol
- python -m unittest discover -s tests -v
- python demo/fraud_detection_demo.py
- python -m compileall -q demo tests
- webapp/index.html dosyasını tarayıcıda aç; normal + şüpheli senaryoyu doğrula.
- PR'da kanıt, hangi entegrasyon noktası etkilendi, kısa test çıktısı ve eksiklerin yazılması zorunlu.

## AI için görev başlangıcı
Önce mevcut branch ve değişen dosyaları kontrol et. docs/TEAM_WORKFLOW.md dosyasından rolünü bul. Rolüne karşılık gelen .claude/skills/<rol>/SKILL.md dosyasını uygula. Planını 3-5 maddede yaz, yalnızca kendi dosyalarını değiştir, test et, küçük bir PR aç. Kullanıcı özellikle istemedikçe main'e merge etme.

