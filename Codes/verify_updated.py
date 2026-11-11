"""Check the current manuscript's bound, schedule and query accounting."""
import math
import numpy as np
from search_model import analyze


def main():
    # y=cos(x)^2: failure y(2y-1)^2 has maximum 2/27 at y=1/6.
    x = math.acos(1/math.sqrt(6))
    bound = 1-math.cos(x)**2*math.cos(2*x)**2
    np.testing.assert_allclose(bound, 25/27, atol=1e-14)
    print(f'Two-check bound: {bound:.10f} at x={x:.6f} rad')
    for N in (2, 4, 8, 16, 32, 64, 128):
        for M in range(N+1):
            result = analyze(N, M)
            if M:
                assert result['success_probability'] >= 25/27-1e-12
            else:
                assert result['success_probability'] == 0
                assert result['expected_oracle_calls'] == result['max_oracle_calls']
    default = analyze(512, 1)
    assert default['max_oracle_calls'] == 64
    np.testing.assert_allclose(default['expected_oracle_calls'], 22.75721088215292, atol=1e-12)
    print('261 small-register cases satisfy the bound or the M=0 budget.')
    print('N=512, M=1: maximum 64 queries; mean %.12f.' % default['expected_oracle_calls'])
    print('Eq. (35) successful-event sum: %.12f.' % default['successful_event_cost'])
    print('The mean includes failed attempts. The guarantee budget is not a per-attempt maximum.')


if __name__ == '__main__':
    main()
