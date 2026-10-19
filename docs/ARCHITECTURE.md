# Mimari — APP Fraud Guard v1 (Hackathon)

## Problem ve değer
Dolandırıcı kişiyi telefonla kandırıp transferi kullanıcının kendisinin onaylamasını sağlar. Çözüm: **numara itibarı + görüşme bağlamı + işlem davranışı + açıklanabilir risk kuralları + kontrollü HOLD**. Normal kullanıcıya gereksiz engel koymamak kadar riskli işlemi geri döndürülemez şekilde yollamamak da önemlidir.

## Önerilen akış
~~~mermaid
flowchart LR
    A["Gelen arama / test simülatörü"] --> B["Mobile: numara itibarı ve izinli sinyaller"]
    B --> C["Backend: normalize et, olay üret"]
    D["Kullanıcı para transferi (demo UI)"] --> C
    C --> E["Fraud Engine: deterministik risk kuralları"]
    F["AI: simüle edilmiş ya da izinli metinden ipuçları"] --> E
    E --> G{"Risk >= 70?"}
    G -->|Evet| H["HOLD + güvenli doğrulama ekranı"]
    G -->|Hayır| I["ALLOW (simülasyon)"]
    E --> J["SRE: redakte event, metrik, alarm"]
    H --> J
~~~

## İş sorumlulukları
- mobile/: Android önce; güvenli/bilinmeyen/şüpheli numara etiketi, izin yönetimi, yerel liste, çağrı var/yok bağlamı; normal GSM görüşmesinden sistem sesi okuma **yok**.
- backend/: sahte müşteri/işlem API'si, numara reputasyonu, event store (MVP'de bellek/JSON/SQLite yeterli), endpoint doğrulama, idempotency.
- fraud_engine/: ortak skor ve açıklama; sentetik konuşma metninden risk ipuçları; deterministik fallback.
- webapp/: mevcut tek HTML'yi koru, risk kararı ve çağrı uyarısını göster, ihtiyaç olursa API adapter ekle.
- ops/: demo akışı, gözlemlenebilirlik, sentetik load, alarm, olay müdahalesi, CI.
- contracts/: yalnızca uyum üzerinde anlaşarak düzenlenen v1 JSON Schema'lar.

## Temel kararlar
1. Bankacılık entegrasyonu ve gerçek para transferi yok: HOLD, ALLOW, vaka kaydı tamamen demo.
2. Mevcut HTML/Python **hemen korunur**. Backend ayrı servis olarak geliştirilebilir; erişilemiyorsa UI local mock'a döner ve ekranda DEMO MODE yazar.
3. Native GSM konuşmasını üçüncü parti uygulamayla otomatik yazıya dökme MVP'nin zorunlu koşulu **değildir**. Ses / transcript için sentetik metin veya kullanıcı onaylı, uygulamanın sahip olduğu VoIP akışı kullanılır.
4. Telefon numarasına TRUSTED etiketi konulsa bile arayan numara spoof edilebilir. Sadece allowlist'e bakarak güvenlik kontrolü bypass edilmez.
5. Güvenlik kararı açıklanabilir: score, reason codes, eventId, model/rule version. Model etkisi belirsizse varsayılan deterministik kural uygulanır.
6. Olay şeması v1, UTC ISO-8601 timestamps, tutarlar TRY, kimlikler sentetik. API endpoint version /api/v1.

## API'den önce birleşme prensibi
Backend, AI ve frontend aynı request/response contract'larını kullanır. Bir ekip diğerini beklemeden contracts/examples/ üzerinden mock geliştirebilir. İki modül birleşmeden önce contract eşleme ve senaryo testleri yapılır.

## SRE yaşam döngüsü
Event alınır -> normalize/parse -> metrikler (held_ratio, false_positive_rate, MTTD, MTTR, risk_latency) -> eşik alarmı -> HOLD/inceleme -> olay sonrası postmortem ve kalıcı önlem. "Korunan tutar" yalnızca sentetik transferlerden hesaplanır; gerçek banka tasarrufu olarak sunulmaz.

