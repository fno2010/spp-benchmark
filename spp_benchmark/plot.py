#!/usr/bin/env python3

import os
import pickle

def load_result(dirname):
    results = []
    for fname in os.listdir(dirname):
        with open(os.path.join(dirname, fname), 'rb') as fd:
            result = pickle.load(fd)
            results.append(result)
    return results

def prune_trival_result(results):
    return [r for r in results if r['s-graph']['edges'] > 0]

def topo_dist(results):
    nodes_dist = dict()
    for r in results:
        node_num = r['nodes']
        nodes_dist[node_num] = nodes_dist.get(node_num, 0) + 1
    return nodes_dist

def plot_result(results):
    import matplotlib.pyplot as plt
    g_succ = []
    g_fail = []
    gp_succ = []
    gp_fail = []
    gpp_succ = []
    gpp_fail = []
    for r in results:
        pn = r['s-graph']['permitted-path-num']
        solver = r['solver']
        if solver['greedy']['status'] == 'SUCCESS':
            g_succ.append((pn, solver['greedy']['time']))
        else:
            g_fail.append((pn, solver['greedy']['time']))
        if solver['greedy+']['status'] == 'SUCCESS':
            gp_succ.append((pn, solver['greedy+']['time']))
        else:
            gp_fail.append((pn, solver['greedy+']['time']))
        if solver['greedy++']['status'] == 'SUCCESS':
            gpp_succ.append((pn, solver['greedy++']['time']))
        else:
            gpp_fail.append((pn, solver['greedy++']['time']))

    g_succ_pn = [v[0] for v in g_succ]
    g_succ_t = [v[1] for v in g_succ]
    plt.scatter(g_succ_pn, g_succ_t, c='red', marker='o', label='greedy succeed')

    g_fail_pn = [v[0] for v in g_fail]
    g_fail_t = [v[1] for v in g_fail]
    plt.scatter(g_fail_pn, g_fail_t, c='red', marker='x', label='greedy failed')

    gp_succ_pn = [v[0] for v in gp_succ]
    gp_succ_t = [v[1] for v in gp_succ]
    plt.scatter(gp_succ_pn, gp_succ_t, c='green', marker='o', label='greedy+ succeed')

    gp_fail_pn = [v[0] for v in gp_fail]
    gp_fail_t = [v[1] for v in gp_fail]
    plt.scatter(gp_fail_pn, gp_fail_t, c='green', marker='x', label='greedy+ failed')

    gpp_succ_pn = [v[0] for v in gpp_succ]
    gpp_succ_t = [v[1] for v in gpp_succ]
    plt.scatter(gpp_succ_pn, gpp_succ_t, c='blue', marker='o', label='greedy++ succeed')

    gpp_fail_pn = [v[0] for v in gpp_fail]
    gpp_fail_t = [v[1] for v in gpp_fail]
    plt.scatter(gpp_fail_pn, gpp_fail_t, c='blue', marker='x', label='greedy++ failed')

    plt.xlabel('Number of Permitted Paths')
    plt.ylabel('Time (s)')
    plt.xscale('log')
    plt.yscale('log')
    plt.legend()
    plt.tight_layout()

    plt.savefig('solver-time.eps')

if __name__ == '__main__':
    import sys
    results = load_result(sys.argv[1])
    results = prune_trival_result(results)
    plot_result(results)
