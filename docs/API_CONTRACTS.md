# V1 Sözleşmesi — Değişiklik Öncesi Onay Zorunlu

Hackathon uyum kaynağı: contracts/risk-evaluation.v1.schema.json ve contracts/risk-result.v1.schema.json. Örnek request/response contracts/examples/ altında. Kimlikler sentetiktir; tüm timestamps UTC ISO-8601; para birimi TRY. API yalnızca demo / test ortamıdır; gerçek para hareketi oluşturmaz.

## GET /api/v1/number-reputation?phoneE164=...
Çıktı (demo): {"phoneE164":"+905550001234","reputation":"UNKNOWN","source":"DEMO_LIST","lastUpdated":"2026-10-17T08:00:00Z"}
- reputation: TRUSTED, UNKNOWN, SUSPICIOUS. TRUSTED bankadan doğrulanmış arama garantisi değildir, spoofing riski vardır.
- Gerçek uygulamada numara iletimi rıza, minimizasyon ve rate-limit kapsamında ele alınmalıdır.

## POST /api/v1/risk/evaluate
- Gövde: RiskEvaluationRequest (schema + contracts/examples/risk-request.json).
- Yanıt: RiskEvaluationResult (schema + contracts/examples/risk-result.json).
- eventId idempotency anahtarıdır: aynı eventId aynı sonucu üretmeli, iki kere kaydetmemeli.
- call.isActive çağrı bağlamı; call.source SIMULATED / OS_SCREENING / USER_REPORTED; call.reputation numara itibarı.
- textSignals gelen transcript'in kendisi değil, normalleştirilmiş ipuçlarıdır: SAFE_ACCOUNT, URGENCY, OTP_REQUEST, REMOTE_ACCESS_REQUEST. Kaynak "SIMULATED" ise gerçek zamanlı konuşma dinleme iddia edilmez.
- Yeni alıcı +30, >=20.000 TRY +25, aktif arama +25, remote access +20, mule fan-in >=4 ve işlem yeni alıcı/yüksek tutarsa +30; >=70 HOLD, altı ALLOW.
- Number reputation ve textSignals v1'de açıklayıcıdır; sessizce ek puan verilmez. AI modülü yeni ağırlık önerirse ayrı v2 kararı gerekir.
- reasonCodes: NEW_BENEFICIARY, HIGH_AMOUNT, ACTIVE_CALL, REMOTE_ACCESS, MULE_FAN_IN; aynı event için deterministik sıra.

## GET /api/v1/alerts
MVP için [] veya aşağıdaki dizi: [{"eventId":"evt-0001","decision":"HOLD","score":80,"createdAt":"2026-10-17T08:05:00Z"}]. Erişim demo ortamıyla sınırlıdır.

## POST /api/v1/incidents/{eventId}/action
Body: {"action":"ESCALATE","actor":"demo-analyst","note":"Sentetik vaka, incelemeye alındı"}. action: ESCALATE, RELEASE_AFTER_REVIEW, KEEP_HOLD. RELEASE_AFTER_REVIEW gerçek bankada otomatik işlemi göndermek anlamına **gelmez**.

## Hatalar / genel kurallar
HTTP 400 validation error, 404 unknown event, 409 duplicate/conflicting payload, 429 rate limit (ileride). JSON: {"error":{"code":"VALIDATION_ERROR","message":"..."},"eventId":"evt-0001"}.
Geçersiz/eksik alanlarda uydurma güvenlik kararı üretme. İstemci ağ kesilirse "Risk doğrulanamadı — güvenli doğrulama" diyerek güvenli demo fallback gösterir. 401/403 production auth için gereklidir; MVP'de hiçbir endpoint internete açık gerçek müşteri bilgisi taşımaz.

## Sözleşme freeze
v1 alan adları, tipleri, skor ve karar semantiği entegrasyon bitene kadar dondurulmuştur. Önerilen değişiklik: önce issue, sonra schema + example + tüketici testleri ile PR. Mevcut Python demo ile statik HTML parity boşluğu docs/ARCHITECTURE.md içinde belirtilmiştir.

