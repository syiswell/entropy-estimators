from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from estimators import npeet_entropy, gcmi_entropy, discrete_entropy
from utils.common import set_seed, timer_profile, Timer


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
            Estimated I(X;Y).

        """
        return npeet_entropy(self.x, k=k)

    @timer_profile
    def gcmi(self):
        """
        Gaussian-Copula Mutual Information.

        Returns
        -------
        float
            Estimated I(X;Y).

        """
        return gcmi_entropy(self.x.T)

    def run_all(self):
        estimated = {}
        for estimator in (self.npeet, self.gcmi):
            estimated[estimator.__name__] = estimator()
        if self.verbose:
            for estimator_name, estimator_value in estimated.items():
                print(f"{estimator_name} H(X)={estimator_value:.3f} (true value: {self.entropy_true:.3f})")
        return estimated


def _entropy_normal(n_samples, n_features, param):
    x = np.random.normal(loc=0, scale=param, size=(n_samples, n_features))
    value_true = n_features * np.log2(param * np.sqrt(2 * np.pi * np.e))
    return x, value_true


def _entropy_normal_correlated(n_samples, n_features, param):
    denom = np.arange(1, n_features + 1)
    variance = param ** 2 / denom
    cov = np.zeros((n_features, n_features))
    for row_id in range(n_features):
        cov[row_id, row_id:] = variance[:n_features-row_id]
    cov = (cov + cov.T) / 2
    x = np.random.multivariate_normal(mean=np.repeat(0, n_features), cov=cov, size=n_samples)
    logdet = np.linalg.slogdet(cov)[1] * np.log2(np.e)
    value_true = 0.5 * (n_features * np.log2(2 * np.pi * np.e) + logdet)
    return x, value_true


def _entropy_uniform(n_samples, n_features, param):
    x = np.random.uniform(low=-param / 2, high=param / 2, size=(n_samples, n_features))
    value_true = n_features * np.log2(param)
    return x, value_true


def _entropy_exponential(n_samples, n_features, param):
    # here param is scale (inverse of rate)
    x = np.random.exponential(scale=param, size=(n_samples, n_features))
    value_true = n_features * (1. + np.log(param)) * np.log2(np.e)
    return x, value_true


def _entropy_randint(n_samples, n_features, param):
    x = np.random.randint(low=0, high=param + 1, size=(n_samples, n_features))
    value_true = n_features * np.log2(param)
    return x, value_true


def entropy_test(generator, n_samples=1000, n_features=10, parameters=np.linspace(1, 50, num=10), xlabel=''):
    estimated = defaultdict(list)
    for param in tqdm(parameters, desc="entropy_test"):
        x, true = generator(n_samples, n_features, param)
        estimated_test = EntropyTest(x=x, entropy_true=true, verbose=False).run_all()
        estimated['true'].append(true)
        for estimator_name, estimator_value in estimated_test.items():
            estimated[estimator_name].append(estimator_value)
    value_true = estimated.pop('true')
    for estimator_name, estimator_value in estimated.items():
        plt.plot(parameters, estimator_value, label=estimator_name)
    plt.plot(parameters, value_true, label='true', ls='--')
    plt.xlabel(xlabel)
    plt.ylabel('Estimated entropy, bits')
    plt.title(generator.__name__)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    set_seed(26)
    entropy_test(_entropy_randint, n_samples=2000, n_features=11, parameters=np.arange(1, 10), xlabel='Width')
    entropy_test(_entropy_normal_correlated, n_features=100, xlabel='Sigma')
    # entropy_test(_entropy_normal, n_features=90, xlabel='Sigma (scale)')
    entropy_test(_entropy_uniform, n_features=100, xlabel='Uniform width')
    entropy_test(_entropy_exponential, n_features=100, xlabel='Scale (inverse rate)')
    Timer.checkpoint()
