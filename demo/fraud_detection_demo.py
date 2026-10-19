"""APP Fraud (sosyal muhendislikle para gonderme) - savunma amacli tespit demosu.

Akis (SRE gereksinimleri 4a/4b/4c + 3a):
  1. Sentetik havale loglari uretilir (JSON satirlari)     -> log toplama
  2. Loglar parse edilir                                   -> 4a
  3. Metrikler hesaplanir                                  -> 4b
  4. Risk kurallari ve alarm esikleri uygulanir            -> 4c
  5. Esik asilirsa islem otomatik bekletilir (HOLD)        -> 3a otomasyon
"""
import json
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

LOG_FILE = Path(__file__).with_name("transfers.log")

# --- Alarm esikleri (kod olarak tutulur; CI/CD ile test edilip yayinlanabilir) ---
HIGH_AMOUNT = 20_000          # TL
RISK_HOLD_SCORE = 70          # bu skor ve ustu islem bekletilir
MULE_FAN_IN_SENDERS = 4       # pencere icinde bu kadar farkli gonderici -> katir hesap
MULE_WINDOW = timedelta(minutes=30)
RISK_RATIO_ALERT = 0.02       # riskli islem / toplam islem orani alarmi (normal gunde ~%0)


def generate_logs(path: Path, seed: int = 42) -> None:
    rnd = random.Random(seed)
    start = datetime(2026, 10, 17, 9, 0, 0)
    customers = [f"C{i:03d}" for i in range(1, 101)]
    known = {c: {f"B{rnd.randint(1, 60):03d}" for _ in range(3)} for c in customers}
    devices = {c: f"D-{c}" for c in customers}
    events = []

    # Normal trafik: bilinen alicilar, bilinen cihaz, dusuk/orta tutar
    for _ in range(400):
        c = rnd.choice(customers)
        events.append({
            "ts": start + timedelta(seconds=rnd.randint(0, 4 * 3600)),
            "customer": c, "to": rnd.choice(sorted(known[c])),
            "amount": round(rnd.uniform(100, 6000), 2),
            "device": devices[c], "remote_access": False, "active_call": False,
            "label": "normal",
        })

    # Saldiri: kurbanlar "banka guvenlik" aramasi sirasinda yeni alicilara yuksek tutar yollar
    mules = ["M901", "M902"]
    attack_start = start + timedelta(hours=2)
    victims = rnd.sample(customers, 8)
    for i, v in enumerate(victims):
        events.append({
            "ts": attack_start + timedelta(minutes=4 * i + rnd.randint(0, 2)),
            "customer": v, "to": mules[i % 2],
            "amount": round(rnd.uniform(35_000, 90_000), 2),
            "device": devices[v], "remote_access": i % 2 == 0, "active_call": True,
            "label": "fraud",
        })

    events.sort(key=lambda e: e["ts"])
    with path.open("w", encoding="utf-8") as f:
        for e in events:
            e = dict(e, ts=e["ts"].isoformat())
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def parse_logs(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            r["ts"] = datetime.fromisoformat(r["ts"])
            rows.append(r)
    return rows


def risk_score(tx: dict, seen_beneficiaries: dict) -> tuple[int, list[str]]:
    score, reasons = 0, []
    if tx["to"] not in seen_beneficiaries[tx["customer"]]:
        score += 30; reasons.append("yeni alici")
    if tx["amount"] >= HIGH_AMOUNT:
        score += 25; reasons.append("yuksek tutar")
    if tx["active_call"]:
        score += 25; reasons.append("islem sirasinda aktif cagri")
    if tx["remote_access"]:
        score += 20; reasons.append("uzaktan erisim uygulamasi")
    return score, reasons


def run() -> None:
    generate_logs(LOG_FILE)
    rows = parse_logs(LOG_FILE)

    # Gecmis (ilk 60 dk) alici bilgisini "bilinen alici" kabul et
    seen = defaultdict(set)
    history_end = rows[0]["ts"] + timedelta(minutes=60)
    for r in rows:
        if r["ts"] <= history_end:
            seen[r["customer"]].add(r["to"])

    held, fan_in, mule_accounts = [], defaultdict(list), set()
    first_fraud_ts = next(r["ts"] for r in rows if r["label"] == "fraud")
    first_alert_ts = None

    for r in rows:
        if r["ts"] <= history_end:
            continue
        score, reasons = risk_score(r, seen)
        if r["to"] not in seen[r["customer"]] and r["amount"] >= HIGH_AMOUNT:  # yeni alici + yuksek tutar
            fan_in[r["to"]].append((r["ts"], r["customer"]))
        recent = {c for t, c in fan_in[r["to"]] if r["ts"] - t <= MULE_WINDOW}
        mule = len(recent) >= MULE_FAN_IN_SENDERS
        if mule:
            mule_accounts.add(r["to"])
            score += 30; reasons.append(f"katir hesap sinyali ({len(recent)} gonderici)")
        if score >= RISK_HOLD_SCORE:
            held.append((r, score, reasons))
            first_alert_ts = first_alert_ts or r["ts"]
        seen[r["customer"]].add(r["to"])

    post = [r for r in rows if r["ts"] > history_end]
    fraud = [r for r in post if r["label"] == "fraud"]
    held_fraud = [h for h in held if h[0]["label"] == "fraud"]
    false_pos = [h for h in held if h[0]["label"] == "normal"]
    saved = sum(h[0]["amount"] for h in held_fraud)
    total = sum(r["amount"] for r in fraud)
    ratio = len(held) / len(post)

    print("=== METRIKLER (4b) ===")
    print(f"Toplam islem            : {len(post)}")
    print(f"Riskli (bekletilen)     : {len(held)}  -> oran {ratio:.1%} "
          f"({'ALARM' if ratio >= RISK_RATIO_ALERT else 'normal'}, esik {RISK_RATIO_ALERT:.0%})")
    print(f"Yakalanan fraud         : {len(held_fraud)}/{len(fraud)}")
    print(f"Yanlis alarm            : {len(false_pos)}")
    print(f"Korunan tutar           : {saved:,.0f} TL / {total:,.0f} TL")
    mttd = (first_alert_ts - first_fraud_ts).total_seconds()
    print(f"Ilk fraud -> ilk alarm  : {mttd:.0f} sn (MTTD)")

    print("\n=== ALARMLAR (4c) -> HOLD (3a otomasyon) ===")
    for r, score, reasons in held:
        print(f"{r['ts']:%H:%M} {r['customer']} -> {r['to']} {r['amount']:>9,.0f} TL "
              f"skor={score:3d} [{', '.join(reasons)}]")

    print(f"\nKatir hesap adaylari (dondurulacak): {', '.join(sorted(mule_accounts)) or '-'}")


if __name__ == "__main__":
    run()
