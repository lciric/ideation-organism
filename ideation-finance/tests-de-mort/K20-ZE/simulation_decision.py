"""K20-ZE — simulation de la capacité de décision de la règle (préinscription, sections 8.1 à 8.3).

C'est le code exécuté avant le scellement (fichier de travail `sim.py`), réuni en un seul script :
- la grille du panel, qui venait d'un fichier de présences (`grille.csv`) construit sur l'archive de la BCE, est ici écrite
  par sa règle ; la règle reproduit exactement les comptes vérifiés sur l'archive le 2026-11-13 (624 lignes, 618 complètes,
  578 principales, 107 tours) et ces comptes sont contrôlés par des assertions ;
- le corps de la simulation et de l'analyse (fonctions `simulate`, `dk`, `design`, `analyse`) est inchangé ;
- chaque cas repart d'un générateur neuf de graine 20261113, comme chaque exécution séparée de `sim.py`.

Aucune donnée de résultat n'est lue : ni prévision, ni réalisé, ni valeur de référence. Les seuls chiffres de résultat
utilisés pour calibrer sont ceux, scellés, de K20 (enquête américaine) : b = 0,19 ; k = 0,29 ; rapport de variances 3,06.

Note : les surprises simulées sont continues, donc sans égalité ; la règle de coupure de la section 6.2 (stricte ou large,
la plus proche du tiers) choisit alors toujours la coupure stricte, qui est celle codée ici.

Usage : python3 simulation_decision.py
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import norm

SEED = 20261113
N_TIRAGES = 2000

# ---------------------------------------------------------------------------------------------------------------------
# Grille du panel (comptes de présence de l'archive, section 4.3 de la préinscription)
# ---------------------------------------------------------------------------------------------------------------------
V = ["HICP", "RGDP", "UNEM"]
lignes = []
for v in V:
    for y in range(2000, 2026):
        for rank in range(1, 9):
            t = 4 * (y - 1) + (rank - 1)            # rang 1 = tour T1 de y - 1
            h = 0 if rank >= 5 else 1
            # rang 1 de 2000 : tour 1999T1, pas de tour précédent ; rang 1 de 2001 : A_YEAR_2_AHEAD absent en 1999T4
            complete = not (rank == 1 and y in (2000, 2001))
            pand = v in ("RGDP", "UNEM") and (y in (2020, 2021) or 4 * 2020 <= t <= 4 * 2021 + 3)
            lignes.append(dict(v=v, y=y, t=t, rank=rank, h=h, complete=complete, principal=complete and not pand))
G = pd.DataFrame(lignes)
assert len(G) == 624 and G.complete.sum() == 618 and G.principal.sum() == 578
assert G[G.principal].t.nunique() == 107

CRIT = 1.708; LAGS = 8
T0 = 4*1998  # 1998Q1
NT = 4*2026 - T0
EP = {"E1":(4*2008,4*2009+1),"E2":(4*2011+2,4*2013),"E3":(4*2019+3,4*2023+3)}
VOLWIN = [(4*2008+1,4*2009+1,2.0),(4*2011+3,4*2013,1.5),(4*2020,4*2020+1,3.0),(4*2021,4*2023+3,2.0)]
G["vi"] = G.v.map({v:i for i,v in enumerate(V)})
G["g"] = G.vi*2 + G.h
P = G[G.principal].reset_index(drop=True)
tt = P.t.values; yy = P.y.values; rk = P["rank"].values; vi = P.vi.values; gg = P.g.values
rounds = np.arange(tt.min(), tt.max()+1)
epmask = {k: ((tt-1 <= T) & (4*yy+3 >= Pk)) for k,(Pk,T) in EP.items()}
assert [int(m.sum()) for m in epmask.values()] == [54, 72, 98]

DF=4
def tdraw(rng, size, df=None):
    df = df or DF
    return rng.standard_t(df, size)/np.sqrt(df/(df-2))

def simulate(rng, lam0, lam1, rho, kappa, s_om, s_nu, s_eta, voltail=True, vm=1.0):
    sig = np.ones(NT)
    if voltail:
        for a,b,m in VOLWIN: sig[a-T0:b-T0+1] = 1 + vm*(m-1)
    gsh = tdraw(rng, NT);
    w = np.empty((3,NT)); s = np.empty((3,NT))
    for v in range(3):
        w[v] = sig*(np.sqrt(rho)*gsh + np.sqrt(1-rho)*tdraw(rng, NT))
        s[v] = w[v] + s_om*rng.standard_normal(NT)*sig
    # classe L par variable et tour : tiers supérieur de |s| sur les tours principaux de v
    L = np.zeros((3,NT), dtype=int)
    for v in range(3):
        tr = np.unique(tt[vi==v]) - T0
        q = np.quantile(np.abs(s[v, tr]), 2/3)
        L[v] = (np.abs(s[v]) > q).astype(int)
    e_out = np.empty(len(P)); r_out = np.empty(len(P)); L_out = np.empty(len(P), dtype=int)
    cache = {}
    for v in range(3):
        for y in range(2000, 2026):
            Fs = 0.0; F = 0.0; Fo_prev = None; obs = {}
            for j in range(0, 9):
                tau = 4*(y-1) + j - 1 - T0
                eps = sig[tau]*(np.sqrt(kappa)*w[v,tau]/sig[tau] + np.sqrt(1-kappa)*rng.standard_normal())
                Fs += eps
                lam = lam1 if L[v,tau]==1 else lam0
                F = F + lam*(Fs - F)
                obs[j] = F + s_nu*rng.standard_normal()
            a = Fs + s_eta*rng.standard_normal()
            cache[(v,y)] = (obs, a)
    for i in range(len(P)):
        obs, a = cache[(vi[i], yy[i])]
        j = rk[i]
        r_out[i] = obs[j] - obs[j-1]; e_out[i] = a - obs[j]; L_out[i] = L[vi[i], tt[i]-T0]
    return r_out, e_out, L_out

def dk(X, u, t, lags=LAGS):
    h = X*u[:,None]
    idx = t - rounds[0]
    H = np.zeros((len(rounds), X.shape[1])); np.add.at(H, idx, h)
    Om = H.T@H
    for j in range(1, lags+1):
        wj = 1 - j/(lags+1); C = H[j:].T@H[:-j]; Om += wj*(C + C.T)
    XtXi = np.linalg.inv(X.T@X)
    return XtXi@Om@XtXi

def design(zr, L, g, ng=6):
    D = np.eye(ng)[g]
    return np.column_stack([D, D*L[:,None], D*zr[:,None], zr*L])

def analyse(r, e, L):
    zr = np.empty_like(r); ze = np.empty_like(e); kg = []
    for g in range(6):
        m = gg==g
        sr = r[m].std(ddof=1); se = e[m].std(ddof=1)
        zr[m] = (r[m]-r[m].mean())/sr; ze[m] = (e[m]-e[m].mean())/se; kg.append(sr/se)
    X = design(zr, L, gg); beta = np.linalg.lstsq(X, ze, rcond=None)[0]; u = ze - X@beta
    Vm = dk(X, u, tt); c = beta[-1]; et = np.sqrt(Vm[-1,-1])
    bmoy = beta[12:18].mean()
    s2 = (u@u)/(len(u)-X.shape[1]); etiid = np.sqrt(s2*np.linalg.inv(X.T@X)[-1,-1]); neff = len(u)*(etiid/et)**2
    lo, hi = c - CRIT*et, c + CRIT*et
    wv = np.zeros(X.shape[1]); wv[12:18] = 1/6; lobm = bmoy - CRIT*np.sqrt(wv@Vm@wv)
    # rapport de variances
    a_ = []; A_ = []
    for g in range(6):
        m = gg==g
        for l, acc in ((0,a_),(1,A_)):
            mm = m & (L==l); acc.extend(zr[mm]-zr[mm].mean())
    a = np.mean(np.square(a_)); A = np.mean(np.square(A_))
    rap = A/a
    # pertinence : rapport de variances de l'écart de la prévision précédente (e + r = réalisé − prévision t−1)
    zp = np.empty_like(r)
    for g in range(6):
        m = gg==g; pv = e[m]+r[m]; zp[m] = (pv-pv.mean())/pv.std(ddof=1)
    a2=[];A2=[]
    for g in range(6):
        m = gg==g
        for l, acc in ((0,a2),(1,A2)):
            mm = m & (L==l); acc.extend(zp[mm]-zp[mm].mean())
    rap_p = np.mean(np.square(A2))/np.mean(np.square(a2))
    a3=[];A3=[]
    for g in range(6):
        m = gg==g
        for l, acc in ((0,a3),(1,A3)):
            mm = m & (L==l); acc.extend(ze[mm]-ze[mm].mean())
    rap_e = np.mean(np.square(A3))/np.mean(np.square(a3))
    biais = (2*bmoy + np.mean(kg))*0.10*(1/a - 1/A)
    seuil = max(0.10, biais)
    # contrôle positif
    Xb = np.column_stack([np.eye(6)[gg], zr]); bb = np.linalg.lstsq(Xb, ze, rcond=None)[0]; ub = ze - Xb@bb
    Vb = dk(Xb, ub, tt); bpool = bb[-1]; lob = bpool - CRIT*np.sqrt(Vb[-1,-1])
    # épisodes
    tmins = []; cmins = []
    for k,m in epmask.items():
        keep = ~m
        Xk = X[keep]; bk = np.linalg.lstsq(Xk, ze[keep], rcond=None)[0]; uk = ze[keep]-Xk@bk
        Vk = dk(Xk, uk, tt[keep]); tmins.append(bk[-1]/np.sqrt(Vk[-1,-1])); cmins.append(bk[-1])
    tmin = min(tmins); cmin = min(cmins)
    marge = min(seuil - lo, hi - 0.40)
    conflit = int(lo > seuil and hi >= 0.40 and tmin < 1 and cmin > 0)
    pert = int(rap < 1.25 and (lo - seuil) <= 0)
    cpok = int(lob > 0 or lobm > 0)
    nc = pert or (cpok < 1) or (marge >= 0) or conflit
    if nc: verdict = "NC"
    elif (lo - seuil > 0) and hi >= 0.40 and tmin >= 1: verdict = "S"
    else: verdict = "E"
    return dict(etiid=etiid, neff=neff, c=c, et=et, bmoy=bmoy, k=np.mean(kg), rap=rap, biais=biais, bpool=bpool, lob=lob, tmin=tmin, cmin=cmin,
                rap_p=rap_p, rap_e=rap_e, pert=pert, verdict=verdict, cp=cpok, lobm=lobm, marge=marge, conflit=conflit)

# ---------------------------------------------------------------------------------------------------------------------
# Cas simulés (sections 8.2 et 8.3)
# ---------------------------------------------------------------------------------------------------------------------
CENTRAL = dict(lam0=0.58, rho=0.3, kappa=0.6, s_om=0.5, s_nu=0.05, s_eta=1.6)
SCENARIOS = {
    "A central":                  (CENTRAL, 0.285),
    "B chocs correles, Student 3": (dict(lam0=0.58, rho=0.6, kappa=0.8, s_om=0.5, s_nu=0.10, s_eta=1.6, df=3), 0.27),
    "C surprise plus bruitee":    (dict(lam0=0.58, rho=0.3, kappa=0.6, s_om=1.0, s_nu=0.05, s_eta=1.6), 0.285),
    "D chocs peu correles":       (dict(lam0=0.58, rho=0.1, kappa=0.4, s_om=0.5, s_nu=0.05, s_eta=1.6), 0.285),
    "E epreuve":                  (dict(lam0=0.58, rho=0.8, kappa=0.9, s_om=0.5, s_nu=0.10, s_eta=1.6, df=3, vm=2.0), 0.27),
}
GRILLE_C = [1.0, 0.50, 0.40]   # lambda1 du scénario central : c ≈ -0,29 ; ≈ 0,07 ; ≈ 0,19 (c = 0 et c ≈ 0,40 : cas A)

def un_cas(nom, cfg):
    global DF
    cfg = dict(cfg); DF = cfg.pop("df", 4)
    rng = np.random.default_rng(SEED)
    out = [analyse(*simulate(rng, **cfg)) for _ in range(N_TIRAGES)]
    df = pd.DataFrame(out)
    print(f"--- {nom}", json.dumps(cfg), "df", DF, "n", N_TIRAGES)
    print(df[["etiid","neff","c","et","bmoy","k","rap","rap_p","rap_e","biais","bpool","lob","tmin"]].describe().loc[["mean","std","50%"]].round(3).to_string())
    vc = df.verdict.value_counts(normalize=True).round(3).to_dict()
    print("issues", vc, "decisif", round(1-vc.get("NC",0),3), "| CP rate", df.cp.mean().round(3), "| marge>=0", (df.marge>=0).mean().round(3), "| conflit", df.conflit.mean().round(3), "| pert", df.pert.mean().round(3))
    return dict(cas=nom, c_moyen=round(df.c.mean(), 3), survit=round(vc.get("S", 0)*100, 1), eliminee=round(vc.get("E", 0)*100, 1),
                non_concluant=round(vc.get("NC", 0)*100, 1), decisif=round(1-vc.get("NC",0), 3))

if __name__ == "__main__":
    print(f"K20-ZE simulation de decision ; graine {SEED} ; {N_TIRAGES} tirages par cas ; grille : {len(P)} lignes principales, {len(rounds)} tours")
    res = []
    for nom, (base, lam1) in SCENARIOS.items():
        res.append(un_cas(f"{nom} | c = 0", dict(base, lam1=base["lam0"])))
        res.append(un_cas(f"{nom} | c ~ 0,40", dict(base, lam1=lam1)))
    for lam1 in GRILLE_C:
        res.append(un_cas(f"grille 8.3 central | lambda1 = {lam1}", dict(CENTRAL, lam1=lam1)))
    print("\n=== Resume (pourcentages survit / eliminee / non concluant ; probabilite de decision)")
    print(pd.DataFrame(res).to_string(index=False))

    print("\n=== Tableau 8.1 (loi normale, dispersion reelle = 1,2 x et, gardes non comprises)")
    for et in [0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.14]:
        sd = et*1.2
        ligne = [f"et={et:.2f}", f"survit si c>{0.10+CRIT*et:.3f}", f"eliminee si c<{0.40-CRIT*et:.3f}"]
        for c in [0.0, 0.40]:
            ps = 1-norm.cdf((0.10+CRIT*et-c)/sd); pe = norm.cdf((0.40-CRIT*et-c)/sd)
            ligne.append(f"c={c:.2f}: decision {min(1, ps+pe):.3f}")
        print("  ".join(ligne))
