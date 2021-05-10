#!/usr/bin/env python3

import os
import random
import pickle
import argparse

from spp_benchmark.reader import TopologyReader, set_dst
from spp_benchmark.sgraph import SGraph, GreedySolver, GreedyPlusSolver, GreedyPPGraphSolver
from spp_benchmark.bgp import bgp_sim

def test_country(topo, cc, solvers, dst=None, save_dir=None):
    """
    Test each solver in `solvers` to solve a SPP instance.

    topo: Internet AS-level topology
    cc: countrycode to filter a subgraph of the Internet
    solvers: dist (solver name -> solver instance)
    dst: destination AS number
    save_dir: directory to dump test result
    """
    result = dict()
    dst = dst or random.choice(list(topo.nodes()))
    set_dst(topo, dst)
    print('[[[ Country: %s, ASes: %d, Edges: %d, Dest: %d ]]]' % (cc, len(topo.nodes), len(topo.edges), dst))
    result['country'] = cc
    result['nodes'] = len(topo.nodes)
    result['edges'] = len(topo.edges)
    succ = bgp_sim(topo, anno_num=5000)
    if succ:
        pcg = SGraph()
        pcg.load(topo)
        pcg.build()
        print('[[ SolverGraph: (Paths: %d, Edges: %d) ]]' % (len(pcg.nodes), len(pcg.edges)))
        result['s-graph'] = dict()
        result['s-graph']['permitted-path-num'] = len(pcg.nodes)
        result['s-graph']['edges'] = len(pcg.edges)
        result['s-graph']['edges-0'] = len([e for e in pcg.edges if pcg.edges[e]['type'] == 0])
        result['s-graph']['edges-1'] = len([e for e in pcg.edges if pcg.edges[e]['type'] == 1])
        result['s-graph']['edges-2'] = len([e for e in pcg.edges if pcg.edges[e]['type'] == 2])
        result['solver'] = dict()
        for solver in solvers:
            s, succ, t = solvers[solver].solve(pcg, enable_timer=True)
            result['solver'][solver.lower()] = dict()
            result['solver'][solver.lower()]['status'] = 'SUCCESS' if succ else 'FAILED'
            result['solver'][solver.lower()]['time'] = t
            result['solver'][solver.lower()]['solution'] = s
            print('%s [%s in %fs]:' % (solver, ('SUCCESS' if succ else 'FAILED'), t), s)
        if save_dir is not None:
            with open(os.path.join(save_dir, '%s-%d.pickle' % (cc, dst)), 'wb') as save_f:
                pickle.dump(result, save_f)
    print()

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--as-rel', required=True)
    parser.add_argument('--as-country', required=True)
    parser.add_argument('--save-dir', required=True)
    parser.add_argument('--country', default=None)
    parser.add_argument('--dst', default=None)
    parser.add_argument('--as-num-lb', type=int, default=10)
    parser.add_argument('--as-num-ub', type=int, default=50)
    return parser.parse_args()


if __name__ == '__main__':
    import sys
    topo_reader = TopologyReader()
    args = getArgs()
    # as_rel_f = sys.argv[1]
    # if args.as_country:
        # as_country_f = sys.argv[2]
    topo_reader.read_topo(args.as_rel, as_country_file=args.as_country)
    # else:
    #     topo_reader.read_topo(as_rel_f)

    gsolver = GreedySolver()
    gpsolver = GreedyPlusSolver()
    gppsolver = GreedyPPGraphSolver()
    solvers = {
        'Greedy': gsolver,
        'Greedy+': gpsolver,
        'Greedy++': gppsolver
    }

    if args.country:
        cc = args.country
        topo = topo_reader.get_subtopo_by_country(cc, maximum=True)
        dst = None
        if len(sys.argv) > 4:
            dst = int(sys.argv[4])
        if len(topo):
            test_country(topo, cc, solvers, dst=dst, save_dir=args.save_dir)
    else:
        countries = [cc for cc, al in reversed(topo_reader.country_stat()) if args.as_num_lb <= al < args.as_num_ub]
        for cc in countries:
            topo = topo_reader.get_subtopo_by_country(cc, maximum=True)
            if len(topo):
                test_country(topo, cc, solvers, save_dir=args.save_dir)
    # else:
    #     degs = sorted(list(topo_reader.dg.degree()), key=lambda d: d[1], reverse=True)[:20]
    #     dst = degs[0][0]
    #     rounds = lambda n, N: (n*(N-1)*15 + (n*(n+N)+N)*5 + n*(4*n+3*N*n+3*N*N+2*N))
    #     for _, d in degs[5:]:
    #         topo = topo_reader.get_subtopo_by_degree(d//2, maximum=True)
    #         set_dst(topo, dst)
    #         bgp_sim(topo, anno_num=5000)
    #         n, N = len(topo), sum([len(topo.nodes[n]['as'].permitted_paths()) for n in topo.nodes()])
    #         n = n - 1
    #         print(n, N, rounds(n, N))
