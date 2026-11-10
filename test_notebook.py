"""Check the functions defined in the public notebook itself."""
import ast
import json
import math
import unittest
from pathlib import Path

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector

NOTEBOOK = Path(__file__).resolve().parents[1] / 'notebooks' / 'fixed_point_search.ipynb'


def load_notebook_functions():
    """Load only function definitions; do not run plots or the demo during import."""
    namespace = dict(np=np, math=math, QuantumCircuit=QuantumCircuit,
                     QuantumRegister=QuantumRegister, ClassicalRegister=ClassicalRegister,
                     Statevector=Statevector)
    notebook = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
    for cell in notebook['cells']:
        if cell['cell_type'] != 'code':
            continue
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        source = '\n'.join(line for line in source.splitlines() if not line.startswith('%'))
        definitions = [node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)]
        if definitions:
            exec(compile(ast.Module(body=definitions, type_ignores=[]), str(NOTEBOOK), 'exec'), namespace)
    return namespace


F = load_notebook_functions()


class NotebookTests(unittest.TestCase):
    def test_gate_blocks_on_arbitrary_states(self):
        rng = np.random.default_rng(22)
        for n in (1, 3, 9):
            marked = (0, 2**n-1)
            vector = rng.normal(size=2**(n+1)) + 1j*rng.normal(size=2**(n+1))
            state = Statevector(vector/np.linalg.norm(vector))
            with self.subTest(data_qubits=n):
                np.testing.assert_allclose(
                    state.evolve(F['fixed_point_circuit'](n, marked)).data,
                    F['fast_f'](state, marked).data, atol=1e-9)
                np.testing.assert_allclose(
                    state.evolve(F['grover_circuit'](n, marked), qargs=list(range(n))).data,
                    F['fast_g'](state, marked).data, atol=1e-9)

    def test_complete_ten_qubit_search(self):
        fast = F['exact_search'](9, [37])
        gates = F['exact_search'](9, [37], engine='qiskit')
        np.testing.assert_allclose(
            [row['conditional_success'] for row in fast['rows']],
            [row['conditional_success'] for row in gates['rows']], atol=1e-9)

    def test_theory_edges_and_query_cost(self):
        for n in (3, 9, 10):
            for m in (0, 1, 3, 2**(n-1), 2**n-1, 2**n):
                with self.subTest(data_qubits=n, solutions=m):
                    result = F['exact_search'](n, range(m))
                    theta = math.asin(math.sqrt(m/2**n))
                    failure = 1.0
                    for row in result['rows']:
                        failure *= math.cos(2**row['check']*theta)**2
                        self.assertAlmostEqual(row['cumulative_success'], 1-failure, places=10)
                    expected = sum(row['oracle_calls']*row['first_success'] for row in result['rows'])
                    expected += result['failure_probability']*result['max_oracle_calls']
                    self.assertAlmostEqual(expected, result['expected_oracle_calls'], places=9)
                    if m:
                        self.assertGreaterEqual(result['success_probability'], 25/27-1e-10)
                    else:
                        self.assertEqual(result['success_probability'], 0)
                        self.assertEqual(result['expected_oracle_calls'], result['max_oracle_calls'])

    def test_failed_measurement_keeps_the_reset_state(self):
        n, N, marked = 4, 16, (2, 9, 13)
        theta = math.asin(math.sqrt(len(marked)/N))
        r = np.ones(N); r[list(marked)] = 0; r /= np.linalg.norm(r)
        s = np.zeros(N); s[list(marked)] = 1; s /= np.linalg.norm(s)
        for phi in (0.15, 0.73, 2.2):
            state = Statevector(np.r_[np.cos(phi)*r+np.sin(phi)*s, np.zeros(N)])
            branches = F['fast_f'](state, marked).data.reshape(2, N)
            self.assertAlmostEqual(float(np.linalg.norm(branches[1])**2), math.sin(phi)**2)
            reset = Statevector(branches[0]/np.linalg.norm(branches[0]))
            self.assertTrue(reset.equiv(np.cos(2*theta)*r+np.sin(2*theta)*s))

    def test_settings_and_circuit_size(self):
        self.assertEqual(F['schedule'](9), [0, 0, 1, 3, 7, 15, 31])
        self.assertEqual(F['parse_solutions'](['001', 1, '110'], 3), (1, 6))
        self.assertEqual(F['parse_solutions']([], 3), ())
        for invalid in ([8], [-1], [1.5], ['102'], ['0000'], [True]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                F['parse_solutions'](invalid, 3)
        for builder in ('dynamic_circuit', 'compact_search_circuit'):
            circuit = F[builder](9, [37])
            self.assertEqual(circuit.num_qubits, 10)
            self.assertEqual(circuit.count_ops()['if_else'], 7)


if __name__ == '__main__':
    unittest.main(verbosity=2)
