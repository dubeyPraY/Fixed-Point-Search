# Run the research calculations

From the repository root, after installing `requirements.txt`:

```bash
python Codes/theta_emerges.py
python Codes/verify_updated.py
python Codes/make_figures.py --output research_results
```

The first script builds the full fixed-point operator for three small marked
sets. It checks unitarity, flag probabilities and normalized conditional states.
The second checks the success bound, the no-solution case and query costs.
The third exports figures and `oracle_scaling.csv`. Use `--format png` to
export only PNGs, or `--format pdf` to export only PDFs.

`search_model.py` holds the analytical probabilities and costs shared by the
research scripts. The main notebook evolves quantum amplitudes independently.
Tests compare the two approaches.

| Output | November 11 manuscript |
|---|---|
| fig3_souffle | Fig. 3: Grover overshoot and cumulative fixed-point success |
| fig5_probability | Fig. 5, with a fixed-schedule comparison added |
| fig6_cumulative | Fig. 6, continued through the fixed schedule |
| fig7_oraclecalls | Fig. 7, with cost definitions and both cutoffs shown |
| diagnostic_two_check_bound | Extra diagnostic for Eqs. (27)-(31) |

These plots explain the manuscript's numerical quantities. They are not
pixel-for-pixel copies, and they do not generate the circuit diagrams.
The research notebook uses the same plotting functions so its results stay
in step with the script.

The figure cutoff depends on M. The fixed schedule depends only on N. Both
are named on the plots. Eq. (35) includes failed attempts; its successful-event
contribution is shown separately. See
[manuscript notes](manuscript_notes.md) for the formulas.

## Rebuild the companion guide

The editable text is `Codes/companion.md`. To rebuild its PDF:

```bash
python -m pip install -r requirements-docs.txt
python tools/build_companion.py
```

Check every page after changing the text. The reference manuscript is a
separate file and should remain unchanged.
