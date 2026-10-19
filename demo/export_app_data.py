"""PaySim'den telefon demosu icin kucuk bir ornek ve egitilmis lojistik regresyon disari aktarir.

Cikti: phone-demo/data.js  (window.APP_DATA = {...}; file:// ile acilabilsin diye JS)
  - model: olcekleyici (ortalama/sapma), agirliklar, sabit, "ek dogrulama" esigi (%0,5 yanlis alarm)
  - sample: test donemindeki TRANSFER islemlerinden normal ve fraud ornekler (ham alanlar + ozellikler)

Kullanim: python demo/export_app_data.py   (CSV demo/data/ altinda olmali)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from paysim_models import load

OUT = Path(__file__).resolve().parents[1] / "phone-demo" / "data.js"
# Telefon demosunda yorumlanabilir olsun diye sade ozellik seti (ic ice gecen ozellikler cikarildi)
FEATURES = ["log_tutar", "log_tutar_orani", "tum_bakiye", "alici_bos_hesap", "log_alici_onceki", "gece"]
FPR_TARGET = 0.005


def features(df):
    f = pd.DataFrame(index=df.index)
    f["log_tutar"] = np.log1p(df["amount"])
    f["log_tutar_orani"] = np.log1p(df["amount"] / (df["oldbalanceOrg"] + 1))
    f["tum_bakiye"] = ((df["amount"] == df["oldbalanceOrg"]) & (df["oldbalanceOrg"] > 0)).astype(int)
    f["alici_bos_hesap"] = (df["oldbalanceDest"] == 0).astype(int)
    f["log_alici_onceki"] = np.log1p(df.groupby("nameDest").cumcount())
    f["gece"] = ((df["step"] % 24) < 6).astype(int)
    return f[FEATURES]


def main():
    df = load()
    X, y = features(df), df["isFraud"].to_numpy()
    # Katir sinyali (v1): ayni saatte (step) ayni aliciya >= 4 farkli gonderici
    senders = df.groupby(["nameDest", "step"])["nameOrig"].transform("nunique")
    cut = int(len(df) * 0.7)

    sc = StandardScaler().fit(X.iloc[:cut])
    lr = LogisticRegression(class_weight="balanced", max_iter=1000).fit(sc.transform(X.iloc[:cut]), y[:cut])
    p = lr.predict_proba(sc.transform(X.iloc[cut:]))[:, 1]
    yte = y[cut:]
    thr = float(np.quantile(p[yte == 0], 1 - FPR_TARGET))
    recall = float((p[yte == 1] > thr).mean())
    auc = float(roc_auc_score(yte, p))

    # Seviye 3: gradient boosting (telefon demosunda golge mod). Kucuk tutuldu ki agaclar JS'e sigsin.
    gb = HistGradientBoostingClassifier(max_iter=60, max_leaf_nodes=15, random_state=1).fit(X.iloc[:cut], y[:cut])
    pg = gb.predict_proba(X.iloc[cut:])[:, 1]
    # Model normallerde asiri emin oldugu icin %0,5 yanlis alarm esigi ~0'a duser; en az %50 isteriz
    thr_g = max(float(np.quantile(pg[yte == 0], 1 - FPR_TARGET)), 0.5)
    recall_g, auc_g = float((pg[yte == 1] > thr_g).mean()), float(roc_auc_score(yte, pg))
    trees = []
    for it in gb._predictors:
        nd = it[0].nodes
        trees.append({"f": nd["feature_idx"].tolist(), "t": nd["num_threshold"].tolist(), "l": nd["left"].tolist(),
                      "r": nd["right"].tolist(), "leaf": nd["is_leaf"].astype(int).tolist(), "v": nd["value"].round(6).tolist()})
    baseline = float(np.ravel(gb._baseline_prediction)[0])

    def gb_manual(x):
        raw = baseline
        for t in trees:
            i = 0
            while not t["leaf"][i]:
                i = t["l"][i] if x[t["f"][i]] <= t["t"][i] else t["r"][i]
            raw += t["v"][i]
        return 1 / (1 + np.exp(-raw))

    rnd = np.random.default_rng(3)
    test = df.iloc[cut:]
    fr = rnd.choice(test.index[test["isFraud"] == 1], 60, replace=False)
    nm = rnd.choice(test.index[test["isFraud"] == 0], 140, replace=False)
    rows = []
    for i in np.concatenate([fr, nm]):
        r = df.loc[i]
        rows.append({
            "step": int(r["step"]), "from": r["nameOrig"], "to": r["nameDest"],
            "amount": round(float(r["amount"]), 2), "balance": round(float(r["oldbalanceOrg"]), 2),
            "destBalance": round(float(r["oldbalanceDest"]), 2),
            "destPrior": int(np.expm1(X.loc[i, "log_alici_onceki"]).round()),
            "destSendersSameHour": int(senders.loc[i]), "isFraud": int(r["isFraud"]),
        })
    rnd.shuffle(rows)

    # JS tarafindaki agac yuruyusu sklearn ile ayni sonucu veriyor mu? (ornek satirlar uzerinde)
    idx = np.concatenate([fr, nm])
    sk = gb.predict_proba(X.loc[idx])[:, 1]
    manual = np.array([gb_manual(X.loc[i].to_numpy()) for i in idx])
    max_diff = float(np.abs(sk - manual).max())
    assert max_diff < 1e-4, f"agac disari aktarimi tutarsiz: {max_diff}"

    data = {
        "source": "PaySim (Lopez-Rojas vd.), Kaggle ealaxi/paysim1 — sentetik veri; TRANSFER islemleri",
        "model": {
            "features": FEATURES, "mean": sc.mean_.round(6).tolist(), "scale": sc.scale_.round(6).tolist(),
            "coef": lr.coef_[0].round(6).tolist(), "intercept": round(float(lr.intercept_[0]), 6),
            "threshold": round(thr, 6), "testRecall": round(recall, 4), "testAuc": round(auc, 4),
            "trainRows": cut, "testRows": len(df) - cut,
        },
        "gb": {
            "features": FEATURES, "baseline": baseline, "trees": trees, "threshold": round(thr_g, 6),
            "testRecall": round(recall_g, 4), "testAuc": round(auc_g, 4),
        },
        "sample": rows,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("// demo/export_app_data.py tarafindan uretildi; elle duzenlemeyin.\nwindow.APP_DATA = "
                   + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"Yazildi: {OUT}  ({OUT.stat().st_size / 1024:.0f} KB)")
    print(f"Model: AUC {auc:.3f}, %{FPR_TARGET * 100:.1f} yanlis alarmda yakalama {recall:.1%}, esik {thr:.4f}")
    for n, w in zip(FEATURES, lr.coef_[0]):
        print(f"  {n:<18} {w:+.2f}")
    print(f"Gradient boosting: {len(trees)} agac, AUC {auc_g:.3f}, yakalama {recall_g:.1%}, esik {thr_g:.4f}, "
          f"JS/sklearn max fark {max_diff:.2e}")


if __name__ == "__main__":
    main()
