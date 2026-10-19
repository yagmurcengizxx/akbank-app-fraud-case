# APP Fraud Case Çalışması: Yol Haritası

Akbank eğitimindeki case çalışması için hazırlanan ekip projesi. Bu dosya hem proje yol haritasıdır hem de Claude Code'un (ve ekip arkadaşlarının) bağlamı hızlıca kavraması için yazıldı.

## Case'in istediği

Eğitimde (SRE / DevOps / Agile-Kanban anlatıldı) şu görev verildi:

1. Bir **Fraud vakası** seç
2. Vakayı **engellemek için çözüm** ne, anlat
3. Vaka **yaşanırsa sonra ne yapılmalı**, anlat

Çerçeve SRE'dir: *tespit, etki analizi, kök neden, tekrar yaşanmaması için önlem.* Slayttaki SRE gereksinimlerine (4a log toplama/parse, 4b metrik belirleme, 4c alarm kriteri, 3a script/otomasyon, 3b CI/CD) bağlı kalıyoruz.

## Seçilen vaka

**Sosyal mühendislikle para gönderme (APP fraud, Authorized Push Payment).** Dolandırıcı kendini banka görevlisi gibi tanıtır, kurbana kendi uygulamasından, kendi OTP'siyle havale yaptırır. Para katır hesaplara dağılır. İşlem sistemde meşru göründüğü için klasik kurallar yakalamaz.

Sözlük: **katır hesap** = paranın izini kaybettirmek için üzerinden geçirildiği ara hesap. **Uzaktan erişim** = saldırganın kurbanın ekranını görmesini/kontrol etmesini sağlayan uygulama (AnyDesk vb.).

## Repo yapısı

| Yol | Ne |
|---|---|
| `APP_Fraud_Case_Sunum.pptx` | 12 slaytlık sunum (konuşmacı notlarıyla) |
| `demo/fraud_detection_demo.py` | Python demosu: log üret, parse et, metrik hesapla, alarm ver, HOLD |
| `demo/ornek_cikti.txt` | Demonun örnek çıktısı |
| `demo/risk_models.py` | Risk skorunun 3 seviyesi (kural, lojistik regresyon, gradient boosting) aynı sentetik veride karşılaştırılır |
| `demo/risk_models_cikti.txt` | Karşılaştırma demosunun örnek çıktısı |
| `demo/requirements.txt` | `risk_models.py` için bağımlılıklar (numpy, scikit-learn) |
| `demo/build_deck.js` | Sunumu üreten pptxgenjs betiği |
| `webapp/index.html` | Görsel deneme için tek dosyalık banka web uygulaması (sunucu gerekmez) |

## Çalıştırma

```bash
# Python demosu (ek paket gerekmez, Python 3.10+)
python demo/fraud_detection_demo.py

# Risk skoru seviyeleri karşılaştırması (önce: pip install -r demo/requirements.txt)
python demo/risk_models.py

# Web uygulaması: dosyayı tarayıcıda aç
webapp/index.html

# Sunumu yeniden üret (Node + pptxgenjs gerekir)
npm install pptxgenjs
node demo/build_deck.js APP_Fraud_Case_Sunum.pptx
```

## Risk kuralları (demo ve web uygulaması aynı mantığı kullanır)

| Sinyal | Puan |
|---|---|
| Yeni alıcı | 30 |
| Yüksek tutar (≥ 20.000 TL) | 25 |
| İşlem sırasında aktif çağrı | 25 |
| Uzaktan erişim uygulaması | 20 |
| Katır hesap sinyali (30 dk içinde ≥ 4 farklı yeni gönderici, tutar ≥ 20.000 TL) | 30 |

Eşik: skor ≥ 70 ise işlem **HOLD**. Riskli işlem oranı %2'yi aşarsa ekibe alarm.

Kural değişirse üç yeri birlikte güncelle: `fraud_detection_demo.py`, `webapp/index.html`, sunumdaki 5. ve 6. slayt (`build_deck.js`).

## Yol haritası

Çalışma Agile/Kanban ile ilerler. Kolonlar: Yapılacak, Devam, Test, Bitti.

### Bitti
- [x] Vaka seçimi ve kurgusu (APP fraud)
- [x] Python tespit demosu (4a, 4b, 4c, 3a)
- [x] Risk skoru 3 seviye: kural tabanlı, lojistik regresyon, gradient boosting karşılaştırması (`demo/risk_models.py`)
- [x] Sunum (12 slayt): vaka, katır hesap, çözüm, risk skoru, skor seviyeleri, demo sonucu, vaka sonrası müdahale, kök neden, önce/sonra
- [x] Görsel web uygulaması (müşteri ekranı + SRE paneli)

### Sıradaki
- [ ] Ekip olarak sunumu gözden geçir, kendi cümlelerinle notları düzenle
- [ ] Sunum provası: süre ölç, rol dağılımı yap (kim hangi slaytı anlatıyor)
- [ ] Canlı demo akışını prova et (web uygulaması senaryosu aşağıda)
- [ ] Olası soruları listele ve cevapları hazırla (aşağıda başlangıç listesi var)

### Geliştirme fikirleri (zamana göre)
- [ ] 3b CI/CD: kuralları YAML/JSON dosyasına taşı, birim testleri yaz, GitHub Actions ile otomatik çalıştır
- [ ] Demoya birim testleri ekle (`pytest`): bilinen fraud yakalanmalı, normal işlem yakalanmamalı
- [ ] Gerçek MTTD/MTTR hesabı: zaman çizelgeli olay simülasyonu ve postmortem şablonu (`docs/postmortem.md`)
- [ ] Web uygulamasında alıcı doğrulama (isim eşleştirme) ve bekleme süresi geri sayımı
- [ ] Runbook dokümanı: alarm geldiğinde nöbetçi ne yapar (adım adım)
- [ ] Grafana benzeri basit dashboard (slaytta geçen araçlara referans)

## Canlı demo senaryosu (web uygulaması)

1. "Normal havale üret": işlemler onaylanır, alarm yok
2. Soldan 2.500 TL'yi Ayşe'ye gönder: normal geçer
3. Alıcıyı `M901` yap, 50.000 TL gir, "telefon görüşmesi" kutusunu işaretle, gönder: uyarı penceresi çıkar
4. "Saldırı simüle et": panelde alarmlar, kırmızıya dönen oran, katır hesap listesi

## Olası jüri soruları

- *Yanlış alarm (false positive) olursa müşteri mağdur olmaz mı?* Skor eşiği ayarlanabilir, HOLD işlemi iptal etmez, ek doğrulama ister. Yanlış alarm oranı ayrı bir metrik olarak izlenir.
- *Kurban işlemi kendisi onayladı, neden banka sorumlu?* Davranışsal sapma (yeni alıcı, yüksek tutar, çağrı) tespit edilebilir, bu da bankanın önleme sorumluluğudur.
- *Bu SRE'nin işi mi?* Evet: tespit süresi, alarm kriteri, otomasyon ve postmortem SRE'nin ana başlıkları.
- *Gerçek sistemde nasıl ölçeklenir?* Loglar akış sistemine (ör. Kafka) gider, kurallar gerçek zamanlı değerlendirilir.

## Kurallar

- Veriler **tamamen kurgusaldır**. Gerçek müşteri, hesap veya IBAN verisi repoya konmaz.
- Demo savunma amaçlıdır; saldırı yöntemi öğretmez, tespit ve önlemi gösterir.
- Sunum Türkçe, kod yorumları ve çıktılar Türkçe (ASCII) yazılır.
- `demo/transfers.log` demo her çalıştığında yeniden üretilir, repoya eklenmez.
