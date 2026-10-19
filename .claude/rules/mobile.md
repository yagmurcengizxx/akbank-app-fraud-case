---
paths:
  - "mobile/**"
---
# Mobile rules
- Mobile yalnızca numara etiketleme, consent/role UX ve güvenli uyarı sağlar; normal GSM ses akışı yakalanıyor varsayma.
- Android CallScreeningService 5 saniyelik callback deadline ve kullanıcı rol gereksinimine uygun ol.
- iOS Call Directory yalnızca caller ID/blocking kapsamında belgelensin.
- API için call.source doğru set edilsin (SIMULATED / OS_SCREENING / USER_REPORTED).
- docs/PLATFORM_FEASIBILITY.md ile çelişme.

