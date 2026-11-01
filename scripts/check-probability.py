"""Deterministic checks for all seven mathematical notes and the three puzzles; standard library only."""
import itertools
import math
from fractions import Fraction


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
    mean = second = bias_rhs = variance_rhs = penalty_rhs = mass = 0.
    for s0, a0, r0, s1, a1, r1, s2 in itertools.product(range(2), repeat=7):
        states, actions, rewards = [s0, s1, s2], [a0, a1], [r0, r1]
        ppath = initial[s0]
        w = 1.
        value = vhat[0][s0]
        local_bias = local_variance = local_penalty = 0.
        for t in range(horizon):
            s, action, r, snext = states[t], actions[t], rewards[t], states[t+1]
            ppath *= b[s][action] * (reward[s][action] if r else 1-reward[s][action]) * (trans[s][action] if snext else 1-trans[s][action])
            local_bias += w * sum(pi[s][j]*(qhat[t][s][j]-q[t][s][j])*(1-b[s][j]/bhat[s][j]) for j in range(2))
            weighted_errors = [pi[s][j]/b[s][j]*(qhat[t][s][j]-q[t][s][j]) for j in range(2)]
            average_error = sum(b[s][j]*weighted_errors[j] for j in range(2))
            local_penalty += w*w*sum(b[s][j]*(weighted_errors[j]-average_error)**2 for j in range(2))
            w *= pi[s][action]/bhat[s][action]
            value += w*(r + vhat[t+1][snext]-qhat[t][s][action])
            conditional_variance = reward[s][action]*(1-reward[s][action]) + trans[s][action]*(1-trans[s][action])*(v[t+1][1]-v[t+1][0])**2
            local_variance += w*w*conditional_variance
        mass += ppath
        mean += ppath*value
        second += ppath*value*value
        bias_rhs += ppath*local_bias
        variance_rhs += ppath*local_variance
        penalty_rhs += ppath*local_penalty
    assert math.isclose(mass, 1., abs_tol=1e-12)
    assert math.isclose(mean-target, bias_rhs, abs_tol=1e-12)
    return mean, second-mean*mean, variance_rhs, penalty_rhs


for qhat, bhat in [(q, b), (bad_q, b), (q, bad_b), (bad_q, bad_b)]:
    mean, variance, rhs, penalty = enumerate_estimator(qhat, bhat)
    if qhat is q or bhat is b:
        assert math.isclose(mean, target, abs_tol=1e-12)
    if bhat is b:
        initial_variance = sum(initial[s]*(v[0][s]-target)**2 for s in range(2))
        assert math.isclose(variance, initial_variance+rhs+penalty, abs_tol=1e-12)
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

# Nonunique optimum: likelihood-ratio-weighted value error is constant over actions.
equal_variance_q = [[[q[t][s][a]+b[s][a]/pi[s][a] for a in range(2)] for s in range(2)] for t in range(horizon)]
_, oracle_variance, _, _ = enumerate_estimator(q, b)
for scale in (-2., -.5, .5, 2.):
    perturbed_q = [[[q[t][s][a]+scale*(1+t+s-2*a) for a in range(2)] for s in range(2)] for t in range(horizon)]
    _, fitted_variance, _, penalty = enumerate_estimator(perturbed_q, b)
    assert penalty > 0
    assert math.isclose(fitted_variance-oracle_variance, penalty, abs_tol=1e-11)
_, same_variance, _, zero_penalty = enumerate_estimator(equal_variance_q, b)
assert math.isclose(same_variance, oracle_variance, abs_tol=1e-12)
assert abs(zero_penalty) < 1e-24
print('PASS: exact fitted-value variance penalty, including a nonunique minimizing fit.')

# PAC-Bayes: enumerate the data distribution, then verify the common event and Gibbs identity.
n, prob_one, lam, delta = 12, .2, 8., .2
prior = (.3, .7)  # Constant-zero and constant-one classifiers.
pop_risk = (prob_one, 1-prob_one)
mgf_average = bad_mass = 0.
def kl2(qdist, pdist):
    return math.fsum(qi*math.log(qi/pi) for qi,pi in zip(qdist,pdist) if qi)
for k in range(n+1):
    mass = math.comb(n,k)*prob_one**k*(1-prob_one)**(n-k)
    empirical = (k/n, 1-k/n)
    moment = math.fsum(prior[j]*math.exp(lam*(pop_risk[j]-empirical[j])) for j in range(2))
    mgf_average += mass*moment
    on_event = math.log(moment) <= lam*lam/(8*n)+math.log(1/delta)
    if not on_event: bad_mass += mass
    weights = [prior[j]*math.exp(-lam*empirical[j]) for j in range(2)]
    normalizer = sum(weights)
    gibbs = [w/normalizer for w in weights]
    for q0 in (0., .1, .37, .8, 1.):
        posterior = (q0,1-q0)
        empirical_risk = sum(posterior[j]*empirical[j] for j in range(2))
        lhs = empirical_risk+kl2(posterior,prior)/lam
        rhs = (kl2(posterior,gibbs)-math.log(normalizer))/lam
        assert math.isclose(lhs,rhs,abs_tol=1e-12)
        if on_event:
            population = sum(posterior[j]*pop_risk[j] for j in range(2))
            assert population <= lhs+math.log(1/delta)/lam+lam/(8*n)+1e-12
