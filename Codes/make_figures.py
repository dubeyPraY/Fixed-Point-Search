#!/usr/bin/env python3
# =============================================================================
#  Figure generation for
#  "Ancilla-mediated fixed-point quantum search using Grover iterations"
#
#  This script supersedes the plotting in FOQA_Complexity_FINAL.ipynb.
#
#  WHAT CHANGED (and why) vs. the original notebook
#  -------------------------------------------------
#  The original `calculate_exp` had two issues that made Fig. 5 inconsistent
#  with the corrected manuscript:
#
#   1) Oracle-cost model.  It used
#          oc = 1 + sum_{q=0}^{l-1}(2^q - 1)  = 2^l - l
#      whereas the corrected schedule (amplify-then-check, Grover counts
#      g_0=0, g_j=2^{j-1}-1) gives per-check cost o_j = 1+g_j and a cumulative
#          O_l = sum_{k<=l} o_k = 2^l.
#
#   2) Expectation weighting.  It accumulated  exp_O_j += oc * p  with the
#      *cumulative* success probability p = sum_{m<=l} P(first success at m).
#      The expectation must weight each round's cost by the probability of
#      *first* success at that round:
#          E[O] = sum_l  O_l * [ sin^2(2^l θ) * Π_{m<l} cos^2(2^m θ) ]  (+ tail).
#
#  With both fixed, E(O_j)/k_opt ≈ 1.32 (mean 1.315, max ~1.34), matching the
#  manuscript's corrected "~1.33 ε ~ sqrt(N/M)".  The probability computation
#  (`calculate_CP`) was already correct and is unchanged.
#
#  Output: publication-ready single-column figures (PDF + PNG), Okabe–Ito
#  colour-blind-safe palette, mathtext (set USETEX=True to match the paper's
#  Computer-Modern text exactly on a machine with a LaTeX + dvipng install).
# =============================================================================
import numpy as np
from math import sqrt, pi, asin, sin, cos
import matplotlib as mpl
import matplotlib.pyplot as plt

USETEX = False   # set True on a machine with latex+dvipng for exact CM text

mpl.rcParams.update({
    "figure.dpi": 200, "savefig.dpi": 300,
    "font.family": "serif", "font.serif": ["DejaVu Serif", "cmr10"],
    "text.usetex": USETEX, "mathtext.fontset": "cm", "font.size": 8.5,
    "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 7.4, "axes.linewidth": 0.7, "lines.linewidth": 1.4,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.major.width": 0.7, "ytick.major.width": 0.7,
    "legend.frameon": True, "legend.framealpha": 0.9, "legend.edgecolor": "0.7",
    "grid.linewidth": 0.4, "grid.alpha": 0.5,
})
BLUE, VERM, GREEN, GREY = "#0072B2", "#D55E00", "#009E73", "#555555"
COL = (3.4, 2.55)   # single-column figure size (inches)
N = 10**10

# ---------------------------------------------------------------- model -------
def calculate_CP(theta):
    """Total probability the doubling schedule converges (angles 2^l θ)."""
    l, p, fp = -1, 0.0, 1.0
    while theta * 2**l < pi/2:
        l += 1
        p  += fp * sin(2**l * theta)**2
        fp *= cos(2**l * theta)**2
    return p

def calculate_exp(theta):
    """Expected oracle calls of the corrected schedule (O_l = 2^l)."""
    l, fp, E, lastO = -1, 1.0, 0.0, 1
    while theta * 2**l < pi/2:
        l += 1
        O_l  = 2**l                              # corrected cumulative cost
        E   += O_l * (sin(2**l * theta)**2) * fp # cost * P(first success at l)
        fp  *= cos(2**l * theta)**2
        lastO = O_l
    E += fp * lastO                              # never-converged tail
    return E

