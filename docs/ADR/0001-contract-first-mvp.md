# ADR-0001: Contract-first, modular-monolith-friendly hackathon

Status: Accepted for demo coordination (2026-10-17).

Context: Tek HTML ve Python demosu var; beş geliştirici paralel çalışacak; kısa süre ve mobil işletim sistemi kısıtları söz konusu.

Decision: Tek GitHub repo, path ownership ve PR review. İki JSON schema ile tek v1 contract, küçük in-process/localhost entegrasyonu. Eski demo korunacak. Android gerçek call screening spike olabilir ama GSM ses dökümü blocking dependency değildir. Fraud rules deterministik kalır, AI annotation yardımcıdır.

Alternatives not chosen: bütün sistemi sıfırdan Next.js/NestJS/Kafka ile yazmak; telefon sesi erişimini garanti kabul etmek; her rol için bağımsız DB ya da deployment yapmak.

Consequences: Entegrasyon kolaylaşır, demo deterministik olur. Risk skorunun Python ve HTML'de kopya bulunması teknik borçtur; ilk uygulama sprintinde fraud_engine/ merkezileştirilmeli, parity testi yazılmalıdır.

