# CallGuard — GSM Audio Monitor

Çalışan MVP, Telefon C'nin hoparlöründeki katılımcı-onaylı sesi bilgisayar mikrofonuyla alır ve PCM16 mono/16 kHz frame'lerini WebSocket üzerinden FastAPI servisine iletir. Normal GSM çağrı sesine doğrudan erişmez; konuşma tanıma, kişi ayrımı veya transkript üretmez. Ham ses hiçbir zaman diske yazılmaz.

## Güvenlik ve yasal sınır

Gerçek testten önce **tüm görüşme katılımcıları sesin bilgisayar mikrofonuna aktarılacağı konusunda açıkça bilgilendirilmeli ve gerekli onay alınmalıdır**. Yerel mevzuat/KVKK ve kurum politikaları ayrıca değerlendirilmelidir. Sistem herhangi bir telefon görüşmesini otomatik veya gizli dinlemeye çalışmaz.

- Dashboard işlevleri admin anahtarı ister; her session için ayrı 256-bit token üretilir.
- Token ve maskelenmemiş numara event loguna/JSON raporuna girmez.
- Session varsayılan 15 dakikada sona erer; aynı anda tek aktif test vardır.
- WebSocket Origin allowlist ve 8 KiB frame sınırı uygulanır.
- İnternete açarken Caddy Basic Auth + HTTPS ve güçlü `CALLGUARD_ADMIN_KEY` birlikte kullanılmalıdır.

## Yerel çalıştırma

Python 3.11+ gerekir (önerilen 3.12):

```bash
cd ops/callguard-listener
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
export CALLGUARD_ADMIN_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export CALLGUARD_ALLOWED_ORIGINS=http://127.0.0.1:8091,http://localhost:8091
uvicorn app.main:app --host 127.0.0.1 --port 8091
```

`http://127.0.0.1:8091` açılır. Mikrofon yalnızca localhost veya geçerli HTTPS'te kullanılabilir. Terminalde üretilen admin anahtarını panelde girin; anahtarı chat/log/commit içine koymayın.

## Kullanım

### LIVE MICROPHONE

1. Katılımcı onay kutusunu işaretleyip session başlatın.
2. Mikrofonu seçin ve Connect'e basın; tarayıcı iznini verin.
3. Telefon A, B'yi arar; B, C'yi ekleyip konferansı birleştirir.
4. C mikrofonunu sessize alır, hoparlörü açar ve bilgisayar mikrofonuna yakın tutulur.
5. Panelde packet, byte, RMS, peak ve activity artışını doğrulayın. Bunlar yalnızca ses enerjisi metrikleridir.
6. Disconnect ardından Stop test ile audio track'lerinin ve session'ın kapandığını doğrulayın.

### SYNTHETIC TEST

Modu `SYNTHETIC TEST` seçin, session oluşturup Connect'e basın. Silence, 440 Hz tone ve varying amplitude kontrolleri gerçek PCM frame gönderir. Interrupt akışı keser; Reconnect yeniden bağlar. UI bu modu gerçek konuşma/GSM olarak etiketlemez.

## Test

```bash
cd ops/callguard-listener
. .venv/bin/activate
python -m unittest discover -s tests -v
python -m compileall -q app tests
curl -fsS http://127.0.0.1:8091/health
```

Repo kökünde ayrıca:

```bash
python -m unittest discover -s tests -v
python demo/fraud_detection_demo.py
```

## Docker ve Compose

8091 kullanımını önce kontrol edin: `ss -ltn | grep ':8091 '`. Başka uygulama varsa `.env` içinde yalnızca host portunu değiştirin.

```bash
cp .env.example .env
# güçlü anahtarları ve gerçek HTTPS origin'i düzenle
docker compose config
docker compose build
docker compose up -d
docker compose ps
curl -fsS http://127.0.0.1:8091/health
```

Port sadece loopback'e publish edilir; mevcut container, ağ veya veritabanına bağlanmaz. `docker compose down` sadece bu compose projesini durdurur.

## HTTPS/WSS (Caddy)

`Caddyfile.example` içindeki alan adını değiştirin, `caddy hash-password` çıktısını `CALLGUARD_BASIC_AUTH_HASH` olarak servis ortamına verin. Caddy 443'ü yönetir ve 127.0.0.1:8091'e proxy eder. WebSocket upgrade otomatik desteklenir. `CALLGUARD_ALLOWED_ORIGINS` değeri tam `https://alan-adı` olmalıdır.

## Coolify

1. Repository ve branch olarak `feature/sre-gsm-listener-v1` seçin.
2. Build pack: Docker Compose; base directory `ops/callguard-listener`; compose file `docker-compose.yml`.
3. `CALLGUARD_ADMIN_KEY` secret olarak, `CALLGUARD_ALLOWED_ORIGINS=https://atanan-alan-adı` normal env olarak girin.
4. Coolify proxy'sinde container port 8091'i alan adına bağlayın; host port çakışırsa compose port mapping'ini kaldırıp yalnız Coolify ağı üzerinden yayınlayın.
5. Health path `/health`, expected status 200. HTTPS sertifikası hazır olmadan mikrofon testi yapmayın.
6. Deploy sonrası container health, origin health, dashboard, synthetic tone ve reconnect testini ayrı ayrı doğrulayın.

Servis bellekte çalışır; restart session/metrikleri temizler. Bu tek testlik MVP için kasıtlıdır. Sonraki aşama, açık rıza/saklama politikası tamamlandıktan sonra STT'nin opsiyonel ve ayrı bir işlem hattı olarak eklenmesidir; LLM çıktısı hiçbir zaman tek başına güvenlik kararı vermemelidir.

