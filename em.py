"""
em.py — Algoritmo EM (Expectation-Maximization) para mistura de gaussianas 1D,
seguindo o pseudocódigo da Listagem 3 do enunciado.

A variável oculta Z indica de qual componente (perfil) cada exemplo veio.
"""
import numpy as np


class MisturaGaussianaEM:
    def __init__(self, K=2, max_iter=200, tol=1e-4, seed=42, var_min=0.05):
        # tol é RELATIVO: para quando |ΔL| < tol * |L|
        # var_min: piso da variância. Sem ele, uma componente pode "colapsar" sobre um único
        # valor repetido (ex.: muitos municípios com taxa zero) e a verossimilhança vai ao infinito.
        self.var_min = var_min
        self.K = K
        self.max_iter = max_iter
        self.tol = tol
        self.seed = seed

    @staticmethod
    def _normal(x, mu, var):
        return np.exp(-0.5 * (x - mu) ** 2 / var) / np.sqrt(2 * np.pi * var)

    def _densidades(self, x):
        # matriz N x K com theta_k * N(x | mu_k, sigma_k^2)
        return np.column_stack([self.theta[k] * self._normal(x, self.mu[k], self.var[k])
                                for k in range(self.K)])

    def fit(self, x):
        x = np.asarray(x, dtype=float)
        N = len(x)
        rng = np.random.default_rng(self.seed)
        # Inicialização: médias em quantis distintos, variância global, pesos iguais
        self.mu = np.quantile(x, np.linspace(0.2, 0.8, self.K)) + rng.normal(0, 1e-3, self.K)
        self.var = np.full(self.K, x.var())
        self.theta = np.full(self.K, 1.0 / self.K)
        self.log_verossimilhanca = []

        for it in range(self.max_iter):
            # E-step: responsabilidades r[n, k] = P(Z=k | x_n)
            dens = self._densidades(x)
            total = dens.sum(axis=1, keepdims=True) + 1e-300
            r = dens / total

            # Log-verossimilhança com os parâmetros atuais
            ll = float(np.log(total).sum())
            self.log_verossimilhanca.append(ll)

            # M-step
            Nk = r.sum(axis=0)
            self.theta = Nk / N
            self.mu = (r * x[:, None]).sum(axis=0) / Nk
            self.var = np.maximum((r * (x[:, None] - self.mu) ** 2).sum(axis=0) / Nk, self.var_min)

            # Convergência
            if it > 0 and abs(ll - self.log_verossimilhanca[-2]) < self.tol * abs(ll):
                break

        # Ordena componentes pela média (componente 0 = menor média)
        ordem = np.argsort(self.mu)
        self.mu, self.var, self.theta = self.mu[ordem], self.var[ordem], self.theta[ordem]
        self.n_iter = len(self.log_verossimilhanca)
        return self

    def responsabilidades(self, x):
        x = np.asarray(x, dtype=float)
        dens = self._densidades(x)
        return dens / (dens.sum(axis=1, keepdims=True) + 1e-300)

    def predizer(self, x):
        return self.responsabilidades(x).argmax(axis=1)
