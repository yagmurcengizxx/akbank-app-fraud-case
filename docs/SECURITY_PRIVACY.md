# Güvenlik / KVKK / Dürüst Demo Çizgisi

- Repo ve demo yalnızca kurgusal müşteri, kurgusal alıcı, kurgusal telefon numarası kullanır. Gerçek IBAN, TC kimlik, kişisel telefon, OTP, parola, access token ve ses kaydı ekleme.
- Varsayılan olarak arama sesi/transcript kaydedilmez. Sentetik konuşma metninde gerçek kişi tanımlanabilecek bilgi bulunmaz. Prototipte konuşma analizi açıkça simülasyon olarak gösterilir.
- Asgari veri: eventId, sentetik müşteri kimliği, risk features, karar, timestamp. Event loglarında ham telefon saklama; gerektiğinde maskelenmiş veya tek yönlü HMAC etiketi kullan.
- Metriklerde gerçek veriymiş gibi yüzdelik başarı vaadi verme. False positive / false negative ihtimalini anlat, değerlendirme sentetik fixture'lara dayanır.
- HOLD geri döndürülemez para aktarımı değildir; meşru kullanıcı için insan incelemesi / bankanın kendi kanalından doğrulama düşünülür. Gerçek blokaj, katır hesabı dondurma gibi işlemler banka yetkisindedir; demo bu eylemleri **simüle** eder.
- Modelin sahte kesinliğine güvenme: AI skor yerine sınıflandırılmış ipuçları sağlayabilir; prompt injection/sahte görüşme metnine karşı veri ve talimatları ayrı ele al.
- Frontend HTML ve API'ye gelen metinleri encode et / textContent kullan; dinamik innerHTML ile güvensiz içerik basma. Rate limit, validation, body size sınırı ve timeout ekle.
- .env, *.pem, API key ve veritabanı dosyaları commit edilmez. CORS üretimde explicit origin gerektirir. Demo servisi localhost'a bağlanmalı.
- Operasyon: inceleme aksiyonlarını audit et, yanlış alarmları takip et, olay sonrası runbook'ta iletişim ve düzeltici faaliyetleri not et.
- Ürünleştirme aşamasında hukuk/uyum değerlendirmesi, açık rıza/meşru işleme şartı, saklama politikası, üçüncü taraf hakları ve bankanın güvenlik onayı ayrıca gerekir.

