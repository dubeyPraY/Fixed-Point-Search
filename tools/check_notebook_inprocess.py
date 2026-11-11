"""Execute notebook cells without starting a Jupyter kernel.

This checks Python code, drawings and exports. It does not test the kernel
protocol or notebook magics. Use check_notebook.py for those checks.
"""
import argparse
import base64
import contextlib
import io
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
import nbformat

ROOT = Path(__file__).resolve().parents[1]


def execute(path, settings=None):
    notebook = nbformat.read(path, as_version=4)
    namespace = {'__name__': '__main__'}
    current_outputs = []

    def display(*objects, **kwargs):
        for obj in objects:
            if isinstance(obj, Figure):
                buffer = io.BytesIO()
                obj.savefig(buffer, format='png', bbox_inches='tight')
                data = {'image/png': base64.b64encode(buffer.getvalue()).decode('ascii'),
                        'text/plain': '<matplotlib figure>'}
            elif hasattr(obj, '_repr_html_'):
                data = {'text/html': obj._repr_html_()}
            elif hasattr(obj, '_repr_markdown_'):
                data = {'text/markdown': obj._repr_markdown_()}
            else:
                data = {'text/plain': str(obj)}
            current_outputs.append(nbformat.v4.new_output('display_data', data=data, metadata={}))

    previous = Path.cwd()
    os.chdir(ROOT)
    try:
        count = 0
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != 'code': continue
            count += 1
            current_outputs = []
            output = io.StringIO()
            # Only the inline backend magic is omitted. Unexpected magics fail.
            source = '\n'.join(line for line in cell.source.splitlines()
                               if line.strip() != '%matplotlib inline')
            # The notebook imports display itself; redirect it after that import.
            source = source.replace('from IPython.display import display, HTML, Markdown',
                                    'from IPython.display import HTML, Markdown')
            source = source.replace('from IPython.display import display', '')
            namespace['display'] = display
            with contextlib.redirect_stdout(output):
                exec(compile(source, f'{path.name}:cell {index}', 'exec'), namespace)
            if output.getvalue():
                current_outputs.insert(0, nbformat.v4.new_output('stream', name='stdout', text=output.getvalue()))
            cell.outputs = current_outputs
            cell.execution_count = count
            cell.metadata.pop('execution', None)
            if 'parameters' in cell.metadata.get('tags', []):
                namespace.update(settings or {})
        nbformat.validate(notebook)
    finally:
        os.chdir(previous)
    return notebook, namespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-cases', action='store_true')
    parser.add_argument('--refresh-example', action='store_true')
    args = parser.parse_args()
    path = ROOT/'notebooks/fixed_point_search.ipynb'
    notebook, ns = execute(path)
    print('PASS: default notebook', flush=True)
    if args.refresh_example:
        nbformat.write(notebook, path)
        execute(path, dict(SAVE_RESULTS=True, OUTPUT_FOLDER=ROOT/'examples/default_run'))
        print('Refreshed saved outputs and default example.', flush=True)
    with TemporaryDirectory(prefix='search-direct-') as temporary:
        if args.all_cases:
            cases = [
                ('no solutions', dict(SOLUTION_STATES=[])),
                ('multiple solutions and compact circuit', dict(TOTAL_QUBITS=4, SOLUTION_STATES=['001','110'], SHOW_CIRCUIT=True, SAVE_RESULTS=True)),
                ('all solutions', dict(TOTAL_QUBITS=4, SOLUTION_STATES=list(range(8)))),
                ('half marked', dict(TOTAL_QUBITS=4, SOLUTION_STATES=[0,1,2,3])),
                ('grouped outcomes', dict(TOTAL_QUBITS=6, SOLUTION_STATES=list(range(20)))),
                ('smallest register', dict(TOTAL_QUBITS=2, SOLUTION_STATES=[1])),
                ('Qiskit engine and full circuit', dict(TOTAL_QUBITS=3, SOLUTION_STATES=[1], ENGINE='qiskit', SHOW_CIRCUIT=True, CIRCUIT_DETAIL='full')),
            ]
            for name, settings in cases:
                settings['OUTPUT_FOLDER'] = Path(temporary)
                _, ns = execute(path, settings)
                assert ns['success_count']+ns['failed_count'] == ns['SHOTS']
                assert set(ns['accepted_counts']).issubset(ns['MARKED'])
                print('PASS:', name, flush=True)
            for filename in ('summary.csv', 'checkpoints.csv', 'all_outcomes.csv', 'run_config.json',
                             'comparison.png', 'outcomes.png', 'search.qpy', 'epsilon_comparison.csv',
                             'oracle_scaling.csv', 'oracle_scaling.png'):
                assert (Path(temporary)/filename).is_file(), filename
            print('PASS: exported tables, figures, settings and circuit', flush=True)
    research_path = ROOT/'Codes/FOQA_Complexity_corrected.ipynb'
    research, _ = execute(research_path)
    if args.refresh_example: nbformat.write(research, research_path)
    print('PASS: research notebook and five plots', flush=True)


if __name__ == '__main__':
    main()
