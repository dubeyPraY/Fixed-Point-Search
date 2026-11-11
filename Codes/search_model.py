"""Analytical model for the manuscript dated 11 November 2026.

The main notebook evolves quantum states independently of this model.
"""
import math
from numbers import Integral


def schedule_length(N):
    """Conservative N-only number of checks, Eq. (22)."""
    if not isinstance(N, Integral) or isinstance(N, bool) or N < 2:
        raise ValueError('N must be an integer of at least 2.')
    return math.ceil(math.log2(math.pi) + math.log2(N)/2)


def analyze(N, M, *, cutoff='fixed'):
    """Compute Eq. (35), including the cost of unsuccessful attempts.

    'fixed' is Algorithm 1. 'figure' uses the manuscript plots' M-dependent
    cutoff; it is not an unknown-M stopping rule.
    """
    r = schedule_length(N)
    if not isinstance(M, Integral) or isinstance(M, bool) or not 0 <= M <= N:
        raise ValueError('M must be an integer between 0 and N.')
    if cutoff not in ('fixed', 'figure'):
        raise ValueError("cutoff must be 'fixed' or 'figure'.")
    theta = math.asin(math.sqrt(M/N))
    if cutoff == 'figure' and M == 0:
        raise ValueError('The M-dependent cutoff is undefined when M=0.')
    last = r-1 if cutoff == 'fixed' else max(0, math.ceil(math.log2(math.pi/(2*theta))))
    survival, event_sum = 1.0, 0.0
    rows = []
    for j in range(last+1):
        p = 0.0 if M == 0 else (1.0 if M == N and j == 0 else math.sin(2**j*theta)**2)
        first = survival*p
        event_sum += 2**j*first
        survival *= 1-p
        rows.append(dict(check=j, grover_iterations=0 if j == 0 else 2**(j-1)-1,
                         oracle_calls=2**j, conditional_success=p,
                         first_success=first, cumulative_success=1-survival))
    epsilon = math.floor(math.pi/4*math.sqrt(N/M)-.5) if M else None
    return dict(N=N, M=M, theta=theta, cutoff=cutoff, last_check=last, rows=rows,
                success_probability=1-survival, failure_probability=survival,
                successful_event_cost=event_sum,
                expected_oracle_calls=event_sum+2**last*survival,
                conditional_success_cost=event_sum/(1-survival) if survival < 1 else None,
                max_oracle_calls=2**last, epsilon=epsilon,
                guarantee_budget=math.pi*math.sqrt(N/M) if M else None)
