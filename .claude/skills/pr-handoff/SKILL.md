---
name: pr-handoff
description: Check code ownership, contracts, tests and concise handoff before asking another hackathon teammate to merge a PR.
disable-model-invocation: true
---
# PR handoff checklist
1. git status ve git diff --stat ile yalnızca kendi dosyaların değiştiğini doğrula.
2. API/schema değişmişse backend + frontend + AI etkisini açıkça yaz ve bütün fixture'ları güncelle.
3. python -m unittest discover -s tests -v ; python demo/fraud_detection_demo.py.
4. Demo: normal ALLOW, şüpheli HOLD, SRE alarmı. Çalıştırmadığın testi geçti olarak yazma.
5. PR açıklamasında kapsam, risk, test kanıtı, platform kısıtı, screenshot ve rollback notu.
6. Merge yalnızca ekip review'ından sonra; force push / main'e direkt push yok.

