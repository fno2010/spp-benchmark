#!/usr/bin/env python3

import os
import pickle

import matplotlib.pyplot as plt

plt.rcParams['text.usetex'] = True

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
    fig, ax = plt.subplots(figsize=(8, 5))

    g_succ = []
    g_fail = []
    gp_succ = []
    gp_fail = []
    gpp_succ = []
    gpp_fail = []
    for r in results:
        pn = r['s-graph']['permitted-path-num']
        # pn = r['nodes']
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
            gpp_succ.append((pn, solver['greedy++']['time']))
            # gpp_fail.append((pn, solver['greedy++']['time']))

    g_succ_pn = [v[0] for v in g_succ]
    g_succ_t = [v[1] for v in g_succ]
    ax.scatter(g_succ_pn, g_succ_t, c='red', marker='o', label='Greedy succeed')

    g_fail_pn = [v[0] for v in g_fail]
    g_fail_t = [v[1] for v in g_fail]
    ax.scatter(g_fail_pn, g_fail_t, c='red', marker='x', label='Greedy failed')

    gp_succ_pn = [v[0] for v in gp_succ]
    gp_succ_t = [v[1] for v in gp_succ]
    ax.scatter(gp_succ_pn, gp_succ_t, c='green', marker='o', label='Greedy+ succeed')

    gp_fail_pn = [v[0] for v in gp_fail]
    gp_fail_t = [v[1] for v in gp_fail]
    ax.scatter(gp_fail_pn, gp_fail_t, c='green', marker='x', label='Greedy+ failed')

    gpp_succ_pn = [v[0] for v in gpp_succ]
    gpp_succ_t = [v[1] for v in gpp_succ]
    ax.scatter(gpp_succ_pn, gpp_succ_t, c='blue', marker='o', label='GreedyMIS succeed')

    gpp_fail_pn = [v[0] for v in gpp_fail]
    gpp_fail_t = [v[1] for v in gpp_fail]
    ax.scatter(gpp_fail_pn, gpp_fail_t, c='blue', marker='x', label='GreedyMIS failed')

    ax.set_xlabel('Number of Permitted Paths', fontsize=16)
    # plt.xlabel('Number of ASes')
    ax.set_ylabel('Time (s)', fontsize=16)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_ylim([1e-5, 10**2])
    ax.legend(fontsize=16)
    plt.tight_layout()

    plt.savefig('solver-time.pdf')
    # plt.savefig('solver-asn-time.eps')

def plot_topo_dist(results):
    nodes = [r['nodes'] for r in results]
    paths = [r['s-graph']['permitted-path-num'] for r in results]
    fig, ax = plt.subplots(figsize=(8, 5))
    _, _, ln1 = ax.hist(nodes, 50, density=True, histtype='step', cumulative=True, color='red', label='\# of ASes')
    ax.set_xlabel('Number of ASes', fontsize=16)
    ax.set_ylabel('CDF', fontsize=16)
    ax.set_ylim((0, 1))
    ax.set_xlim((0, max(nodes)))

    ax2 = ax.twiny()
    _, _, ln2 = ax2.hist(paths, 10000, density=True, histtype='step', cumulative=True, color='blue', label='\# of Permitted Paths')
    ax2.set_xscale('log')
    ax2.set_xlabel('Number of Permitted Paths', fontsize=16)
    ax2.set_xlim((1, max(paths)))

    lns = ln1 + ln2
    lbs = [l.get_label() for l in lns]
    ax.legend(lns, lbs, loc=2, fontsize=16)

    plt.tight_layout()

    plt.savefig('asnum-permitted-paths-cdf.pdf')

def plot_sgraph_dist(results):
    nodes = [r['s-graph']['permitted-path-num'] for r in results]
    fig, ax = plt.subplots()
    ax.hist(nodes, 50, density=True, histtype='step', cumulative=True)
    ax.set_xscale('log')
    ax.set_xlabel('Number of Permitted Paths')
    ax.set_ylabel('CDF')
    plt.tight_layout()

    plt.savefig('permitted-path-cdf.pdf')

if __name__ == '__main__':
    import sys
    results = load_result(sys.argv[1])
    results = prune_trival_result(results)
    plot_result(results)
    plot_topo_dist(results)
    # plot_sgraph_dist(results)
