import random
from copy import copy

import genetic


class TSSProblem:

    def __init__(self, dltm, threshold):
        self.dltm = dltm
        self.threshold = threshold

    def fit(self, vec):
        n = len(vec)
        if n != len(self.dltm.ord_to_agent):
            raise ValueError('vector length ({}) != agents number ({})'.format(n, len(self.dltm.ord_to_agent)))

        start_vec = [1 if a else 0 for a in vec]
        cur_vec = copy(start_vec)
        cur_infl = [0 for _ in range(n)]
        cur_indices = []
        for i in range(n):
            if cur_vec[i]:
                cur_indices.append(i)

        while wt(cur_vec) < self.threshold:
            new_indices = []
            for i in cur_indices:
                agent = self.dltm.ord_to_agent[i]
                for agent_to in self.dltm.graph[agent]:
                    i_to = self.dltm.agent_to_ord[agent_to]
                    cur_infl[i_to] += self.dltm.infl[(agent, agent_to)]
                    if not cur_vec[i_to] and cur_infl[i_to] >= self.dltm.agents[agent_to]:
                        new_indices.append(self.dltm.agent_to_ord[agent_to])
                        cur_vec[i_to] = 1

            if len(new_indices) == 0:
                break
            cur_indices = list(new_indices)

        return wt(start_vec) if wt(cur_vec) >= self.threshold else n + 1

    def solve_abstract(self, solver, seed=None):
        random.seed(seed)

        solution_vec = solver()
        solution = []
        for i in range(len(solution_vec)):
            if solution_vec[i]:
                solution.append(self.dltm.ord_to_agent[i])
        return solution

    def solve_using_1p1(self, iterations, seed=None):
        return self.solve_abstract(lambda: genetic.using_1p1(
            [1] * len(self.dltm.agents), self.fit, genetic.default_mutation, iterations
        ), seed)

    def solve_using_1cl(self, lmbd, iterations, seed=None):
        return self.solve_abstract(lambda: genetic.using_1cl(
            [1] * len(self.dltm.agents), self.fit, genetic.default_mutation, lmbd, iterations
        ), seed)

    def solve_using_custom_ga(self, l, h, g, iterations, seed=None):
        return self.solve_abstract(lambda: genetic.using_custom_ga(
            [1] * len(self.dltm.agents), self.fit, genetic.default_mutation, genetic.two_point_crossover, l, h, g, iterations
        ), seed)


def wt(vec):
    return sum(vec)
