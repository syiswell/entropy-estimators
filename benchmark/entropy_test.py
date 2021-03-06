from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from estimators import npeet_entropy, gcmi_entropy
from utils.algebra import entropy_normal_theoretic
from utils.common import set_seed, timer_profile, Timer
from utils.constants import IMAGES_DIR, TIMINGS_DIR


class EntropyTest:

    def __init__(self, x, entropy_true, verbose=True):
        if x.ndim == 1:
            x = np.expand_dims(x, axis=1)
        self.x = x
        self.entropy_true = entropy_true
        self.verbose = verbose

    @timer_profile
    def npeet(self, k=3):
        """
        Non-parametric Entropy Estimation Toolbox.

        Parameters
        ----------
        k : int
            No. of nearest neighbors.
            See https://github.com/gregversteeg/NPEET/blob/master/npeet_doc.pdf.

        Returns
        -------
        float
            Estimated Entropy H(X).

        """
        return npeet_entropy(self.x, k=k)

    @timer_profile
    def gcmi(self):
        """
        Gaussian-Copula Mutual Information.

        Returns
        -------
        float
            Estimated Entropy H(X).

        """
        return gcmi_entropy(self.x.T)

    def run_all(self):
        estimated = {}
        for estimator in (self.npeet, self.gcmi):
            try:
                estimated[estimator.__name__] = estimator()
            except Exception:
                estimated[estimator.__name__] = np.nan
        if self.verbose:
            for estimator_name, estimator_value in estimated.items():
                print(f"{estimator_name} H(X)={estimator_value:.3f} (true value: {self.entropy_true:.3f})")
        return estimated


def generate_normal_correlated(n_samples, n_features, sigma, loc=None):
    cov = np.random.uniform(low=0, high=sigma, size=(n_features, n_features))
    cov = cov.dot(cov.T)  # make cov positive definite
    if loc is None:
        loc = np.repeat(0, n_features)
    x = np.random.multivariate_normal(mean=loc, cov=cov, size=n_samples)
    entropy_true = entropy_normal_theoretic(cov)
    return x, entropy_true, cov


def _entropy_normal_correlated(n_samples, n_features, param):
    x, entropy_true, cov = generate_normal_correlated(n_samples, n_features, param)
    return x, entropy_true


def _entropy_uniform(n_samples, n_features, param):
    x = np.random.uniform(low=0, high=param, size=(n_samples, n_features))
    entropy_true = n_features * np.log2(param)
    return x, entropy_true


def _entropy_exponential(n_samples, n_features, param):
    # here param is scale (inverse of rate)
    x = np.random.exponential(scale=param, size=(n_samples, n_features))
    entropy_true = n_features * (1. + np.log(param)) * np.log2(np.e)
    return x, entropy_true


def _entropy_randint(n_samples, n_features, param):
    x = np.random.randint(low=0, high=param + 1, size=(n_samples, n_features))
    entropy_true = n_features * np.log2(param)
    return x, entropy_true


def entropy_test(generator, n_samples=1000, n_features=10, parameters=np.linspace(1, 50, num=10), xlabel=''):
    estimated = defaultdict(list)
    for param in tqdm(parameters, desc=f"{generator.__name__} test"):
        x, entropy_true = generator(n_samples, n_features, param)
        estimated_test = EntropyTest(x=x, entropy_true=entropy_true, verbose=False).run_all()
        estimated['true'].append(entropy_true)
        for estimator_name, estimator_value in estimated_test.items():
            estimated[estimator_name].append(estimator_value)
    entropy_true = estimated.pop('true')
    plt.figure()
    plt.plot(parameters, entropy_true, label='true', ls='--', marker='x')
    for estimator_name, estimator_value in estimated.items():
        plt.plot(parameters, estimator_value, label=estimator_name)
    plt.xlabel(xlabel)
    plt.ylabel('Estimated entropy, bits')
    plt.title(f"{generator.__name__.lstrip('_')}: len(X)={n_samples}, dim(X)={n_features}")
    plt.legend()
    plt.savefig(IMAGES_DIR / f"{generator.__name__}.png")
    # plt.show()


def entropy_all_tests(n_samples=10_000, n_features=10):
    set_seed(26)
    entropy_test(_entropy_randint, n_samples=n_samples, n_features=n_features, xlabel=r'$X \sim $Randint$(0, x)$')
    entropy_test(_entropy_normal_correlated, n_samples=n_samples, n_features=n_features,
                 xlabel=r'$X \sim \mathcal{N}(0, \Sigma^\top \Sigma), \Sigma_{ij} \sim $Uniform$(0, x)$')
    entropy_test(_entropy_uniform, n_samples=n_samples, n_features=n_features, xlabel=r'$X \sim $Uniform$(0, x)$')
    entropy_test(_entropy_exponential, n_samples=n_samples, n_features=n_features, xlabel=r'$X \sim $Exp(scale=x)')
    Timer.checkpoint(fpath=TIMINGS_DIR / "entropy.txt")


if __name__ == '__main__':
    entropy_all_tests()
