# Platform Gerçekliği — Call Screening / Transcript

## Android
Resmî Android CallScreeningService, kullanıcı tarafından call-screening rolü verildiğinde çağrı bilgisi için kullanılabilir; onScreenCall çağrısına **5 saniye içinde** cevap verilmelidir. Uygulama izinleri ve cihaz sürümü önemlidir. Bu arayüz telefonun normal GSM görüşme sesini uygulamaya vermek için tasarlanmamıştır. Telefon uygulamasının yerine geçmek ya da genel telefon sesini gizlice kaydetmek MVP için hedef değildir.
MVP: rol/izin araştırması, numara itibarı, risk etiketi, demo incoming-call ekranı, bankacılık ekranında "aktif arama" simülasyonu. Gerçek OS screening bir P2 spike'tır.

## iOS
CallKit / Call Directory extension, numara tanımlama ve blok listesi sağlar. Standart hücresel aramanın sesini üçüncü taraf banka uygulamasının gizlice dinleyip gerçek zamanlı metne dökeceği varsayımıyla ürün tasarlamayın. iOS için gösterilebilir MVP: rehber dışı numara etiketi / eğitim ekranı, senaryo simülasyonu ve güvenli banka içi onay akışı.

## Transcript yolu
Yarışma demonuzda *sentetik veya kullanıcıca bilerek sağlanan konuşma metni* üzerinde STT sonrası risk analizi canlandırın. Gerçek ürün araştırmasında kullanıcı izni, diğer tarafın hakları, KVKK, cihaz/ülke/OS dağılımı ve bankanın resmi erişim yetkileri ayrı değerlendirilmelidir.

## Güvenlik tasarım notu
Allowlist kesin güven demek değildir: telefon numarası spoofing olabilir. Banka görevlisi olduğunu iddia eden arayana para transferi yerine uygulamanın içinde başlatılan, bağımsız doğrulama adımı sunulmalıdır.

## Resmî kaynaklar
- Android CallScreeningService: https://developer.android.com/reference/android/telecom/CallScreeningService
- Apple CallKit: https://developer.apple.com/documentation/callkit
- Apple Call Directory: https://developer.apple.com/documentation/CallKit/identifying-and-blocking-calls

Kaynaklar uygulama API kapsamı içindir; hackathon demosundaki sinyallerin hepsi gerçek telefon API'sinden geliyormuş gibi anlatılamaz.