assert mgf_average <= math.exp(lam*lam/(8*n))
assert bad_mass <= delta
assert .085495 < .05+(20+math.log(20))/1000+1000/80000 < .085496
assert math.sqrt(math.log(20)/200) < .5  # Invalid data-dependent-prior certificate.
print('PASS: PAC-Bayes exponential moment, common event, Gibbs identity, and numerical certificate.')

# Gaussian mixture integral, and all three reported confidence-sequence radii.
for time, rounded in [(100,.365639),(1000,.096064),(10000,.032730)]:
    radius = math.sqrt((100+time)*(2*math.log(20)+math.log1p(time/100)))/time
    assert abs(radius-rounded) <= .0000005
# A separate numerical integration checks the square-completion normalization.
rho, variance_time, sum_noise = 2., 3., .7
integral_steps, left, right = 10000, -10., 10.
step = (right-left)/integral_steps
def mixture_integrand(u):
    return math.sqrt(rho/(2*math.pi))*math.exp(u*sum_noise-(rho+variance_time)*u*u/2)
num = step/3*(mixture_integrand(left)+mixture_integrand(right)+math.fsum(
    (4 if j%2 else 2)*mixture_integrand(left+j*step) for j in range(1,integral_steps)))
closed = math.sqrt(rho/(rho+variance_time))*math.exp(sum_noise**2/(2*(rho+variance_time)))
assert math.isclose(num,closed,rel_tol=1e-12)
assert math.sqrt(.02*math.log(20)) < .5  # Invalid plug-in-variance interval excludes either Bernoulli outcome.
print('PASS: confidence-sequence normalization, numerical radii, and plug-in failure.')

# Denoising: independent posterior probabilities versus analytic moments and derivatives.
a, sigma = 2., 1.3
for y in (-2., -.2, 0., .7, 3.):
    plus = 1/(1+math.exp(-2*a*y/sigma**2))
    mean = a*(2*plus-1)
    variance = 4*a*a*plus*(1-plus)
    assert math.isclose(mean,a*math.tanh(a*y/sigma**2),abs_tol=1e-12)
    assert math.isclose(variance,a*a/math.cosh(a*y/sigma**2)**2,abs_tol=1e-12)
    eps = 1e-5
    derivative = (a*math.tanh(a*(y+eps)/sigma**2)-a*math.tanh(a*(y-eps)/sigma**2))/(2*eps)
    assert math.isclose(derivative,variance/sigma**2,rel_tol=1e-7,abs_tol=1e-10)
for k in (1,2,10,100):
    excess = (1-math.exp(-4*k**4))/(2*k*k)
    assert 0 <= excess <= 1/(k*k)
    assert .5+k*math.cos(k*k*(math.pi/(k*k))) < 0
print('PASS: denoising posterior moments and vanishing-risk/negative-variance counterexample.')

# Floor series: exact integration of partial sums; no floating-point floor near a jump.
for base, denominator, depth in [(2,Fraction(3),10),(3,Fraction(4),7),(2,Fraction(5,2),10),(4,Fraction(11,2),5)]:
    count = base**depth
    partial_integral = Fraction(0)
    for j in range(count):
        value = sum((Fraction(j//base**(depth-k))/denominator**k for k in range(1,depth+1)),Fraction(0))
        partial_integral += value*value/count
    constant = Fraction(base-1)/(denominator-base)**2*(Fraction(2*base-1,6)+Fraction(base-1)/(2*(denominator-1)))
    exact = denominator**2*constant/(denominator**2-1)
    ratio = base/denominator
    tail = ratio**(depth+1)/(1-ratio)
    bound = 2*base/(denominator-base)*tail
    assert partial_integral <= exact <= partial_integral+bound
    if base==2 and denominator==3: assert exact==Fraction(27,32)
print('PASS: floor-series closed form inside exact rational truncation enclosures.')

# Puzzle 1: enumerate every subset in the proposed strategy for small N, including endpoints.
for size in range(2,9):
    for budget in range(size+1):
        risk = Fraction(size-budget,2*size-budget)
        subsets = list(itertools.combinations(range(size),budget))
        for marked in range(size):
            missed = sum(marked not in subset for subset in subsets)
            error = Fraction(missed,len(subsets))*(1-risk)
            assert error==risk
# Puzzle 2: a finite joint law with calibrated but unequal forecasts.
weight=Fraction(2,5)
identity=Fraction(0)
for outcome in (0,1):
    first,second=Fraction(outcome),Fraction(1,2)
    average=weight*first+(1-weight)*second
    identity += average*(outcome-average)/2
assert identity==weight*(1-weight)*Fraction(1,4)>0
# Puzzle 3: exact harmonic equations and boundary values for gambler's ruin.
hit=[Fraction(j,100) for j in range(101)]
assert hit[0]==0 and hit[-1]==1
assert all(hit[j]==(hit[j-1]+hit[j+1])/2 for j in range(1,100))
# Sensor non-identifiability: both norm-one parameter points give the same observed mean.
contrast=(1/math.sqrt(2),-1/math.sqrt(2))
assert abs(sum(contrast)) < 1e-15
assert math.isclose(dot(contrast,contrast),1.)
print('PASS: all three puzzle checks and the unidentifiable sensor contrast.')
print('All finite checks passed. These checks complement, rather than replace, the proofs.')
