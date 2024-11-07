#  Based on Liu & Terzi's k-degree anonymity:
# [1] https://dl.acm.org/doi/10.1145/1376616.1376629

import networkx as nx
import numpy as np
import random as rn

def sort_dv(dv):
    dv.sort(reverse=True)
    # permutation holds the mapping between original vertex and degree-sorted vertices
    degree_sequence, permutation = zip(*dv)
    degree_sequence = np.array(degree_sequence)
    return degree_sequence, permutation


# "degree anonymization cost" as defined in Section 4 of [1]
# 计算i-j个节点增加到第一个节点的度数需要边的花费，第一个节点度数是最大的
def assignment_cost_additions_only(degree_sequence):
    return np.sum(degree_sequence[0] - degree_sequence)


# median of a sorted array
def median(degree_sequence):
    n = len(degree_sequence)
    return degree_sequence[n // 2] if n % 2 else (degree_sequence[n // 2 - 1] + degree_sequence[n // 2]) // 2


# "degree anonymization cost" as defined in Section 8 of [1]
# 这个条件下可以删除和添加边，先求出中位数，然后多的删除边，少的添加边，计算花费的代价
def assignment_cost_additions_deletions(degree_sequence):
    md = median(degree_sequence)
    return np.sum(np.abs(md - degree_sequence))


# Precomputation of the anonymisation cost, as described in Section 4 of [1]
def anonymisation_cost_precomputation(degree_sequence, k, with_deletions):
    n = np.size(degree_sequence)
    # C[i, j]表示将度序列从第 i 个节点到第 j 个节点之间的序列调整到满足k-匿名性的最小成本。
    # 具体来说，C[i, j]存储了将子序列 degree_sequence[i,j] 调整到满足 k-匿名性的总成本。
    # 递推公式 C[i, j] = C[i, j - 1] + (i,j)节点匿名的成本
    C = np.full([n, n], np.inf)
    for i in range(n - 1):
        # j从 i+k-1是确保子序列至少i+k-1个节点才能组成k匿名
        for j in range(i + k - 1, np.min([i + 2 * k, n])):
            if with_deletions:
                if C[i, j - 1] == np.inf:
                    C[i, j] = assignment_cost_additions_deletions(degree_sequence[i:j + 1])
                else:
                    C[i, j] = C[i, j - 1] + median(degree_sequence[i:j + 1]) - degree_sequence[j]
            else:
                if C[i, j - 1] == np.inf:
                    C[i, j] = assignment_cost_additions_only(degree_sequence[i:j + 1])
                else:
                    C[i, j] = C[i, j - 1] + degree_sequence[i] - degree_sequence[j]
    return C


# The dynamic programming algorithm described in Section 4 of [1]
def dp_degree_anonymiser(degree_sequence, k, with_deletions=False):
    C = anonymisation_cost_precomputation(degree_sequence, k, with_deletions)
    n = np.size(degree_sequence)
    Da = np.full(n, np.inf)
    sequences = [None] * n
    cost, anonymised_sequence = dp_degree_anonymiser_recursion(degree_sequence, k, C, n, Da, sequences, with_deletions)
    return anonymised_sequence


# The dynamic programming algorithm described in Section 4 of [1] - recursion part
def dp_degree_anonymiser_recursion(degree_sequence, k, C, n, Da, sequences, with_deletions):
    group_degree = None
    if with_deletions:
        group_degree = median(degree_sequence)
    else:
        group_degree = degree_sequence[0]
    all_in_one_group_sequence = np.full(n, group_degree)
    all_in_one_group_cost = C[0, n - 1]

    if n < 2 * k:
        return all_in_one_group_cost, all_in_one_group_sequence
    else:

        min_cost = np.inf
        min_cost_sequence = np.empty(0)
        # number of recursions optimised according to Eq. 4 in [1]
        # originally: range(k-1,n-k)
        for t in range(np.max([k - 1, n - 2 * k]), n - k):
            # this IF-ELSE is to avoid recomputing cost and sequence for the same value of t more than once
            if Da[t] == np.inf:
                cost, sequence = dp_degree_anonymiser_recursion(degree_sequence[0:t + 1], k, C, t + 1, Da, sequences,
                                                                with_deletions)
                Da[t] = cost
                sequences[t] = sequence
            else:
                cost = Da[t]
                sequence = sequences[t]
            cost = cost + C[t + 1, n - 1]
            if cost < min_cost:
                min_cost = cost
                if with_deletions:
                    min_cost_sequence = np.concatenate(
                        (sequence, np.full(np.size(degree_sequence[t + 1:]), median(degree_sequence[t + 1:]))))
                else:
                    min_cost_sequence = np.concatenate(
                        (sequence, np.full(np.size(degree_sequence[t + 1:]), degree_sequence[t + 1])))
        to_return = (min_cost, min_cost_sequence) if min_cost < all_in_one_group_cost else (
        all_in_one_group_cost, all_in_one_group_sequence)
        return to_return


# Section 6.2 in [1]
# 输入(度序列，原始图)
def priority(degree_sequence, original_G):
    n = len(degree_sequence)
    # 如果度序列的总数是奇数，那么该序列不可实现
    # if the sum of the degree sequence is odd, the degree sequence isn't realisable
    if np.sum(degree_sequence) % 2 != 0:
        return None

    G = nx.empty_graph(n)  # 创建一个空图G
    # transform list of degrees in list of (vertex, degree)
    vd = [(v, d) for v, d in enumerate(degree_sequence)]  # 返回枚举对象，v为序，d为度

    while True:

        # sort the list of pairs by degree (second element in the pair)
        # 按照度的大小排列vd
        vd.sort(key=lambda tup: tup[1], reverse=True)
        # 如果我们以一个负度为介数，那么度序列不可实现
        # if we ended up with a negative degree, the degree sequence isn't realisable

        if vd[-1][1] < 0:
            return None
        # tot_degree 计算总的度数
        tot_degree = 0
        for vertex in vd:  # 对序列的每个元组进行遍历
            tot_degree = tot_degree + vertex[1]  # 取元组的第二项（即度的大小）求出总的度
        # if all the edges required by the degree sequence have been added, G has been created
        # 当在度序列里的所有边都已经被添加，图G已经创建好了
        # 如果总度数==0，返回图G
        if tot_degree == 0:
            return G

        # gather all the vertices that need more edges
        # 收集所有需要更多边的顶点
        # 取出vd里面所有度大于0的点
        remaining_vertices = [i for i, vertex in enumerate(vd) if vertex[1] > 0]
        # pick a random one
        # 随机取出其中的一个点
        idx = remaining_vertices[rn.randrange(len(remaining_vertices))]
        # 此处v代表该点在vd中的序号
        v = vd[idx][0]
        # 遍历所有图里面的边，取出他们的soure和target作为u和v
        # iterate over all the degree-sorted vertices u such that (u,v) is an edge in the original graph
        for i, u in enumerate(vd):
            # 当我们已经添加了一条边，则循环停止
            # stop when we added v_d edges
            # 如果该点的度为0，则跳出循环
            if vd[idx][1] == 0:
                break
            # 此处防止添加source和target一样的点
            # don't add self-loops
            if u[0] == v:  # 如果遍历到和v一样的点，则continue
                continue
            # 确保我们不会添加两条相同的边
            # make sure we're not adding the same edge twice..
            if G.has_edge(u[0], v):
                continue
            # 如果原始图里存在该条边，并且该点在vd的度大于0，则添加该条边
            # add the edge if this exists also in the original graph
            if original_G.has_edge(v, u[0]) and u[1] > 0:
                G.add_edge(v, u[0])
                # decrease the degree of the connected vertex
                # 减少target和source的度
                vd[i] = (u[0], u[1] - 1)
                # keep track of how many edges we added
                # 刷新vd里的值
                vd[idx] = (v, vd[idx][1] - 1)

        # iterate over all the degree-sorted vertices u such that (u,v) is NOT an edge in the original graph
        # 遍历所有在度序列里的、但是不在原始图的点
        for i, u in enumerate(vd):
            # stop when we added v_d edges
            # 当我们已经添加了一条边时跳出循环
            if vd[idx][1] == 0:
                break
            # 不要添加自我连通的边
            # don't add self-loops
            if u[0] == v:
                continue
            # 保证不会添加两条相同的边
            # make sure we're not adding the same edge twice..
            if G.has_edge(v, u[0]):
                continue
            # 现在添加不在原始图中的边
            # now add edges that are not in the original graph
            if not original_G.has_edge(v, u[0]):
                G.add_edge(v, u[0])
                # decrease the degree of the connected vertex
                vd[i] = (u[0], u[1] - 1)
                # keep track of how many edges we added
                vd[idx] = (v, vd[idx][1] - 1)

# 度数最低的noise节点度数+1
def probing(dv, noise):
    # increase only the degree of the lowest degree nodes, as suggested in the paper
    n = len(dv)
    for v in range(-noise, 0):
        dv[v] = (np.min([dv[v][0] + 1, n - 1]), dv[v][1])
    return dv


# Anonymise G given a value of k using DP degree anonymiser, PRIORITY, and PROBING (edge removals: optional)
def graph_anonymiser(G, k, noise=10, with_deletions=False):
    dv = [(d, v) for v, d in G.degree()]
    degree_sequence, permutation = sort_dv(dv)

    attempt = 1
    print("Attempt number", attempt)
    # 获得调整代价最小的度序列
    anonymised_sequence = dp_degree_anonymiser(degree_sequence, k, with_deletions=with_deletions)
    # 将匿名化后的度序列中的每个值放回对应原始节点的位置
    new_anonymised_sequence = [None] * len(degree_sequence)
    for i in range(len(permutation)):
        new_anonymised_sequence[permutation[i]] = anonymised_sequence[i]
    anonymised_sequence = new_anonymised_sequence
    # 获得了最佳的度序列，根据优先级进行图的动态调整
    Ga = priority(anonymised_sequence, G)

    while Ga is None:
        attempt = attempt + 1
        print("Attempt number", attempt)

        dv = probing(dv, noise)
        degree_sequence, permutation = sort_dv(dv)

        anonymised_sequence = dp_degree_anonymiser(degree_sequence, k, with_deletions=with_deletions)

        new_anonymised_sequence = [None] * len(degree_sequence)
        for i in range(len(permutation)):
            new_anonymised_sequence[permutation[i]] = anonymised_sequence[i]
        anonymised_sequence = new_anonymised_sequence
        # 判断一个给定的度序列是否可以构成一个简单无向图
        if not nx.is_valid_degree_sequence_erdos_gallai(anonymised_sequence):
            continue
        Ga = priority(anonymised_sequence, G)
        if Ga is None:
            print("the sequence is valid but the graph construction failed")
    return Ga


def generate_non_k_anonymous_graph(num_nodes=100, k=3):
    while True:
        # 使用Erdős-Rényi模型生成随机图
        G = nx.erdos_renyi_graph(num_nodes, p=0.05)
        # 检查是否满足k-匿名性
        degree_count = {}
        for node, degree in G.degree():
            if degree in degree_count:
                degree_count[degree] += 1
            else:
                degree_count[degree] = 1

        # 如果存在任何一个度数出现次数小于k，则图不满足k-匿名性
        if any(count < k for count in degree_count.values()):
            return G

def print_G(G):
    print("Graph - Nodes:", G.nodes(), "Edges:", G.edges())
    degree_sequence = [d for n, d in G.degree()]
    print("Degree sequence of the original graph:", degree_sequence)


if __name__ == '__main__':
    # # 创建一个简单的非 k-匿名图
    # G = nx.Graph()
    # # 添加边以形成一个非 k-匿名的度序列
    # edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (0, 2)]
    # G.add_edges_from(edges)
    #
    # # 打印原始图的信息
    # print("Original Graph - Nodes:", G.nodes(), "Edges:", G.edges())
    # degree_sequence = [d for n, d in G.degree()]
    # print("Degree sequence of the original graph:", degree_sequence)
    #
    # # 设置匿名参数 k 和噪声参数 noise
    # k = 3  # 我们设置 k 为 3，因为原始图中没有三个或更多节点有相同的度
    # noise = 1
    #
    # # 调用匿名化函数
    # Ga = graph_anonymiser(G, k, noise, with_deletions=False)
    #
    # # 如果成功返回了匿名化的图，则打印其信息
    # if Ga is not None:
    #     print("Anonymized Graph - Nodes:", Ga.nodes(), "Edges:", Ga.edges())
    #     anonymized_degree_sequence = [d for n, d in Ga.degree()]
    #     print("Degree sequence of the anonymized graph:", anonymized_degree_sequence)
    # else:
    #     print("Failed to create an anonymized graph.")

    G = generate_non_k_anonymous_graph()
    print("原始图：")
    print_G(G)
    k = 3
    noise = 10
    Ga = graph_anonymiser(G, k, noise, with_deletions=True)
    print("匿名图：")
    print_G(Ga)











