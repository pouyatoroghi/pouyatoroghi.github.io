"""Deterministic checks for the three applied probability notes; Python standard library only."""
import itertools
import math


def chi2_sf_even(n, threshold):
    assert n > 0 and n % 2 == 0
    z = threshold / 2
    if z == 0:
        return 1.
    terms = [k*math.log(z)-math.lgamma(k+1) for k in range(n // 2)]
    largest = max(terms)
    return math.exp(-z+largest) * math.fsum(math.exp(value-largest) for value in terms)


# The chi-square survival function is an exact finite sum for even degrees of freedom.
n, a = 100, 2.0
probability = chi2_sf_even(n, n * a)
moment2 = (a * a / (2 * a - 1)) ** (n / 2) * chi2_sf_even(n, n * (2 * a - 1))
theta = (1 - 1 / a) / 2
rate = (a - 1 - math.log(a)) / 2
assert probability**2 <= moment2 <= math.exp(-2 * n * rate)

# Independent Simpson quadrature of E_P[1{T >= na} dP/dQ], rather than the tail formula.
def integrand(x):
    log_density = (n / 2 - 1) * math.log(x) - x / 2 - n / 2 * math.log(2) - math.lgamma(n / 2)
    return math.exp(log_density + n / 2 * math.log(a) - theta * x)


steps = 20000
lo, hi = n * a, n * a + 600
dx = (hi - lo) / steps
quadrature = dx / 3 * (integrand(lo) + integrand(hi) + math.fsum(
    (4 if i % 2 else 2) * integrand(lo + i * dx) for i in range(1, steps)))
assert math.isclose(moment2, quadrature, rel_tol=1e-8)
print(f"Detector p={probability:.12g}; second moment={moment2:.12g}")
print(f"Relative variance per draw: naive={(1-probability)/probability:.9g}; tilted={moment2/probability**2-1:.9g}")
print(f"Draws for <=10% relative RMSE: naive={math.ceil((1-probability)/probability/.01)}; tilted={math.ceil((moment2/probability**2-1)/.01)}")
tail_errors, ratio_errors = [], []
for dimension in (100, 200, 400):
    tail = chi2_sf_even(dimension, dimension*a)
    second = (a*a/(2*a-1))**(dimension/2) * chi2_sf_even(dimension, dimension*(2*a-1))
    tail_limit = math.exp(-dimension*rate)/((a-1)*math.sqrt(math.pi*dimension))
    ratio_limit = (a-1)*math.sqrt(math.pi*dimension)/2
    tail_errors.append(abs(tail/tail_limit-1))
    ratio_errors.append(abs((second/tail**2)/ratio_limit-1))
    print(f"Asymptotic check n={dimension}: tail/expression={tail/tail_limit:.6f}, relative-second-moment/expression={(second/tail**2)/ratio_limit:.6f}")
assert tail_errors[2] < tail_errors[1] < tail_errors[0]
assert ratio_errors[2] < ratio_errors[1] < ratio_errors[0]

# Exact enumeration of a two-stage, two-state Markov model with stochastic transitions/rewards.
b = ((.65, .35), (.4, .6))
pi = ((.25, .75), (.7, .3))
bad_b = ((.55, .45), (.6, .4))
initial = (.6, .4)
trans = ((.2, .8), (.7, .3))  # Pr(next state=1 | state, action)
reward = ((.15, .7), (.45, .85))  # Pr(reward=1 | state, action)
horizon = 2
q = [[[0.0]*2 for _ in range(2)] for _ in range(horizon)]
v = [[0.0]*2 for _ in range(horizon+1)]
for t in reversed(range(horizon)):
    for s in range(2):
        for action in range(2):
            p = trans[s][action]
            q[t][s][action] = reward[s][action] + (1-p)*v[t+1][0] + p*v[t+1][1]
        v[t][s] = sum(pi[s][action]*q[t][s][action] for action in range(2))
target = sum(initial[s]*v[0][s] for s in range(2))
bad_q = [[[q[t][s][action] + .1*(1+t+s-2*action) for action in range(2)] for s in range(2)] for t in range(horizon)]


def enumerate_estimator(qhat, bhat):
    vhat = [[sum(pi[s][action]*qhat[t][s][action] for action in range(2)) for s in range(2)] for t in range(horizon)] + [[0., 0.]]
    mean = second = bias_rhs = variance_rhs = mass = 0.
    for s0, a0, r0, s1, a1, r1, s2 in itertools.product(range(2), repeat=7):
        states, actions, rewards = [s0, s1, s2], [a0, a1], [r0, r1]
        ppath = initial[s0]
        w = 1.
        value = vhat[0][s0]
        local_bias = local_variance = 0.
        for t in range(horizon):
            s, action, r, snext = states[t], actions[t], rewards[t], states[t+1]
            ppath *= b[s][action] * (reward[s][action] if r else 1-reward[s][action]) * (trans[s][action] if snext else 1-trans[s][action])
            local_bias += w * sum(pi[s][j]*(qhat[t][s][j]-q[t][s][j])*(1-b[s][j]/bhat[s][j]) for j in range(2))
            w *= pi[s][action]/bhat[s][action]
            value += w*(r + vhat[t+1][snext]-qhat[t][s][action])
            conditional_variance = reward[s][action]*(1-reward[s][action]) + trans[s][action]*(1-trans[s][action])*(v[t+1][1]-v[t+1][0])**2
            local_variance += w*w*conditional_variance
        mass += ppath
        mean += ppath*value
        second += ppath*value*value
        bias_rhs += ppath*local_bias
        variance_rhs += ppath*local_variance
    assert math.isclose(mass, 1., abs_tol=1e-12)
    assert math.isclose(mean-target, bias_rhs, abs_tol=1e-12)
    return mean, second-mean*mean, variance_rhs


for qhat, bhat in [(q, b), (bad_q, b), (q, bad_b), (bad_q, bad_b)]:
    mean, variance, rhs = enumerate_estimator(qhat, bhat)
    if qhat is q or bhat is b:
        assert math.isclose(mean, target, abs_tol=1e-12)
    if qhat is q and bhat is b:
        initial_variance = sum(initial[s]*(v[0][s]-target)**2 for s in range(2))
        assert math.isclose(variance, initial_variance+rhs, abs_tol=1e-12)
    print(f"Policy enumeration: true_Q={qhat is q}, true_b={bhat is b}, value={mean:.9f}, bias={mean-target:.9f}")
unseen = math.exp(100000*math.log1p(-.5**20))
print(f"20-step coverage: unseen={unseen:.9f}, minimax absolute-error lower bound={unseen/2:.9f}")

# Two-dimensional Gaussian completion and the matrix determinant lemma.
g11, g12, g22 = 5., 1., 3.
det = g11*g22-g12*g12
u = (.4, -.7)
c = (1.2, -.8)
center = ((g22*c[0]-g12*c[1])/det, (-g12*c[0]+g11*c[1])/det)
quad = lambda z: g11*z[0]**2+2*g12*z[0]*z[1]+g22*z[1]**2
dot = lambda x, y: sum(a*b for a, b in zip(x, y))
assert math.isclose(dot(u,c)-quad(u)/2, -quad(tuple(u[i]-center[i] for i in range(2)))/2+dot(c,center)/2, abs_tol=1e-12)
x = (.6, -1.1)
leverage = (g22*x[0]**2-2*g12*x[0]*x[1]+g11*x[1]**2)/det
updated_det = (g11+x[0]**2)*(g22+x[1]**2)-(g12+x[0]*x[1])**2
assert math.isclose(updated_det/det, 1+leverage, abs_tol=1e-12)
for name, determinant, directional_eigenvalue in [('balanced', 441, 21), ('confounded', 41, 1)]:
    beta = .1*math.sqrt(math.log(determinant)+2*math.log(20))+1
    print(f"Calibration {name}: beta={beta:.9f}, contrast half-width={beta/math.sqrt(directional_eigenvalue):.9f}")
print('PASS: exact finite-model bias/variance, independent quadrature, Gaussian square completion, and determinant identities.')
