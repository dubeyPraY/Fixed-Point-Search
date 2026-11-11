"""Build F from the oracle and uniform preparation, then read out theta.

Reference: 7 November 2026 manuscript, Eq. (13) and Appendix A.
Matrices use |ancilla>|data> ordering. Dense matrices are for small examples.
"""
import math
import numpy as np


def construct_F_hat_operator(N, marked_indices):
    """Return F = D_conditional C_S, Grover G, and phase oracle O.

    C_S swaps the ancilla sectors on marked states. D_conditional applies
    I-2|u><u| only in sector 0. Neither construction needs theta or M.
    """
    if isinstance(N, bool) or not isinstance(N, (int, np.integer)) or N < 2 or N & (N-1):
        raise ValueError('N must be a power of two, at least 2.')
    marked = tuple(marked_indices)
    if any(isinstance(x, bool) or not isinstance(x, (int, np.integer)) or not 0 <= x < N for x in marked):
        raise ValueError('Marked indices must be integers in [0, N).')
    marked = tuple(sorted(set(marked)))
    identity = np.eye(N, dtype=complex)
    projector = np.zeros((N, N), dtype=complex)
    projector[list(marked), list(marked)] = 1
    oracle = identity-2*projector
    uniform = np.ones(N)/math.sqrt(N)
    reflection = identity-2*np.outer(uniform, uniform)
    zero = np.zeros_like(identity)
    flag = np.block([[identity-projector, projector], [projector, identity-projector]])
    conditional = np.block([[reflection, zero], [zero, identity]])
    return conditional @ flag, -reflection @ oracle, oracle


def apply_F_hat_to_superposition(N, marked_indices):
    operator, _, _ = construct_F_hat_operator(N, marked_indices)
    initial = np.r_[np.ones(N)/math.sqrt(N), np.zeros(N)]
    branches = (operator @ initial).reshape(2, N)
    p0, p1 = np.sum(abs(branches)**2, axis=1)
    state0 = branches[0]/math.sqrt(p0) if p0 > 1e-25 else np.zeros(N, complex)
    state1 = branches[1]/math.sqrt(p1) if p1 > 1e-25 else np.zeros(N, complex)
    theta = math.asin(math.sqrt(float(np.clip(p1, 0, 1))))
    return float(p0), float(p1), theta, state0, state1


def verify_theoretical_formula(N, marked_indices, emergent_theta, state_data_if_0, state_data_if_1):
    marked = sorted(set(marked_indices))
    theta = math.asin(math.sqrt(len(marked)/N))
    s = np.zeros(N); s[marked] = 1
    r = 1-s
    if len(marked): s /= math.sqrt(len(marked))
    if len(marked) < N: r /= math.sqrt(N-len(marked))
    reset = math.cos(2*theta)*r+math.sin(2*theta)*s
    return dict(theoretical_theta_rad=theta, emergent_theta_rad=emergent_theta,
                theta_error=abs(theta-emergent_theta),
                overlap_ancilla_0=float(abs(np.vdot(reset, state_data_if_0))**2) if len(marked)<N else None,
                overlap_ancilla_1=float(abs(np.vdot(s, state_data_if_1))**2) if marked else None)


def main():
    print('N=8: only the marked set changes; theta is read from the output.')
    for marked in ([5], [5, 6], [4, 5, 6, 7]):
        F, _, _ = construct_F_hat_operator(8, marked)
        np.testing.assert_allclose(F.conj().T @ F, np.eye(16), atol=1e-12)
        p0, p1, theta, state0, state1 = apply_F_hat_to_superposition(8, marked)
        check = verify_theoretical_formula(8, marked, theta, state0, state1)
        np.testing.assert_allclose([p0, p1], [1-len(marked)/8, len(marked)/8], atol=1e-12)
        np.testing.assert_allclose([check['theta_error'], check['overlap_ancilla_0'],
                                   check['overlap_ancilla_1']], [0, 1, 1], atol=1e-12)
        print(f'M={len(marked)}: P(flag=1)={p1:.6f}, theta={theta:.6f} rad; both conditional states agree.')
    print('All three operators are unitary and agree with the manuscript.')


if __name__ == '__main__':
    main()
