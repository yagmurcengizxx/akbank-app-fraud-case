const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "APP Fraud Case Çalışması";

const RED = "D81E3A", DARK = "2B0A10", INK = "2E2E2E", MUTED = "6B6B6B", TINT = "FDECEE", WHITE = "FFFFFF", LINE = "E8C9CE";
const F = "Calibri";
let n = 0;

function base(title, notes) {
  const s = pres.addSlide();
  n++;
  s.background = { color: WHITE };
  s.addText(title, { x: 0.5, y: 0.3, w: 9, h: 0.7, fontFace: F, fontSize: 32, bold: true, color: RED, margin: 0, isTextBox: true, valign: "middle" });
  s.addText("APP Fraud Case · SRE bakışı", { x: 0.5, y: 5.2, w: 5, h: 0.25, fontFace: F, fontSize: 10, color: MUTED, margin: 0, isTextBox: true });
  s.addText(String(n), { x: 9, y: 5.2, w: 0.5, h: 0.25, fontFace: F, fontSize: 10, color: MUTED, align: "right", margin: 0, isTextBox: true });
  if (notes) s.addNotes(notes);
  return s;
}
function circle(s, x, y, d, label, fill = RED, color = WHITE, size = 16) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
  s.addText(label, { x, y, w: d, h: d, align: "center", valign: "middle", fontFace: F, fontSize: size, bold: true, color, margin: 0, isTextBox: true });
}
function card(s, x, y, w, h, fill = TINT) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.12 });
}

// 1 Kapak
{
  const s = pres.addSlide(); n++;
  s.background = { color: DARK };
  s.addText("APP Fraud Case Çalışması", { x: 0.6, y: 1.5, w: 8.8, h: 1.0, fontFace: F, fontSize: 44, bold: true, color: WHITE, margin: 0, isTextBox: true });
  s.addText("Sosyal mühendislikle para gönderme: önleme ve vaka sonrası müdahale", { x: 0.6, y: 2.6, w: 8.8, h: 0.9, fontFace: F, fontSize: 22, color: "F4B6BF", margin: 0, isTextBox: true });
  s.addText("SRE bakışıyla: tespit · müdahale · kök neden · önlem", { x: 0.6, y: 4.4, w: 8.8, h: 0.4, fontFace: F, fontSize: 16, color: "CFA3AA", margin: 0, isTextBox: true });
  s.addNotes("Bir fraud vakası seçtik; nasıl engellenir ve yaşanırsa ne yapılır sorularını SRE perspektifiyle yanıtlıyoruz.");
}

