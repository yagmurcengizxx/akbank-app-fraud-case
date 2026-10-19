"""Risk skoru: uc olgunluk seviyesinin ayni sentetik veri uzerinde karsilastirilmasi.

  Seviye 1: Kural tabanli toplamsal skor        (elle verilmis puanlar, aciklanabilir)
  Seviye 2: Lojistik regresyon                  (agirliklar veriden ogrenilir, aciklanabilir)
  Seviye 3: Gradient boosting (ML)              (dogrusal olmayan iliskiler, aciklamasi zor)
  Hibrit  : ML skoru + kritik kural gecersiz kilma (bankalarda yaygin yaklasim)

Gereksinim: pip install numpy scikit-learn
Veri tamamen kurgusaldir; fraud ve normal dagilimlari bilerek ortusur (kolay problem degil).
"""
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

FEATURES = ["yeni_alici", "tutar_orani", "tutar_tl", "aktif_cagri", "uzaktan_erisim",
            "yeni_cihaz", "gece", "alici_fan_in", "oturum_sn", "bakiye_orani"]
HIGH_AMOUNT = 20_000
RULE_THRESHOLD = 70
FPR_TARGET = 0.005   # ortak karsilastirma noktasi: normal islemlerin en fazla %0,5'i alarm


def make_data(n=30_000, fraud_rate=0.02, seed=7):
    rnd = np.random.default_rng(seed)
    y = (rnd.random(n) < fraud_rate).astype(int)
    avg = rnd.lognormal(8.0, 0.6, n)                  # musterinin ortalama islem tutari
    balance = avg * rnd.lognormal(3.2, 0.5, n)
    stealth = (y == 1) & (rnd.random(n) < 0.20)       # "sessiz" fraud: dusuk sinyalli, zor vaka
    loud = (y == 1) & ~stealth

    ratio = rnd.lognormal(0.0, 0.7, n)                # normal: ortalama civari, uzun kuyruk
    ratio[loud] = rnd.lognormal(2.1, 0.6, loud.sum())
    ratio[stealth] = rnd.lognormal(0.4, 0.6, stealth.sum())
    amount = avg * ratio

    def flag(p_legit, p_loud, p_stealth):
        p = np.full(n, p_legit)
        p[loud], p[stealth] = p_loud, p_stealth
        return (rnd.random(n) < p).astype(int)

    new_payee = flag(0.12, 0.95, 0.80)
    call = flag(0.03, 0.80, 0.25)
    remote = flag(0.01, 0.35, 0.05)
    new_dev = flag(0.03, 0.10, 0.05)
    night = flag(0.05, 0.15, 0.10)
    fan_in = rnd.poisson(0.15, n)                     # mesru: kira/market gibi yogun alicilar da var
    fan_in[rnd.random(n) < 0.02] += 4
    fan_in[loud] = rnd.poisson(2.5, loud.sum())
    session = rnd.lognormal(3.3, 0.4, n)              # oturum suresi (sn)
    session[loud] = rnd.lognormal(4.0, 0.4, loud.sum())  # yonlendirilen kullanici daha yavas
    X = np.column_stack([new_payee, ratio, amount, call, remote, new_dev, night,
                         fan_in, session, amount / balance])
    return X, y


def rule_score(X):
    f = {name: X[:, i] for i, name in enumerate(FEATURES)}
    return (30 * f["yeni_alici"] + 25 * (f["tutar_tl"] >= HIGH_AMOUNT) + 25 * f["aktif_cagri"]
            + 20 * f["uzaktan_erisim"] + 30 * (f["alici_fan_in"] >= 4))


def report(name, y, alarm, score):
    p = precision_score(y, alarm, zero_division=0)
    r = recall_score(y, alarm)
    fpr = ((alarm == 1) & (y == 0)).sum() / (y == 0).sum()
    auc = roc_auc_score(y, score)
    print(f"{name:<26} {r:>8.1%} {p:>9.1%} {fpr:>9.2%} {auc:>7.3f}")


def at_fpr(y, score, fpr_target):
    """Normallerin en fazla fpr_target kadarini alarma dusuren esigi bul."""
    thr = np.quantile(score[y == 0], 1 - fpr_target)
    return (score > thr).astype(int)


def main():
    X, y = make_data()
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.4, stratify=y, random_state=1)
    print(f"Veri: {len(y)} islem, fraud orani {y.mean():.1%} (test: {len(yte)} islem, {yte.sum()} fraud)\n")

    s1 = rule_score(Xte)

    scaler = StandardScaler().fit(Xtr)
    lr = LogisticRegression(class_weight="balanced", max_iter=1000).fit(scaler.transform(Xtr), ytr)
    s2 = lr.predict_proba(scaler.transform(Xte))[:, 1]

    gb = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, random_state=1).fit(Xtr, ytr)
    s3 = gb.predict_proba(Xte)[:, 1]

    # Hibrit: ML esigi VEYA kritik kural (yeni alici + aktif cagri + tutar ortalamanin 5 kati)
    critical = ((Xte[:, 0] == 1) & (Xte[:, 3] == 1) & (Xte[:, 1] >= 5)).astype(int)

    print("A) Varsayilan karar esigiyle (kural: skor>=70, modeller: olasilik>=0.5)")
    print(f"{'Model':<26} {'Yakalama':>8} {'Kesinlik':>9} {'Yanlis':>9} {'AUC':>7}")
    report("1. Kural tabanli", yte, (s1 >= RULE_THRESHOLD).astype(int), s1)
    report("2. Lojistik regresyon", yte, (s2 >= 0.5).astype(int), s2)
    report("3. Gradient boosting", yte, (s3 >= 0.5).astype(int), s3)

    print(f"\nB) Esit yanlis alarm butcesiyle (normal islemlerin en fazla {FPR_TARGET:.1%}'i alarm)")
    print(f"{'Model':<26} {'Yakalama':>8} {'Kesinlik':>9} {'Yanlis':>9} {'AUC':>7}")
    # kural skoru ayrik oldugu icin esitlikleri bozmak adina cok kucuk gurultu eklenir
    s1_tb = s1 + np.random.default_rng(0).random(len(s1)) * 1e-3
    a1, a2, a3 = (at_fpr(yte, s, FPR_TARGET) for s in (s1_tb, s2, s3))
    report("1. Kural tabanli", yte, a1, s1)
    report("2. Lojistik regresyon", yte, a2, s2)
    report("3. Gradient boosting", yte, a3, s3)
    report("Hibrit (ML + kritik kural)", yte, np.maximum(a3, critical), s3)

    print("\nSeviye 2 agirliklari (standartlastirilmis; + fraud'a iter):")
    for name, w in sorted(zip(FEATURES, lr.coef_[0]), key=lambda t: -abs(t[1])):
        print(f"  {name:<16} {w:+.2f}")

    imp = permutation_importance(gb, Xte, yte, scoring="roc_auc", n_repeats=5, random_state=1)
    print("\nSeviye 3 ozellik onemi (permutation, AUC kaybi):")
    for name, v in sorted(zip(FEATURES, imp.importances_mean), key=lambda t: -t[1])[:6]:
        print(f"  {name:<16} {v:.3f}")


if __name__ == "__main__":
    main()
