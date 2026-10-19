# Beş Kişilik Paralel Geliştirme Rehberi

## Kod sahipliği / ilk sprint
| Rol | Birincil yol | PR branch | Tamamlama kriteri |
| --- | --- | --- | --- |
| 1 Telefon & Mobile | mobile/ | feature/mobile-screening | Numara güven etiketi, izin ekranı, simüle arama, güvenli çıkış |
| 2 Backend & Data | backend/ | feature/backend-api | Contract v1 endpoint'leri, sahte data, doğrulama ve idempotency |
| 3 AI & Risk | fraud_engine/ | feature/ai-risk | Explainable puan, text signals, fallback, 3 pozitif + 3 negatif test |
| 4 Frontend | webapp/ | feature/frontend-demo | Transfer, HOLD, çağrı banner, açıklama, API/mock adapter |
| 5 SRE & Integrasyon | ops/, demo/, sunum | feature/sre-observability | Log, alarm, metrik, test, olay sonrası runbook, sunum uyumu |

Çapraz / ortak alanlar: contracts/, docs/API_CONTRACTS.md, CLAUDE.md, AGENTS.md, .claude/, .github/, root config -> birleştirme sorumlusunun (entegrasyon kaptanı) onayı gerekir. Her rol kendi skills dosyasını okumalı: .claude/skills/mobile-call-screening, backend-contract, ai-fraud-engine, frontend-fraud-demo, sre-incident.

## Takım protokolü
1. main en güncel ve gösterilebilir stabil sürümdür; herkes kendi feature branch'inde çalışır.
2. Çalışmaya başlarken görevini ve değiştireceğin dosyaları ekibe yaz. Başka modülün dosyası gerekiyorsa önce issue/PR'da anlaş.
3. Contract-first: Backend endpoint taslağını ve contracts/examples/ örneklerini ilk checkpoint'te sabitle; mobil/frontend/AI buna göre mock ile ilerlesin.
4. PR = küçük, tek modül, açık demo adımları, test çıktısı ve ekran görüntüsü (UI ise). Başka ekipten en az 1 review.
5. Contract change breaking ise aynı PR'da ilgili adapter'ı ve testleri de düzelt; yarışma sırasında belirsiz breaking change yok.
6. Çatışma durumunda başkasının commitini silme / force push yapma. Entegrasyon kaptanına bildirim, rebase veya merge ile izlenebilir çözüm.
7. Her 30-45 dakikada entegrasyon check-in: hangi API hazır, hangi sahte data kullanıldı, hangi demo kırılıyor?

## Öncelik sırası
P0: bir normal işlem + bir dolandırıcılık işlemi + HOLD + SRE alarmı demoda çalışmalı.
P1: caller reputation ve açıklanabilir text-risk ipuçları; mock veriyle uçtan uca bağlanmalı.
P2: gerçek Android call screening feasibility spike, ileri seviye AI/STT, veri tabanı kalıcılığı, güzel animasyonlar.

## PR kabul şartları
- [ ] Sadece sahibi olduğum modülde değişiklik yaptım (istisnalar açıklandı)
- [ ] Contract v1'i bozmadım, örnek fixture ile denedim
- [ ] Normal ve fraud senaryolarını test ettim
- [ ] Yeni bağımlılık, izin, veri toplama ihtiyacını belirttim
- [ ] Demoda **simülasyon** olan özellikleri açıkça işaretledim

## Komutlar
~~~bash
git switch main && git pull
git switch -c feature/mobile-screening
# kendi modülünde çalış
python -m unittest discover -s tests -v
git add mobile && git commit -m "feat(mobile): add caller reputation prototype"
git push -u origin feature/mobile-screening
# GitHub'dan PR -> main; bir review + checks
~~~

## İletişim formatı
Standup: "Bitti / şimdi / blocker / değişen contract / demo etkisi". PR açıklaması aynı şablonla. Her role farklı AI bağlanabilir; önemli olan branch izolasyonudur, ortak çalışma klasörünü eşzamanlı düzenlememektir.