// 2 Vaka secimi
{
  const s = base("Seçilen vaka: APP Fraud", "Fraud tanımı: haksız kazanç için aldatıcı yöntemler. Biz kurbanın parayı kendi eliyle gönderdiği APP vakasını seçtik.");
  card(s, 0.5, 1.2, 4.3, 3.7);
  s.addText("Fraud nedir?", { x: 0.75, y: 1.35, w: 3.8, h: 0.4, fontFace: F, fontSize: 20, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addText("Haksız kazanç için bilerek yapılan aldatıcı veya sahte yöntemler. Çalıntı kart, hesap ele geçirme, sahte kimlik gibi türleri var.", { x: 0.75, y: 1.85, w: 3.8, h: 1.5, fontFace: F, fontSize: 16, color: INK, margin: 0, valign: "top", isTextBox: true });
  s.addText("Biz hangisini seçtik?", { x: 0.75, y: 3.4, w: 3.8, h: 0.4, fontFace: F, fontSize: 20, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addText("Sosyal mühendislikle para gönderme (Authorized Push Payment).", { x: 0.75, y: 3.85, w: 3.8, h: 0.9, fontFace: F, fontSize: 16, color: RED, bold: true, margin: 0, valign: "top", isTextBox: true });
  s.addShape(pres.ShapeType.roundRect, { x: 5.1, y: 1.2, w: 4.4, h: 3.7, fill: { color: RED }, line: { color: RED }, rectRadius: 0.12 });
  s.addText("Neden zor?", { x: 5.4, y: 1.35, w: 3.8, h: 0.4, fontFace: F, fontSize: 20, bold: true, color: WHITE, margin: 0, isTextBox: true });
  s.addText([
    { text: "Giriş ve OTP meşru", options: { bullet: true, breakLine: true } },
    { text: "İşlemi müşteri kendisi onaylar", options: { bullet: true, breakLine: true } },
    { text: "Saldırı bankanın dışında (telefon, SMS) başlar", options: { bullet: true, breakLine: true } },
    { text: "Para hızla katır hesaplara dağılır", options: { bullet: true } },
  ], { x: 5.4, y: 1.9, w: 3.9, h: 2.9, fontFace: F, fontSize: 16, color: WHITE, paraSpaceAfter: 10, margin: 0, valign: "top", isTextBox: true });
}

// 3 Vaka akisi
{
  const s = base("Vaka nasıl işliyor?", "Beş adımlık akış. Sistem açısından 3. adım normal bir havaleye benzer.");
  const steps = [
    ["Temas", "Banka güvenlik birimi adıyla aranır, güven kurulur"],
    ["Baskı", "Hesabınız tehlikede, hemen para aktarın aciliyeti"],
    ["Havale", "Kurban kendi uygulamasından, kendi OTP'siyle gönderir"],
    ["Dağıtım", "Para katır hesaplara bölünür, nakde çevrilir"],
    ["Fark etme", "Kurban geç anlar, para geri alınamaz hale gelmiştir"],
  ];
  steps.forEach(([h, d], i) => {
    const y = 1.2 + i * 0.76;
    card(s, 0.5, y, 9, 0.66);
    circle(s, 0.65, y + 0.1, 0.46, String(i + 1));
    s.addText(h, { x: 1.35, y, w: 1.7, h: 0.66, fontFace: F, fontSize: 18, bold: true, color: INK, margin: 0, valign: "middle", isTextBox: true });
    s.addText(d, { x: 3.0, y, w: 6.35, h: 0.66, fontFace: F, fontSize: 15, color: INK, margin: 0, valign: "middle", isTextBox: true });
  });
}

// 3b Katir hesap
{
  const s = base("Katır hesap nedir?", "Katır hesap: dolandırıcılık parasının izini kaybettirmek için üzerinden geçirildiği ara hesap. Para katır hesapta durdurulabilirse kayıp geri alınabilir.");
  card(s, 0.5, 1.2, 4.4, 3.7);
  s.addText("Tanım", { x: 0.75, y: 1.35, w: 3.9, h: 0.4, fontFace: F, fontSize: 19, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addText("Dolandırıcılıkla elde edilen paranın izini kaybettirmek için üzerinden geçirildiği ara hesap. Para hızla başka hesaplara dağıtılır.", { x: 0.75, y: 1.8, w: 3.9, h: 1.4, fontFace: F, fontSize: 15, color: INK, margin: 0, valign: "top", isTextBox: true });
  s.addText("Hesap sahibi kim?", { x: 0.75, y: 3.2, w: 3.9, h: 0.4, fontFace: F, fontSize: 19, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addText([
    { text: "Bilinçli: komisyon karşılığı hesabını kullandırır", options: { bullet: true, breakLine: true } },
    { text: "Bilinçsiz: kolay iş ilanıyla kandırılmış kişi", options: { bullet: true } },
  ], { x: 0.75, y: 3.65, w: 3.9, h: 1.2, fontFace: F, fontSize: 14, color: INK, paraSpaceAfter: 6, margin: 0, valign: "top", isTextBox: true });
  s.addShape(pres.ShapeType.roundRect, { x: 5.1, y: 1.2, w: 4.4, h: 3.7, fill: { color: RED }, line: { color: RED }, rectRadius: 0.12 });
  s.addText("Nasıl tespit edilir?", { x: 5.35, y: 1.35, w: 3.9, h: 0.4, fontFace: F, fontSize: 19, bold: true, color: WHITE, margin: 0, isTextBox: true });
  s.addText([
    { text: "Kısa sürede çok sayıda farklı göndericiden para gelir (fan-in)", options: { bullet: true, breakLine: true } },
    { text: "Gönderenler hesaba ilk kez para yollar", options: { bullet: true, breakLine: true } },
    { text: "Gelen para hemen çıkar, bakiye durmaz", options: { bullet: true, breakLine: true } },
    { text: "Demoda: 30 dakikada 4 gönderici ve 20 bin TL üzeri tutar", options: { bullet: true } },
  ], { x: 5.35, y: 1.85, w: 3.9, h: 2.95, fontFace: F, fontSize: 15, color: WHITE, paraSpaceAfter: 8, margin: 0, valign: "top", isTextBox: true });
}

// 4 Onleme cozumu
{
  const s = base("Engellemek için çözüm", "SRE ana gereksinimleri slaytındaki madde numaralarıyla eşleştirdik.");
  const hdr = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: RED }, fontFace: F, fontSize: 14 } });
  const cell = (t, b = false) => ({ text: t, options: { fontFace: F, fontSize: 14, color: INK, bold: b } });
  const rows = [
    [hdr("SRE maddesi"), hdr("Ne yapıyoruz?"), hdr("Örnek")],
    [cell("4a Log toplama / parse", true), cell("Havale loglarını ayrıştır"), cell("alıcı, tutar, cihaz, aktif çağrı")],
    [cell("4b Metrik belirleme", true), cell("Risk metriklerini üret"), cell("riskli işlem oranı, katır sinyali")],
    [cell("4c Alarm kriterleri", true), cell("Risk skoru ve eşik tanımla"), cell("skor ≥ 70 → alarm")],
    [cell("3a Script / otomasyon", true), cell("Eşik aşılınca otomatik aksiyon"), cell("işlemi bekletme (HOLD)")],
    [cell("3b CI/CD mantığı", true), cell("Kuralları kod olarak yönet"), cell("test et, otomatik yayınla")],
  ];
  s.addTable(rows, { x: 0.5, y: 1.2, w: 9, colW: [2.9, 3.2, 2.9], rowH: 0.58, border: { type: "solid", pt: 0.75, color: LINE }, valign: "middle" });
  s.addText("Kullanıcı tarafı: uygulamada uyarı ekranı ve farkındalık kampanyası", { x: 0.5, y: 4.75, w: 9, h: 0.35, fontFace: F, fontSize: 14, italic: true, color: MUTED, margin: 0, isTextBox: true });
}

// 5 Risk skoru
{
  const s = base("Alarm kriteri: risk skoru", "Her sinyale puan veriyoruz. Toplam 70 ve üzeri ise işlem otomatik bekletilir.");
  s.addChart(pres.charts.BAR, [{ name: "Puan", labels: ["Yeni alıcı", "Yüksek tutar (≥20 bin TL)", "İşlem sırasında aktif çağrı", "Uzaktan erişim uygulaması", "Katır hesap sinyali"], values: [30, 25, 25, 20, 30] }], {
    x: 0.5, y: 1.2, w: 5.6, h: 3.8, barDir: "bar", chartColors: [RED],
    showTitle: true, title: "Sinyal puanları", titleFontFace: F, titleFontSize: 14, titleColor: INK,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontFace: F, dataLabelFontSize: 12, dataLabelColor: INK,
    catAxisLabelFontFace: F, catAxisLabelFontSize: 12, catAxisLabelColor: INK, catAxisOrientation: "maxMin",
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 50,
  });
  card(s, 6.4, 1.2, 3.1, 3.7);
  s.addText("Eşik", { x: 6.65, y: 1.35, w: 2.6, h: 0.4, fontFace: F, fontSize: 18, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addText("70", { x: 6.65, y: 1.8, w: 2.6, h: 1.0, fontFace: F, fontSize: 60, bold: true, color: RED, margin: 0, isTextBox: true });
  s.addText("ve üzeri skor: işlem bekletilir, ek doğrulama istenir.", { x: 6.65, y: 2.85, w: 2.6, h: 0.9, fontFace: F, fontSize: 14, color: INK, margin: 0, valign: "top", isTextBox: true });
  s.addText("Ayrıca riskli işlem oranı %2'yi aşarsa ekibe alarm gider.", { x: 6.65, y: 3.8, w: 2.6, h: 0.9, fontFace: F, fontSize: 14, color: INK, margin: 0, valign: "top", isTextBox: true });
}

// 5b Skor seviyeleri
{
  const s = base("Skor nasıl gelişir? Üç seviye", "Aynı sentetik veride (30 bin işlem, yüzde 2 fraud) üç yaklaşımı yanlış alarm oranı yüzde 0,5'e sabitleyerek karşılaştırdık. Veri kurgusaldır, gerçek performans değildir. Amaç yaklaşımların farkını göstermek. Kod: demo/risk_models.py");
  const lv = [
    ["1", "Kural tabanlı", "Elle verilmiş puanlar toplanır", "Açıklanabilir, hemen uygulanır", "%67"],
    ["2", "Lojistik regresyon", "Ağırlıklar veriden öğrenilir", "Açıklanabilir, tutar oranı gibi sürekli özellik", "%84"],
    ["3", "Gradient boosting (ML)", "Doğrusal olmayan ilişkileri yakalar", "Açıklaması zor, izleme gerekir", "%83"],
  ];
  lv.forEach(([no, name, how, note, rec], i) => {
    const x = 0.5 + i * 3.05;
    card(s, x, 1.2, 2.9, 3.0);
    circle(s, x + 0.2, 1.35, 0.5, no);
    s.addText(name, { x: x + 0.85, y: 1.35, w: 1.95, h: 0.5, fontFace: F, fontSize: 15, bold: true, color: INK, margin: 0, valign: "middle", isTextBox: true });
    s.addText(how, { x: x + 0.2, y: 2.0, w: 2.5, h: 0.65, fontFace: F, fontSize: 14, color: INK, margin: 0, valign: "top", isTextBox: true });
    s.addText(note, { x: x + 0.2, y: 2.65, w: 2.5, h: 0.65, fontFace: F, fontSize: 14, color: MUTED, margin: 0, valign: "top", isTextBox: true });
    s.addText(rec, { x: x + 0.2, y: 3.3, w: 2.5, h: 0.5, fontFace: F, fontSize: 30, bold: true, color: RED, margin: 0, isTextBox: true });
    s.addText("fraud yakalama", { x: x + 0.2, y: 3.8, w: 2.5, h: 0.3, fontFace: F, fontSize: 12, color: MUTED, margin: 0, isTextBox: true });
  });
  s.addText("Aynı yanlış alarm bütçesinde (normal işlemlerin %0,5'i) · kurgusal veri · hibrit yaklaşım: ML skoru + kritik kural", { x: 0.5, y: 4.45, w: 9, h: 0.5, fontFace: F, fontSize: 14, italic: true, color: MUTED, margin: 0, valign: "top", isTextBox: true });
}

// 5c PaySim
{
  const s = base("Açık veri setinde test: PaySim", "PaySim: Kaggle'daki sentetik mobil para transferi veri seti. Sadece TRANSFER işlemleri, zamana göre bölündü: ilk yüzde 70 eğitim, son yüzde 30 test. Fraud'ların yüzde 96'sı bakiyenin tamamını gönderiyor, normal işlemlerde bu neredeyse hiç yok. Bu yüzden sonuçlar gerçek dünyadan iyimser. Bu sinyal olmadan modeller yüzde 27-28 yakalıyor. Kod: demo/paysim_models.py");
  const st = [["%95", "Kural tabanlı"], ["%100", "Lojistik regresyon"], ["%100", "Gradient boosting"]];
  s.addText("532 bin transfer · %1,4 fraud · zamana göre eğitim/test · yanlış alarm %0,5'te sabit", { x: 0.5, y: 1.1, w: 9, h: 0.35, fontFace: F, fontSize: 14, color: MUTED, margin: 0, isTextBox: true });
  st.forEach(([big, lbl], i) => {
    const x = 0.5 + i * 3.05;
    card(s, x, 1.6, 2.9, 1.45);
    s.addText(big, { x, y: 1.7, w: 2.9, h: 0.75, fontFace: F, fontSize: 36, bold: true, color: RED, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(lbl + " · fraud yakalama", { x, y: 2.45, w: 2.9, h: 0.45, fontFace: F, fontSize: 14, color: INK, align: "center", margin: 0, isTextBox: true });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 3.3, w: 9, h: 1.65, fill: { color: RED }, line: { color: RED }, rectRadius: 0.12 });
  s.addText("Dikkat: sonuç gerçek dünyaya göre iyimser", { x: 0.75, y: 3.4, w: 8.5, h: 0.4, fontFace: F, fontSize: 18, bold: true, color: WHITE, margin: 0, isTextBox: true });
  s.addText([
    { text: "Fraud'ların %96'sı bakiyenin tamamını gönderiyor, normallerde neredeyse hiç yok. APP'ye uygun bir sinyal (“tüm paranızı güvenli hesaba aktarın”).", options: { bullet: true, breakLine: true } },
    { text: "Bu sinyal çıkarılınca modeller %27-28 yakalıyor. Cihaz ve çağrı sinyalleri bu yüzden kritik.", options: { bullet: true } },
  ], { x: 0.75, y: 3.85, w: 8.5, h: 1.05, fontFace: F, fontSize: 14, color: WHITE, paraSpaceAfter: 4, margin: 0, valign: "top", isTextBox: true });
}

// 6 Demo sonucu
{
  const s = base("Demo sonucu", "Demo: demo/fraud_detection_demo.py. Sentetik veri: 310 işlem, 8 kurgusal APP fraud işlemi. Sayılar kurgusal verinin çıktısıdır.");
  const stats = [["8 / 8", "fraud işlemi yakalandı"], ["0", "yanlış alarm"], ["533 bin TL", "korunan tutar"], ["%2,6", "riskli işlem oranı (eşik %2)"]];
  stats.forEach(([big, lbl], i) => {
    const x = 0.5 + i * 2.28;
    card(s, x, 1.2, 2.14, 1.9);
    s.addText(big, { x, y: 1.35, w: 2.14, h: 0.9, fontFace: F, fontSize: big.length > 6 ? 28 : 40, bold: true, color: RED, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(lbl, { x: x + 0.1, y: 2.25, w: 1.94, h: 0.75, fontFace: F, fontSize: 14, color: INK, align: "center", valign: "top", margin: 0, isTextBox: true });
  });
  const flow = ["Log üret", "Parse et", "Metrik hesapla", "Kural ve alarm", "HOLD"];
  flow.forEach((t, i) => {
    const x = 0.5 + i * 1.82;
    s.addShape(pres.ShapeType.roundRect, { x, y: 3.5, w: 1.62, h: 0.8, fill: { color: i === 4 ? RED : WHITE }, line: { color: RED, width: 1.5 }, rectRadius: 0.1 });
    s.addText(t, { x, y: 3.5, w: 1.62, h: 0.8, fontFace: F, fontSize: 14, bold: true, color: i === 4 ? WHITE : RED, align: "center", valign: "middle", margin: 0, isTextBox: true });
    if (i < 4) s.addText("›", { x: x + 1.62, y: 3.5, w: 0.2, h: 0.8, fontFace: F, fontSize: 22, bold: true, color: RED, align: "center", valign: "middle", margin: 0, isTextBox: true });
  });
  s.addText("Kurgusal veriyle çalışan Python demosu · 4a, 4b, 4c ve 3a maddelerini gösterir", { x: 0.5, y: 4.55, w: 9, h: 0.35, fontFace: F, fontSize: 14, italic: true, color: MUTED, margin: 0, isTextBox: true });
}

// 7 Vaka yasanirsa
{
  const s = base("Vaka yaşanırsa ne yapılmalı?", "Olay yönetimi akışı: tespit, etki analizi, acil aksiyon, kök neden, postmortem, iyileştirme.");
  const steps = [
    ["Tespit", "Alarm tetiklenir, nöbetçi ekip bilgilenir"],
    ["Etki analizi", "Kaç müşteri, ne kadar tutar, hangi hesaplar?"],
    ["Acil aksiyon", "İşlemi durdur, katır hesapları dondur, müşteriyi ara"],
    ["Kök neden", "Kural neden yakalamadı? Eşik, veri veya süreç eksiği"],
    ["Postmortem", "Suçlu aramadan zaman çizelgesi, MTTD ve MTTR raporu"],
    ["İyileştirme", "Yeni kural, metrik, runbook ve kampanya"],
  ];
  steps.forEach(([h, d], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.6, y = 1.2 + row * 1.25;
    card(s, x, y, 4.4, 1.1);
    circle(s, x + 0.15, y + 0.3, 0.5, String(i + 1));
    s.addText(h, { x: x + 0.85, y: y + 0.08, w: 3.4, h: 0.38, fontFace: F, fontSize: 17, bold: true, color: INK, margin: 0, isTextBox: true });
    s.addText(d, { x: x + 0.85, y: y + 0.45, w: 3.4, h: 0.6, fontFace: F, fontSize: 14, color: INK, margin: 0, valign: "top", isTextBox: true });
  });
}

// 8 Kok neden ve onlem
{
  const s = base("Kök neden ve tekrar yaşanmaması", "Blameless postmortem örneği: kişiyi değil sistemi ve süreci sorguluyoruz.");
  card(s, 0.5, 1.2, 4.4, 3.7);
  s.addText("Neden yakalanmadı?", { x: 0.75, y: 1.35, w: 3.9, h: 0.4, fontFace: F, fontSize: 19, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addText([
    { text: "Yeni alıcı ve yüksek tutar için kural yoktu", options: { bullet: true, breakLine: true } },
    { text: "Çağrı ve uzaktan erişim sinyali loglanmıyordu", options: { bullet: true, breakLine: true } },
    { text: "Katır hesap girişleri izlenmiyordu", options: { bullet: true, breakLine: true } },
    { text: "Alarm yoktu, müşteri şikayetiyle öğrenildi", options: { bullet: true } },
  ], { x: 0.75, y: 1.85, w: 3.9, h: 2.9, fontFace: F, fontSize: 15, color: INK, paraSpaceAfter: 8, margin: 0, valign: "top", isTextBox: true });
  s.addShape(pres.ShapeType.roundRect, { x: 5.1, y: 1.2, w: 4.4, h: 3.7, fill: { color: RED }, line: { color: RED }, rectRadius: 0.12 });
  s.addText("Önlem aksiyonları", { x: 5.35, y: 1.35, w: 3.9, h: 0.4, fontFace: F, fontSize: 19, bold: true, color: WHITE, margin: 0, isTextBox: true });
  s.addText([
    { text: "Risk skoru ve HOLD kuralı (CI/CD ile yayın)", options: { bullet: true, breakLine: true } },
    { text: "Yeni log alanları ve metrikler", options: { bullet: true, breakLine: true } },
    { text: "Katır hesap alarmı ve hızlı dondurma", options: { bullet: true, breakLine: true } },
    { text: "Runbook, tatbikat, müşteri uyarı ekranı", options: { bullet: true } },
  ], { x: 5.35, y: 1.85, w: 3.9, h: 2.9, fontFace: F, fontSize: 15, color: WHITE, paraSpaceAfter: 8, margin: 0, valign: "top", isTextBox: true });
}

// 9 Once / sonra
{
  const s = base("Kazanım: önce ve sonra", "Önce sütunu kurgusal bir başlangıç durumudur, sonra sütunu demodaki davranıştır.");
  const rows = [
    ["Tespit", "Müşteri şikayetiyle, saatler sonra", "İşlem anında, otomatik alarm"],
    ["Müdahale", "Manuel ve geç", "Otomatik HOLD, katır hesap dondurma"],
    ["Korunan tutar", "Çoğunlukla geri alınamaz", "Demoda 8/8 işlem durduruldu"],
    ["Öğrenme", "Kayıt yok", "Postmortem ve yeni kural"],
  ];
  s.addText("Önce", { x: 2.6, y: 1.15, w: 3.2, h: 0.4, fontFace: F, fontSize: 18, bold: true, color: MUTED, margin: 0, align: "center", isTextBox: true });
  s.addText("Sonra", { x: 6.1, y: 1.15, w: 3.4, h: 0.4, fontFace: F, fontSize: 18, bold: true, color: RED, margin: 0, align: "center", isTextBox: true });
  rows.forEach(([h, a, b], i) => {
    const y = 1.65 + i * 0.8;
    s.addText(h, { x: 0.5, y, w: 2.0, h: 0.7, fontFace: F, fontSize: 16, bold: true, color: INK, margin: 0, valign: "middle", isTextBox: true });
    card(s, 2.6, y, 3.2, 0.7, "F1F1F1");
    s.addText(a, { x: 2.7, y, w: 3.0, h: 0.7, fontFace: F, fontSize: 14, color: INK, margin: 0, align: "center", valign: "middle", isTextBox: true });
    card(s, 6.1, y, 3.4, 0.7, TINT);
    s.addText(b, { x: 6.2, y, w: 3.2, h: 0.7, fontFace: F, fontSize: 14, color: INK, bold: true, margin: 0, align: "center", valign: "middle", isTextBox: true });
  });
}

// 10 Kapanis
{
  const s = pres.addSlide(); n++;
  s.background = { color: DARK };
  s.addText("Özet", { x: 0.6, y: 0.7, w: 8.8, h: 0.8, fontFace: F, fontSize: 40, bold: true, color: WHITE, margin: 0, isTextBox: true });
  const items = [["Vaka", "Sosyal mühendislikle para gönderme (APP fraud)"], ["Engelleme", "Log, metrik, alarm, otomatik HOLD ve CI/CD ile kural yönetimi"], ["Vaka sonrası", "Etki analizi, kök neden, blameless postmortem, iyileştirme"]];
  items.forEach(([h, d], i) => {
    const y = 1.8 + i * 0.95;
    circle(s, 0.6, y + 0.1, 0.55, String(i + 1), RED, WHITE, 18);
    s.addText(h, { x: 1.4, y, w: 2.2, h: 0.75, fontFace: F, fontSize: 20, bold: true, color: "F4B6BF", margin: 0, valign: "middle", isTextBox: true });
    s.addText(d, { x: 3.6, y, w: 5.9, h: 0.75, fontFace: F, fontSize: 16, color: WHITE, margin: 0, valign: "middle", isTextBox: true });
  });
  s.addText("Sorular?", { x: 0.6, y: 4.7, w: 8.8, h: 0.5, fontFace: F, fontSize: 20, color: "CFA3AA", margin: 0, isTextBox: true });
}

pres.writeFile({ fileName: process.argv[2] }).then(() => console.log("ok"));
