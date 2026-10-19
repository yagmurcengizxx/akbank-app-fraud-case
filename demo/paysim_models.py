"""PaySim (Kaggle) uzerinde risk skorunun 3 seviyesi.

Veri: https://www.kaggle.com/datasets/ealaxi/paysim1  ->  demo/data/ altina koy
      (PS_20174392719_1491204439457_log.csv, ~470 MB)

Sadece TRANSFER islemleri kullanilir (kurbandan baska hesaba para gonderme = APP'ye en yakin akis).
Zaman sirali bolme: ilk %70 egitim, son %30 test (gelecegi gecmisle tahmin etmek, sizinti yok).

Kullanim:
  python demo/paysim_models.py                 # tum veri
  python demo/paysim_models.py --nrows 500000  # ilk 500 bin satir (hizli)
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

DATA = Path(__file__).with_name("data")
FEATURES = ["log_tutar", "tutar_orani", "tum_bakiye", "hesap_bosaldi", "alici_bos_hesap",
            "alici_onceki_islem", "gece", "tutar_ust_kisim"]
# PaySim'de fraud'larin ~%96'si bakiyenin TAMAMINI gonderir, normallerde ~%0. Sinyal APP'ye uygun
# ("paranizi guvenli hesaba aktarin") ama bu kadar keskin ayrim simulatorun ozelligidir.
STRONG = ["tum_bakiye", "tutar_orani", "hesap_bosaldi"]
RULE_THRESHOLD = 70
FPR_TARGET = 0.005


def load(nrows=None):
    files = sorted(DATA.glob("PS_*.csv")) or sorted(DATA.glob("*.csv"))
    if not files:
        raise SystemExit("demo/data/ icinde PaySim CSV dosyasi yok. Kaggle'dan indirip oraya koyun.")
    cols = ["step", "type", "amount", "nameOrig", "oldbalanceOrg", "newbalanceOrig",
            "nameDest", "oldbalanceDest", "isFraud"]
    df = pd.read_csv(files[0], usecols=cols, nrows=nrows)
    df = df[df["type"] == "TRANSFER"].sort_values("step", kind="stable").reset_index(drop=True)
    return df


def build_features(df):
    f = pd.DataFrame(index=df.index)
    f["log_tutar"] = np.log1p(df["amount"])
    f["tutar_orani"] = df["amount"] / (df["oldbalanceOrg"] + 1)             # bakiyenin ne kadari gidiyor
    f["tum_bakiye"] = ((df["amount"] == df["oldbalanceOrg"]) & (df["oldbalanceOrg"] > 0)).astype(int)
    f["hesap_bosaldi"] = ((df["newbalanceOrig"] == 0) & (df["oldbalanceOrg"] > 0)).astype(int)
    f["alici_bos_hesap"] = (df["oldbalanceDest"] == 0).astype(int)           # alici hesap bos/yeni mi
    f["alici_onceki_islem"] = df.groupby("nameDest").cumcount()              # aliciya daha once gelen transfer (fan-in vekili)
    f["gece"] = ((df["step"] % 24) < 6).astype(int)
    f["tutar_ust_kisim"] = (df["amount"] >= 200_000).astype(int)
    return f[FEATURES]


def rule_score(f):
    """Seviye 1: elle verilmis puanlar (APP demosundaki mantigin PaySim karsiligi)."""
    return (30 * (f["alici_onceki_islem"] == 0) + 25 * f["tutar_ust_kisim"] + 30 * f["hesap_bosaldi"]
            + 40 * f["tum_bakiye"]
            + 20 * f["alici_bos_hesap"] + 30 * (f["alici_onceki_islem"] >= 3)).to_numpy()


def row(name, y, alarm, score):
    p = precision_score(y, alarm, zero_division=0)
    r = recall_score(y, alarm)
    fpr = ((alarm == 1) & (y == 0)).sum() / (y == 0).sum()
    print(f"{name:<26} {r:>8.1%} {p:>9.1%} {fpr:>9.2%} {roc_auc_score(y, score):>7.3f}")


def at_fpr(y, score, target):
    thr = np.quantile(score[y == 0], 1 - target)
    return (score > thr).astype(int)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nrows", type=int, default=None)
    args = ap.parse_args()

    df = load(args.nrows)
    X, y = build_features(df), df["isFraud"].to_numpy()
    cut = int(len(df) * 0.7)
    Xtr, Xte, ytr, yte = X.iloc[:cut], X.iloc[cut:], y[:cut], y[cut:]
    print(f"TRANSFER islemi: {len(df):,}  (egitim {len(Xtr):,}, test {len(Xte):,}; test fraud: {yte.sum():,} = {yte.mean():.2%})")
    if ytr.sum() < 10 or yte.sum() < 5:
        raise SystemExit("Egitim/test icinde yeterli fraud yok, --nrows degerini artirin.")

    s1 = rule_score(Xte).astype(float)
    sc = StandardScaler().fit(Xtr)
    lr = LogisticRegression(class_weight="balanced", max_iter=1000).fit(sc.transform(Xtr), ytr)
    s2 = lr.predict_proba(sc.transform(Xte))[:, 1]
    gb = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, random_state=1).fit(Xtr, ytr)
    s3 = gb.predict_proba(Xte)[:, 1]
    critical = ((Xte["tum_bakiye"] == 1) & (Xte["alici_bos_hesap"] == 1)).to_numpy().astype(int)

    print("\nA) Varsayilan esik (kural: skor>=70, modeller: olasilik>=0.5)")
    print(f"{'Model':<26} {'Yakalama':>8} {'Kesinlik':>9} {'Yanlis':>9} {'AUC':>7}")
    row("1. Kural tabanli", yte, (s1 >= RULE_THRESHOLD).astype(int), s1)
    row("2. Lojistik regresyon", yte, (s2 >= 0.5).astype(int), s2)
    row("3. Gradient boosting", yte, (s3 >= 0.5).astype(int), s3)

    print(f"\nB) Esit yanlis alarm butcesi (normal islemlerin en fazla {FPR_TARGET:.1%}'i alarm)")
    print(f"{'Model':<26} {'Yakalama':>8} {'Kesinlik':>9} {'Yanlis':>9} {'AUC':>7}")
    s1_tb = s1 + np.random.default_rng(0).random(len(s1)) * 1e-3   # kural skoru ayrik, esitlikleri boz
    a1, a2, a3 = (at_fpr(yte, s, FPR_TARGET) for s in (s1_tb, s2, s3))
    row("1. Kural tabanli", yte, a1, s1)
    row("2. Lojistik regresyon", yte, a2, s2)
    row("3. Gradient boosting", yte, a3, s3)
    row("Hibrit (ML + kritik kural)", yte, np.maximum(a3, critical), s3)

    print("\nC) Saglamlik kontrolu: 'tum bakiye' ve iliskili sinyaller olmadan")
    print(f"{'Model':<26} {'Yakalama':>8} {'Kesinlik':>9} {'Yanlis':>9} {'AUC':>7}")
    weak = [c for c in FEATURES if c not in STRONG]
    sc_w = StandardScaler().fit(Xtr[weak])
    lr_w = LogisticRegression(class_weight="balanced", max_iter=1000).fit(sc_w.transform(Xtr[weak]), ytr)
    s2w = lr_w.predict_proba(sc_w.transform(Xte[weak]))[:, 1]
    gb_w = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, random_state=1).fit(Xtr[weak], ytr)
    s3w = gb_w.predict_proba(Xte[weak])[:, 1]
    row("2. Lojistik regresyon", yte, at_fpr(yte, s2w, FPR_TARGET), s2w)
    row("3. Gradient boosting", yte, at_fpr(yte, s3w, FPR_TARGET), s3w)

    print("\nSeviye 2 agirliklari (standartlastirilmis; + fraud'a iter):")
    for name, w in sorted(zip(FEATURES, lr.coef_[0]), key=lambda t: -abs(t[1])):
        print(f"  {name:<20} {w:+.2f}")


if __name__ == "__main__":
    main()
