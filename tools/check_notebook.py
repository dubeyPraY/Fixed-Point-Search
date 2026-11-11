"""Execute the public notebook and its settings checks in the current Python environment.

Run from the repository root:
    python tools/check_notebook.py
    python tools/check_notebook.py --all-cases
    python tools/check_notebook.py --refresh-example
"""
import argparse
import copy
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / 'notebooks' / 'fixed_point_search.ipynb'


def with_settings(notebook, settings):
    result = copy.deepcopy(notebook)
    for cell in result.cells:
        if 'parameters' in cell.metadata.get('tags', []):
            cell.source += '\n' + settings
    return result


def execute(notebook, folder):
    """Use this Python executable, rather than a user's unrelated default kernel."""
    kernels = folder / 'kernels'
    kernel = kernels / 'search-check'
    kernel.mkdir(parents=True, exist_ok=True)
    flags = ['-S'] if sys.flags.no_site else []
    (kernel / 'kernel.json').write_text(json.dumps({
        'argv': [sys.executable, *flags, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': 'Search checks', 'language': 'python',
    }), encoding='utf-8')
    manager = KernelManager(kernel_name='search-check',
        kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernels)]))
    client = NotebookClient(notebook, km=manager, timeout=300, startup_timeout=180,
                            resources={'metadata': {'path': str(ROOT)}})
    try:
        client.execute()
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
    nbformat.validate(notebook)
    for cell in notebook.cells:
        # Execution timings are machine-specific and add noise to notebook diffs.
        cell.metadata.pop('execution', None)
    return notebook


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-cases', action='store_true')
    parser.add_argument('--refresh-example', action='store_true',
                        help='Refresh the committed notebook outputs and examples/default_run.')
    args = parser.parse_args()
    original = nbformat.read(NOTEBOOK, as_version=4)
    with TemporaryDirectory(prefix='search-check-') as temp:
        folder = Path(temp)
        os.environ.setdefault('MPLCONFIGDIR', str(folder / 'matplotlib'))
        os.environ.setdefault('IPYTHONDIR', str(folder / 'ipython'))
        os.environ.setdefault('JUPYTER_RUNTIME_DIR', str(folder / 'runtime'))
        print('Checking the default notebook...', flush=True)
        executed = execute(copy.deepcopy(original), folder)
        image_count = sum('image/png' in output.get('data', {})
            for cell in executed.cells for output in cell.get('outputs', []))
        if image_count != 3:
            raise AssertionError(f'Expected three default figures, found {image_count}.')
        print('PASS: default notebook, tables and three figures', flush=True)
        if args.refresh_example:
            nbformat.write(executed, NOTEBOOK)
            export = with_settings(original,
                f'SAVE_RESULTS = True\nOUTPUT_FOLDER = Path({str(ROOT / "examples" / "default_run")!r})')
            execute(export, folder)
            print('Refreshed notebook outputs and examples/default_run.', flush=True)
        if args.all_cases:
            cases = [
                ('no solutions', 'TOTAL_QUBITS = 10\nSOLUTION_STATES = []'),
                ('multiple solutions and compact circuit',
                 'TOTAL_QUBITS = 4\nSOLUTION_STATES = ["001", "110"]\nSHOW_CIRCUIT = True\nSAVE_RESULTS = True'),
                ('all solutions', 'TOTAL_QUBITS = 4\nSOLUTION_STATES = list(range(8))'),
                ('half marked', 'TOTAL_QUBITS = 4\nSOLUTION_STATES = [0, 1, 2, 3]'),
                ('grouped outcome chart', 'TOTAL_QUBITS = 6\nSOLUTION_STATES = list(range(20))'),
                ('smallest register', 'TOTAL_QUBITS = 2\nSOLUTION_STATES = [1]'),
                ('Qiskit engine and full circuit',
                 'TOTAL_QUBITS = 3\nSOLUTION_STATES = [1]\nENGINE = "qiskit"\nSHOW_CIRCUIT = True\nCIRCUIT_DETAIL = "full"'),
            ]
            cells = []
            for label, settings in cases:
                configured = with_settings(original, settings +
                    f'\nOUTPUT_FOLDER = Path({str(folder / "exports")!r})')
                cells.extend(nbformat.v4.new_code_cell(cell.source)
                             for cell in configured.cells if cell.cell_type == 'code')
                cells.append(nbformat.v4.new_code_cell(
                    'assert success_count + failed_count == SHOTS\n'
                    'assert all(value in MARKED for value in accepted_counts)\n'
                    f'print({"PASS: " + label!r})'))
            checked = execute(nbformat.v4.new_notebook(cells=cells), folder)
            for cell in checked.cells:
                for output in cell.get('outputs', []):
                    if output.output_type == 'stream' and 'PASS:' in output.text:
                        print(output.text.strip(), flush=True)
            required = ['summary.csv', 'checkpoints.csv', 'all_outcomes.csv',
                        'run_config.json', 'comparison.png', 'outcomes.png', 'search.qpy',
                        'epsilon_comparison.csv', 'oracle_scaling.csv', 'oracle_scaling.png']
            for name in required:
                if not (folder / 'exports' / name).is_file():
                    raise AssertionError(f'Missing export: {name}')
            print('PASS: exported tables, settings, figures and circuit', flush=True)


if __name__ == '__main__':
    main()
