"""Numerical plots for the manuscript dated 11 November 2026.

The figure cutoff depends on M. Algorithm 1 instead uses a fixed N-based
schedule. Cost plots distinguish Eq. (35) from its successful-event contribution.
Run from any folder; output goes to research_results/ unless --output is set.
"""
import argparse
import csv
from pathlib import Path
import math
import numpy as np
import matplotlib.pyplot as plt
from search_model import analyze


def make_figures(N=10**10):
    """Return named figures and the numerical sweep without writing files."""
    if N < 100:
        raise ValueError('Use N >= 100 for the sparse-solution plot grid.')
    M = np.unique(np.r_[np.arange(1, min(50, N//100+1)),
        np.logspace(np.log10(min(50, N//100)), np.log10(N//100), 1400).astype(np.int64)])
    figure = [analyze(N, int(m), cutoff='figure') for m in M]
    fixed = [analyze(N, int(m)) for m in M]
    eps = np.array([r['epsilon'] for r in fixed])
    event = np.array([r['successful_event_cost'] for r in figure])
    figure_mean = np.array([r['expected_oracle_calls'] for r in figure])
    fixed_mean = np.array([r['expected_oracle_calls'] for r in fixed])
    figures = {}
    with plt.rc_context({'font.size': 10, 'axes.grid': True, 'grid.alpha': .25}):
        fig, ax = plt.subplots(figsize=(6, 4), layout='constrained')
        ax.semilogx(M, [r['success_probability'] for r in figure], label='M-dependent figure cutoff')
        ax.semilogx(M, [r['success_probability'] for r in fixed], alpha=.7, label='Fixed N-based schedule')
        ax.axhline(25/27, color='gray', ls='--', label='Bound: 25/27')
        ax.set(xlabel='Number of solutions M', ylabel='Cumulative success probability', ylim=(.9, 1.005))
        ax.legend(fontsize=8)
        figures['fig5_probability'] = fig

        fig, ax = plt.subplots(figsize=(7, 4.5), layout='constrained')
        ax.loglog(M, math.pi*np.sqrt(N/M), '--', color='gray', label='Budget sufficient for success guarantee')
        ax.loglog(M, eps, label='Grover benchmark, Eq. (6)')
        ax.loglog(M, event, ':', label='Figure cutoff: successful-event contribution')
        ax.loglog(M, figure_mean, label='Figure cutoff: Eq. (35), all attempts')
        ax.loglog(M, fixed_mean, label='Fixed schedule: Eq. (35), all attempts')
        ax.set(xlabel='Number of solutions M', ylabel='Oracle calls')
        ax.legend(fontsize=8)
        figures['fig7_oraclecalls'] = fig

        fig, ax = plt.subplots(figsize=(6, 4), layout='constrained')
        for m in (1, 100, 10000):
            if m > N: continue
            r = analyze(N, m)
            ax.plot([x['check'] for x in r['rows']], [x['cumulative_success'] for x in r['rows']],
                    marker='.', label=f'M={m:,}')
        ax.axhline(25/27, color='gray', ls='--', label='Bound: 25/27')
        ax.set(xlabel='Checkpoint j', ylabel='Cumulative success probability', ylim=(0, 1.04))
        ax.legend(fontsize=8)
        figures['fig6_cumulative'] = fig

        theta = .075
        ks = np.arange(int(2.4*math.pi/(4*theta))+1)
        last = math.ceil(math.log2(math.pi/(2*theta)))
        q = 2**np.arange(last+1)
        cumulative = 1-np.cumprod(np.cos(q*theta)**2)
        fig, ax = plt.subplots(figsize=(6, 4), layout='constrained')
        ax.plot(ks, np.sin((2*ks+1)*theta)**2, label='Grover')
        ax.step(np.r_[0, q], np.r_[0, cumulative], where='post', label='Fixed-point cumulative success')
        ax.axhline(25/27, color='gray', ls='--', label='Bound: 25/27')
        ax.set(xlabel='Oracle calls', ylabel='Success probability', xlim=(0, max(ks)), ylim=(0, 1.04))
        ax.legend(fontsize=8)
        figures['fig3_souffle'] = fig

        x = np.linspace(math.pi/4, math.pi/2, 800)
        fig, ax = plt.subplots(figsize=(6, 4), layout='constrained')
        ax.plot(x, 1-np.cos(x)**2*np.cos(2*x)**2)
        xm = math.acos(1/math.sqrt(6))
        ax.scatter([xm], [25/27], color='tab:orange', label='Minimum: 25/27')
        ax.set(xlabel='x = 2^c theta (radians)', ylabel='Two-check success probability')
        ax.legend()
        figures['diagnostic_two_check_bound'] = fig
    rows = [[int(m), r['epsilon'], f['last_check'], r['last_check'],
             f['successful_event_cost'], f['expected_oracle_calls'], r['expected_oracle_calls']]
            for m, f, r in zip(M, figure, fixed)]
    return figures, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('research_results'))
    parser.add_argument('--format', choices=('png', 'pdf', 'both'), default='both')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    figures, rows = make_figures()
    for name, figure in figures.items():
        for extension in (('png', 'pdf') if args.format == 'both' else (args.format,)):
            figure.savefig(args.output/f'{name}.{extension}', dpi=180)
        plt.close(figure)
    with (args.output/'oracle_scaling.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['M', 'epsilon_eq6', 'figure_last_check', 'fixed_last_check',
                         'figure_successful_event_cost', 'figure_all_attempt_cost', 'fixed_all_attempt_cost'])
        writer.writerows(rows)
    values = np.asarray(rows)
    for name, column in [('Successful-event contribution, figure cutoff', 4), ('Eq. (35), figure cutoff', 5), ('Eq. (35), fixed schedule', 6)]:
        ratios = values[:, column]/values[:, 1]
        print(f'{name}: ratio to epsilon min={ratios.min():.6f}, mean={ratios.mean():.6f}, max={ratios.max():.6f}')
    print('Ratios are finite-grid summaries, not universal constants.')
    print('Wrote figures and sweep to', args.output.resolve())


if __name__ == '__main__':
    main()