# ------------------------------------------------------------- M sweep --------
M = np.array(list(range(1, 50)) +
             list(np.unique(np.logspace(np.log10(50), np.log10(N//100),
                                        1400).astype(np.int64))))
theta = np.array([asin(sqrt(m/N)) for m in M])
kopt  = np.array([int(pi/4/t - 0.5) for t in theta])
P     = np.array([calculate_CP(t)  for t in theta])
E     = np.array([calculate_exp(t) for t in theta])
worst = pi * np.sqrt(N / M)
print(f"min P (plotted) = {P.min():.4f};  E/kopt mean = {(E/kopt).mean():.3f}")

# ================================================================= Fig 4 ======
fig, ax = plt.subplots(figsize=COL)
ax.set_xscale('log'); ax.grid(True, which='both', ls='--')
ax.plot(M, P, color=BLUE, lw=1.4)
ax.axhline(0.9259, color=VERM, ls=(0, (5, 2)), lw=1.1)
ax.text(0.98, 0.9259, r'analytic bound $0.9259$', color=VERM, fontsize=7,
        ha='right', va='bottom', transform=ax.get_yaxis_transform())
ax.set_xlabel(r'Number of solutions $M$'); ax.set_ylabel(r'Probability to converge')
ax.set_ylim(0.90, 1.005); ax.set_xlim(1, N//100)
fig.tight_layout(pad=0.3)
fig.savefig('fig4_probability.pdf'); fig.savefig('fig4_probability.png'); plt.close(fig)

# ================================================================= Fig 5 ======
fig, ax = plt.subplots(figsize=COL)
ax.set_xscale('log'); ax.set_yscale('log'); ax.grid(True, which='both', ls='--')
ax.plot(M, worst, color=GREY, ls=(0, (2, 2)), lw=1.0, label=r'Worst case $\pi\sqrt{N/M}$')
ax.plot(M, E,     color=VERM, lw=1.5, label=r'Fixed-point (expected)')
ax.plot(M, kopt,  color=BLUE, lw=1.5, label=r'Grover optimal (known $M$)')
ax.set_xlabel(r'Number of solutions $M$'); ax.set_ylabel(r'Oracle calls')
ax.set_xlim(1, N//100); ax.legend(loc='upper right')
fig.tight_layout(pad=0.3)
fig.savefig('fig5_oraclecalls.pdf'); fig.savefig('fig5_oraclecalls.png'); plt.close(fig)

# ============================================ Fig A: the soufflé problem =======
th = 0.075; kmax = int(2.4 * (pi/4/th)); ks = np.arange(0, kmax+1)
Pg = np.sin((2*ks + 1) * th)**2
fp, p, l, Oj, Pj = 1.0, 0.0, -1, [], []
while th * 2**l < pi/2:
    l += 1; p += fp*sin(2**l*th)**2; fp *= cos(2**l*th)**2; Oj.append(2**l); Pj.append(p)
Oj, Pj = np.array(Oj), np.array(Pj)
kpk = int(round(pi/4/th - 0.5)); ktr = int(round((pi/th - 1)/2))
fig, ax = plt.subplots(figsize=(3.5, 2.6)); ax.grid(True, ls='--')
ax.plot(ks, Pg, color=BLUE, lw=1.3, label=r'Standard Grover $\sin^2((2k+1)\theta)$')
ax.step(np.r_[0, Oj], np.r_[0, Pj], where='post', color=VERM, lw=1.6, label=r'Fixed-point (cumulative)')
ax.scatter(Oj, Pj, s=11, color=VERM, zorder=6)
ax.scatter([kpk], [np.sin((2*kpk+1)*th)**2], s=16, color=BLUE, zorder=6)
ax.axhline(0.9259, color=GREY, ls=(0, (4, 2)), lw=0.9)
ax.text(kmax*0.985, 0.9259, r'$0.9259$', color=GREY, fontsize=7, ha='right', va='bottom')
ax.annotate('overshoot', xy=(ktr, np.sin((2*ktr+1)*th)**2), xytext=(ktr-1, 0.30),
            fontsize=7.2, color=BLUE, ha='center',
            arrowprops=dict(arrowstyle='->', color=BLUE, lw=0.8))
ax.set_xlabel(r'Oracle calls'); ax.set_ylabel(r'Success probability')
ax.set_xlim(0, kmax); ax.set_ylim(0, 1.03); ax.legend(loc='center right')
fig.tight_layout(pad=0.3)
fig.savefig('figA_souffle.pdf'); fig.savefig('figA_souffle.png'); plt.close(fig)

# ==================================== Fig B: worst-case two-index function =====
x = np.linspace(pi/4, pi/2, 800); pc1 = 1 - np.cos(x)**2 * np.cos(2*x)**2
xm = 1.15026; pm = 1 - cos(xm)**2 * cos(2*xm)**2
fig, ax = plt.subplots(figsize=COL); ax.grid(True, ls='--')
ax.plot(x, pc1, color=BLUE, lw=1.6)
ax.scatter([xm], [pm], s=16, color=VERM, zorder=6)
ax.annotate(r'min $=0.9259$' + '\n' + r'at $x\approx1.150$', xy=(xm, pm),
            xytext=(1.18, 0.955), fontsize=7.2, color=VERM,
            arrowprops=dict(arrowstyle='->', color=VERM, lw=0.8))
ax.set_xlabel(r'$x=2^{c}\theta$')
ax.set_ylabel(r'$p_{c,1}(x)=1-\cos^2 x\,\cos^2 2x$')
ax.set_xlim(pi/4, pi/2); ax.set_ylim(0.92, 1.005)
ax.set_xticks([pi/4, 3*pi/8, pi/2]); ax.set_xticklabels([r'$\pi/4$', r'$3\pi/8$', r'$\pi/2$'])
fig.tight_layout(pad=0.3)
fig.savefig('figB_worstcase.pdf'); fig.savefig('figB_worstcase.png'); plt.close(fig)

# ================================= Fig C: cumulative convergence (few M) =======
fig, ax = plt.subplots(figsize=(3.5, 2.6)); ax.grid(True, ls='--')
for m, c, lab in [(1, BLUE, r'$M=1$'), (100, GREEN, r'$M=10^{2}$'), (10**4, VERM, r'$M=10^{4}$')]:
    t = asin(sqrt(m/N)); fp, p, l, xs, ys = 1.0, 0.0, -1, [], []
    while t * 2**l < pi/2:
        l += 1; p += fp*sin(2**l*t)**2; fp *= cos(2**l*t)**2; xs.append(l); ys.append(p)
    ax.plot(xs, ys, marker='o', ms=3, color=c, lw=1.2, label=lab)
ax.axhline(0.9259, color=GREY, ls=(0, (4, 2)), lw=0.9)
ax.text(0.5, 0.9259, r'$0.9259$', color=GREY, fontsize=7, va='bottom')
ax.set_xlabel(r'Checkpoint index $j$ (angle $2^{j}\theta$)')
ax.set_ylabel(r'Cumulative success $P_j$')
ax.set_ylim(0, 1.03); ax.legend(loc='lower right')
fig.tight_layout(pad=0.3)
fig.savefig('figC_cumulative.pdf'); fig.savefig('figC_cumulative.png'); plt.close(fig)

print("Wrote fig4, fig5, figA, figB, figC (pdf + png).")
