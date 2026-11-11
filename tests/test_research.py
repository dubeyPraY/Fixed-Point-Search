"""Cross-check research calculations against the independent gate notebook."""
import math
from pathlib import Path
import sys
import unittest
import numpy as np
from qiskit.quantum_info import Operator
from test_notebook import F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'Codes'))
from search_model import analyze
from theta_emerges import construct_F_hat_operator, apply_F_hat_to_superposition, verify_theoretical_formula


class ResearchTests(unittest.TestCase):
    def test_full_operator_matches_gates_and_is_unitary(self):
        for n in (1, 2, 3):
            N = 2**n
            for marked in ([], [N-1], list(range(N//2)), list(range(N))):
                with self.subTest(N=N, marked=marked):
                    op, g, oracle = construct_F_hat_operator(N, marked)
                    np.testing.assert_allclose(op.conj().T@op, np.eye(2*N), atol=1e-12)
                    np.testing.assert_allclose(op, Operator(F['fixed_point_circuit'](n, marked)).data, atol=1e-12)
                    np.testing.assert_allclose(g, Operator(F['grover_circuit'](n, marked)).data, atol=1e-12)
                    p0, p1, theta, state0, state1 = apply_F_hat_to_superposition(N, marked)
                    np.testing.assert_allclose([p0, p1], [1-len(marked)/N, len(marked)/N], atol=1e-12)
                    check = verify_theoretical_formula(N, marked, theta, state0, state1)
                    self.assertLess(check['theta_error'], 1e-7)
                    for key in ('overlap_ancilla_0', 'overlap_ancilla_1'):
                        if check[key] is not None: self.assertAlmostEqual(check[key], 1, places=12)

    def test_costs_match_statevector_and_telescoping_identity(self):
        for n in range(1, 8):
            N = 2**n
            for M in range(N+1):
                with self.subTest(N=N, M=M):
                    theory = analyze(N, M)
                    actual = F['exact_search'](n, range(M))
                    for key in ('success_probability', 'failure_probability', 'expected_oracle_calls', 'max_oracle_calls'):
                        self.assertAlmostEqual(theory[key], actual[key], places=10)
                    if M:
                        theta = math.asin(math.sqrt(M/N))
                        q = theory['max_oracle_calls']
                        failure = (math.sin(2*q*theta)/(2*q*math.sin(theta)))**2
                        self.assertAlmostEqual(theory['failure_probability'], failure, places=12)
                        self.assertGreaterEqual(theory['success_probability'], 25/27-1e-12)

    def test_default_and_cutoff_distinctions(self):
        result = analyze(512, 1)
        self.assertEqual(result['max_oracle_calls'], 64)
        self.assertEqual(result['epsilon'], 17)
        self.assertAlmostEqual(result['expected_oracle_calls'], 22.75721088215292, places=10)
        self.assertAlmostEqual(result['successful_event_cost'], 22.073504813780723, places=10)
        self.assertEqual(analyze(512, 3, cutoff='figure')['last_check'], 5)
        self.assertEqual(analyze(512, 3)['last_check'], 6)
        self.assertGreater(analyze(512, 3)['expected_oracle_calls'], analyze(512, 3, cutoff='figure')['expected_oracle_calls'])
        dense = analyze(512, 511)
        self.assertGreater(dense['failure_probability'], 0)
        self.assertGreater(dense['max_oracle_calls'], dense['guarantee_budget'])
        with self.assertRaises(ValueError): analyze(512, 0, cutoff='figure')


if __name__ == '__main__':
    unittest.main()
