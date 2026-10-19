---
name: ai-fraud-engine
description: Implement deterministic APP fraud scoring plus optional simulated-text signals and explainable outputs.
---
# Fraud engine workflow
1. Mevcut demo/fraud_detection_demo.py risk_score ve docs/API_CONTRACTS.md'yi incele.
2. V1: new +30, high >=20000 +25, active call +25, remote +20, qualifying mule fan-in >=4 +30; score >=70 HOLD. Reason code sırası sabit.
3. contracts/examples/risk-request.json için 80/HOLD beklenen fixtures ile test et.
4. Text signals SAFE_ACCOUNT/URGENCY/OTP_REQUEST/REMOTE_ACCESS_REQUEST yalnızca açıklama içindir; izinsiz ek puan verme.
5. LLM/STT modülü eklenirse offline deterministic fallback ve gerçek ses toplama yok; metin kullanıcı tarafından açıkça simüle edilmiş veya izinli.
6. Yanlış olumlu/olumsuz testlerini ve karar izahını PR'a ekle.
Scope: fraud_engine/ and its tests via integration owner.

