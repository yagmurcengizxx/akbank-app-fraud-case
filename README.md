# APP Fraud Case — Telefonla Başlayan Dolandırıcılığa Karşı Risk Motoru

Telefonla başlayan sosyal mühendislik (APP fraud, "authorized push payment") ile para transferi risk sinyallerini birleştiren **savunma odaklı bir MVP**. 17 Ekim 2026 Akbank hackathon case'i için **ekip çalışması** olarak geliştirildi.

> Bu bir demo/prototiptir. Tüm veriler sentetiktir veya açık veri setidir (PaySim). Gerçek banka entegrasyonu, telefon konuşması kaydı ya da gerçek müşteri verisi içermez.

## Neler var

| Klasör / dosya | Açıklama |
|---|---|
| `presentation/index.html` | Asıl sunum: kaydırarak ilerleyen, animasyonlu web sunumu. `j/k` bölüm, `←/→` saldırı zinciri adımı. Etkileşimli risk skoru hesaplayıcısı içerir. |
| `phone-demo/index.html` | Canlı demo: iPhone çerçeveli bankacılık uygulaması + canlı risk motoru paneli + SRE paneli. "Korumasız · Sahne 1" / "Korumalı · Sahne 2" modları (`?mod=korumasiz`). |
| `demo/fraud_detection_demo.py` | Sadece Python standart kütüphanesiyle sentetik işlem, risk puanı, HOLD ve metrik. |
| `demo/risk_models.py`, `demo/paysim_models.py` | Kural tabanlı, lojistik regresyon ve gradient boosting karşılaştırması (sentetik veri ve PaySim). |
| `ops/callguard-listener/` | FastAPI tabanlı dinleyici servis prototipi (Docker). |
| `contracts/`, `docs/` | v1 API sözleşmesi, mimari, platform kısıtları, güvenlik/gizlilik, demo planı. |
| `webapp/`, `APP_Fraud_Case_Sunum.pptx` | Eski demo ve PowerPoint sunum (yedek). |

## Risk modeli (v1)

| Sinyal | Puan |
|---|---|
| Yeni alıcı | +30 |
| Tutar ≥ 20.000 TRY | +25 |
| İşlem sırasında aktif görüşme | +25 |
| Uzaktan erişim uygulaması | +20 |
| Katır hesap sinyali (30 dk'da aynı alıcıya ≥4 yeni gönderici) | +30 |

Skor **≥ 70 → HOLD**. Karar sırası: kural skoru → lojistik regresyon eşiği (ek doğrulama) → müşteri yanıtı / aktif çağrı → onay. Gradient boosting gölge modda puanlar, karara etki etmez. Ağırlıklar demo referansıdır, gerçek bankacılık doğruluğu iddiası değildir.

## Çalıştırma

Sunum ve demo için kurulum gerekmez; `presentation/index.html` ve `phone-demo/index.html` dosyalarını tarayıcıda açın.

```bash
python demo/fraud_detection_demo.py
python -m unittest discover -s tests -v
```

Model karşılaştırması için:

```bash
pip install -r demo/requirements.txt
python demo/risk_models.py
```

PaySim deneyi için CSV'yi `demo/data/` altına koyun (repoya dahil değildir).

## Not

Bu proje bir ekip çalışmasıdır; bu repo projenin son halinin kişisel kopyasıdır.
