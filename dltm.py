import math
import random

from networkx import gnp_random_graph, gnm_random_graph, watts_strogatz_graph, barabasi_albert_graph


class DLTM:

    def __init__(self):
        self.agents = {}        # agent_id -> theta
        self.graph = {}         # agent_id_from -> [list of agent_id_to]
        self.infl = {}          # (agent_id_from, agent_id_to) -> influence

        self.ord_to_agent = []  # ordinal (number in [0;n) range) -> agent_id
        self.agent_to_ord = {}  # agent_id -> ordinal

    def put_agent(self, agent_id, theta):
        self.agents[agent_id] = theta
        self.graph[agent_id] = []
        self.ord_to_agent.append(agent_id)
        self.agent_to_ord[agent_id] = len(self.ord_to_agent) - 1

    def put_agents(self, agent_pairs):
        for agent_id, theta in agent_pairs:
            self.put_agent(agent_id, theta)

    def add_edge(self, agent_id_from, agent_id_to, influence):
        if not (agent_id_from in self.agents):
            self.put_agent(agent_id_from, 0)
        self.graph[agent_id_from].append(agent_id_to)
        self.infl[(agent_id_from, agent_id_to)] = influence

    def add_edges(self, edge_trios):
        for agent_id_from, agent_id_to, influence in edge_trios:
            self.add_edge(agent_id_from, agent_id_to, influence)

    # Random DLTM generation

    # 1. Graph generation

    def generate_gnp_random_graph(self, n, p, seed=None):
        graph = gnp_random_graph(n, p, seed=seed, directed=True)
        [self.put_agent(i, 0) for i in range(n)]
        [self.add_edge(a_from, a_to, 0) for a_from, a_to in graph.edges]
        return self

    def generate_gnm_random_graph(self, n, m, seed=None):
        graph = gnm_random_graph(n, m, seed=seed, directed=True)
        [self.put_agent(i, 0) for i in range(n)]
        [self.add_edge(a_from, a_to, 0) for a_from, a_to in graph.edges]
        return self

    def generate_watts_strogatz_graph(self, n, k, p, seed=None):
        graph = watts_strogatz_graph(n, k, p, seed=seed)
        [self.put_agent(i, 0) for i in range(n)]
        [self.add_edge(a_from, a_to, 0) for a_from, a_to in graph.edges]
        [self.add_edge(a_to, a_from, 0) for a_from, a_to in graph.edges]
        return self

    def generate_barabasi_albert_graph(self, n, m, seed=None):
        graph = barabasi_albert_graph(n, m, seed=seed, initial_graph=None)
        [self.put_agent(i, 0) for i in range(n)]
        [self.add_edge(a_from, a_to, 0) for a_from, a_to in graph.edges]
        [self.add_edge(a_to, a_from, 0) for a_from, a_to in graph.edges]
        return self

    # 2. Influence generation

    def generate_influences(self, generator, seed=None):
        random.seed(seed)
        for a_from, a_to in self.infl:
            i = generator(random)
            self.infl[(a_from, a_to)] = i
        return self

    def generate_constant_influences(self, c):
        return self.generate_influences(lambda r: c, None)

    def generate_range_influences(self, i_from, i_to, seed=None):
        return self.generate_influences(lambda r: r.randrange(i_from, i_to + 1), seed)

    # 3. Agents threshold generation

    def generate_proportional_thresholds(self, theta):
        if theta < 0 or theta > 1:
            raise ValueError('theta must be in [0;1] range')

        for a in self.agents.keys():
            self.agents[a] = 0
        for (_, a_to), infl in self.infl.items():
            self.agents[a_to] += infl
        for a, thr in self.agents.items():
            self.agents[a] = math.ceil(thr * theta)
        return self


def read_dltm(path):
    with open(path) as f:
        dltm = DLTM()

        for line in f.readlines():
            sep_pos = line.rfind("#")
            line_content = line if sep_pos == -1 else line[:sep_pos]
            line_args = line_content.split()

            if len(line_args) == 0:
                continue
            if len(line_args) == 1:
                raise ValueError("Too few arguments, expected either agent or edge declaration, got {}".format(line_content))
            else:
                if line_args[0] in ['a', 'A']:
                    if len(line_args) < 3:
                        raise ValueError("Too few arguments at agent declaration. Expected 'a <agent_id> <theta>', got {}".format(line_content))
                    dltm.put_agent(line_args[1], int(line_args[2]))
                else:
                    if line_args[0] in ['i', 'I']:
                        if len(line_args) < 4:
                            raise ValueError("Too few arguments at edge declaration. Expected 'i <agent_from_id> <agent_to_id> <influence>', got {}".format(line_content))
                        dltm.add_edge(line_args[1], line_args[2], int(line_args[3]))
                    else:
                        raise ValueError("Expected either agent declaration ('a agent1 = ...') or edge ('i agent1 agnet2 ...'), got {}".format(line_content))

        return dltm


def write_dltm(dltm, path):
    with open(path, "w") as f:
        for a_id in dltm.agents.keys():
            f.write("a {} {}\n".format(a_id, dltm.agents[a_id]))
        f.write("\n")

        for a_from, a_to in dltm.infl.keys():
            f.write("i {} {} {}\n".format(a_from, a_to, dltm.infl[(a_from, a_to)]))
