---
paths:
  - "webapp/**"
---
# Frontend rules
- Mevcut index.html çalışmayı sürdürür; tasarımı iyileştirirken demo akışını bozma.
- Kullanıcıya ALLOW/HOLD ve gerekçeleri, DEMO MODE, risk doğrulanamadığında fallback göster.
- Kullanıcı kaynaklı metni doğrudan innerHTML'e ekleme; textContent/sanitization kullan.
- API mock ile gerçek local API arasında uyumlu adapter yaz; kopya fraud rule çoğaltma.

