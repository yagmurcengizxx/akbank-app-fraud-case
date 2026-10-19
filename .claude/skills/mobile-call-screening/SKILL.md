---
name: mobile-call-screening
description: Build or review the fraud-case mobile caller reputation prototype within actual Android/iOS platform limits.
---
# Mobile call security workflow
1. docs/PLATFORM_FEASIBILITY.md, docs/API_CONTRACTS.md ve mobile/README.md oku.
2. Önce Android ya da sadece UI simülasyon kapsamını PR'da ilan et. Gerçek GSM sesine erişim vaat etme.
3. Gelen arama için UNKNOWN/SUSPICIOUS/TRUSTED etiketi ve "bankadan geri arama" güvenli UX'i yap. TRUSTED tek başına izinli transfer demek değil.
4. Kullanıcının izin verip vermemesini işleyerek call.source ve isActive sinyallerini üret; 5 saniye sınırına uyan OS screening taslağı ayrı spike olsun.
5. Mock request'i contracts/examples/ ile doğrula. Test ve platform sınırı kanıtını PR'da açıkla.
Scope: mobile/. Other modules only through agreed API changes.

