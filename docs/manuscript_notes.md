# Manuscript version and conventions

This repository follows the supplied manuscript dated November 11, 2026.
The [reference PDF](manuscript-2026-11-11.pdf) is included unchanged, with its
SHA-256 checksum alongside it. The arXiv link identifies the paper but may
serve a different version. All equation numbers below refer to the local PDF.

| Topic | Reference |
|---|---|
| Grover benchmark epsilon | Eq. (6) |
| Four-dimensional fixed-point operator | Eq. (13) |
| Output of the first check | Eq. (15) |
| State after an unsuccessful check | Eqs. (16), (19) |
| Schedule length and Grover counts | Eqs. (22), (23) |
| Conditional, first and cumulative success | Eqs. (25), (29), (30) |
| Per-check and cumulative query costs | Eqs. (32), (33) |
| Budget sufficient for the success guarantee | Eq. (34) |
| Expected cost of all attempts | Eq. (35) |
| Approximate epsilon comparison | Eq. (36) |
| Gate construction | Appendix A |

## Cost and stopping rules

Algorithm 1 runs checks j=0,...,r-1, where r=ceil(log2(pi sqrt(N))).
Its schedule does not need M. The analytical figure cutoff instead stops at
the first L for which 2^L theta >= pi/2. That cutoff uses M through theta;
it is useful for analysis but is not the stopping rule of the unknown-M search.

Let w_j be the probability of first succeeding at check j and
S_J=sum(2^j w_j). Eq. (35) gives the mean over all attempts:
E_J=S_J+2^J P(failure). The mean conditioned on success is S_J/P(success).
The code names these separately. For N=512, M=1, S_J=22.0735048138 and
E_J=22.7572108822. All unsuccessful attempts have a cost.

The 1.33 epsilon comparison is approximate and depends on the cutoff and
cost convention. On the supplied N=10^10 grid, the all-attempt mean ratio is
1.326455 at the figure cutoff and 1.465243 for the fixed schedule. These are
unweighted grid means, not universal constants.

## Wording qualifications

These notes clarify the reference without editing the supplied manuscript.

- A final "not found" result does not prove M=0. The exact two-check lower
  bound is 25/27, about 92.6%; its complementary error bound is 2/27, about
  7.4%. Rounded percentages should not replace these fractions in exact inequalities.
- The pi sqrt(N/M) budget in Eq. (34) is sufficient to reach the success
  guarantee. Some attempts continue beyond that checkpoint. The maximum
  cost of an attempt is 2^(r-1), set by N.
- Appendix A, page 10, says the ancilla-1 sector is never populated. Successful
  checks do populate |1,S>. The search stops on that outcome. The |1,R>
  component stays zero in the ideal search.
- Eq. (6) is the paper's small-angle, integer benchmark. It is not the exact
  optimal integer for every M/N. At N=8, M=1 it gives 1; two Grover iterations
  give the larger first-peak success probability.
- The displayed r in Eq. (22) is conservative. For arbitrary N it need not
  be the smallest integer satisfying the preceding arcsine condition. The
  notebook uses a power-of-two register and follows the displayed formula.

The code implements ideal uniform preparation. Its one-query-per-G-or-F
accounting follows the paper, including access to a controlled oracle.
Elementary gate count, oracle construction and device noise are separate costs.
