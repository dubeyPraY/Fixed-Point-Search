
import numpy as np
from scipy.optimize import minimize_scalar

# ---------- 1. the two-index bound  f(x) = 1 - cos^2(x) cos^2(2x) ----------
f = lambda x: 1 - np.cos(x)**2 * np.cos(2*x)**2
res = minimize_scalar(f, bounds=(np.pi/4, np.pi/2), method='bounded')
print("1) two-index bound: min f = %.6f at x = %.4f   f(pi/4)=%.4f  f(pi/2^-)=%.4f"
      % (res.fun, res.x, f(np.pi/4), f(np.pi/2-1e-9)))

# threshold x* where cumulative-through-pass-c already reaches the bound (small-theta limit)
g = lambda x: 1 - np.sin(2*x)**2/(4*x**2) - res.fun
from scipy.optimize import brentq
xstar = brentq(g, 1.0, 1.5)
print("   x* (cumulative reaches bound at pass c alone) = %.4f" % xstar)

# ---------- 2. full algorithm ----------
def analyze(N, M, schedule="corrected", a=None):
    theta = np.arcsin(np.sqrt(M/N))
    th_min = np.arcsin(np.sqrt(1.0/N))
    if a is None:                       # need 2^(a-1) * th_min >= pi/2
        a = int(np.ceil(np.log2((np.pi/2)/th_min))) + 1
    j = np.arange(1, a+1, dtype=float)
    if schedule == "corrected":         # K_j = 2^(j-1) - 1
        phi = 2.0**(j-1) * theta
        O   = 2.0**j - 1
    else:                               # paper's K_j = 2^j - 2
        phi = (2.0**j - 2) * theta
        phi[0] = theta
        O   = 2.0**(j+1) - j - 2
    p    = np.sin(phi)**2
    cos2 = np.cos(phi)**2
    surv = np.concatenate(([1.0], np.cumprod(cos2)))   # surv[k] = prod_{m<=k} cos^2
    S    = surv[:-1]                                   # survival entering pass j
    Pcum = 1 - surv[1:]                                # cumulative success through pass j
    EO   = np.sum(O * S * p) + O[-1] * surv[-1]        # expected calls incl. failure tail
    c    = int(np.argmax(phi >= np.pi/4))              # first index with phi >= pi/4
    Pc1  = Pcum[min(c+1, a-1)]
    Oc1  = O[min(c+1, a-1)]
    k    = int(np.argmax(Pcum >= res.fun))             # first pass reaching the bound
    eps  = np.pi/(4*theta) - 0.5
    sq   = np.sqrt(N/M)
    return dict(theta=theta, a=a, Pc1=Pc1, Oc1=Oc1, phi_c=phi[c],
                EO=EO, EO_eps=EO/eps, EO_sq=EO/sq,
                Ostop=O[k], Ostop_eps=O[k]/eps, Ostop_sq=O[k]/sq,
                Pfinal=Pcum[-1], eps=eps)

N = 1e10
Ms = np.unique(np.round(np.logspace(0, 8.5, 400)).astype(int))
for sch in ["corrected", "paper"]:
    r = [analyze(N, M, sch) for M in Ms]
    print("\n2) schedule = %s   (N=1e10, a=%d)" % (sch, r[0]['a']))
    print("   min cumulative P at pass c+1 over M : %.4f" % min(x['Pc1'] for x in r))
    print("   E[O]/sqrt(N/M):  min %.2f  mean %.2f  max %.2f"
          % (min(x['EO_sq'] for x in r), np.mean([x['EO_sq'] for x in r]), max(x['EO_sq'] for x in r)))
    print("   E[O]/eps      :  min %.2f  mean %.2f  max %.2f"
          % (min(x['EO_eps'] for x in r), np.mean([x['EO_eps'] for x in r]), max(x['EO_eps'] for x in r)))
    print("   worst-case calls to reach the bound, /sqrt(N/M): max %.2f   /eps: max %.2f"
          % (max(x['Ostop_sq'] for x in r), max(x['Ostop_eps'] for x in r)))
    print("   O_{c+1}/sqrt(N/M) (unrefined bound): max %.2f" % max(x['Oc1_sq'] if 'Oc1_sq' in x else x['Oc1']/np.sqrt(N/M) for x, M in zip(r, Ms)))

# ---------- 3. does a = ceil(log2(eps0)) suffice, as the paper states? ----------
eps0 = np.pi/4*np.sqrt(N) - 0.5
a_paper = int(np.ceil(np.log2(eps0)))
r = analyze(N, 1, "corrected", a=a_paper)
print("\n3) paper's a (2^a >= eps0) = %d  -> final cumulative P at M=1: %.4f" % (a_paper, r['Pfinal']))
r2 = analyze(N, 1, "corrected")
print("   required a = %d                    -> final cumulative P at M=1: %.4f" % (r2['a'], r2['Pfinal']))
