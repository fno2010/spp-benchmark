#!/usr/bin/env python3

import os
import random
import pickle

from spp_benchmark.reader import TopologyReader, set_dst
from spp_benchmark.pcgraph import PCGraph, GreedySolver, GreedyPlusSolver, GreedyPPGraphSolver
from spp_benchmark.bgp import bgp_sim

def test_country(topo, cc, solvers, dst=None, save_dir=None):
    result = dict()
    dst = dst or random.choice(list(topo.nodes()))
    set_dst(topo, dst)
    print('[[[ Country: %s, ASes: %d, Edges: %d, Dest: %d ]]]' % (cc, len(topo.nodes), len(topo.edges), dst))
    result['country'] = cc
    result['nodes'] = len(topo.nodes)
    result['edges'] = len(topo.edges)
    succ = bgp_sim(topo, iter_num=50, anno_num=5000)
    if succ:
        pcg = PCGraph()
        pcg.load(topo)
        pcg.build()
        print('[[ SolverGraph: (Paths: %d, Edges: %d) ]]' % (len(pcg.nodes), len(pcg.edges)))
        result['s-graph'] = dict()
        result['s-graph']['permitted-path-num'] = len(pcg.nodes)
        result['s-graph']['edges'] = len(pcg.edges)
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


if __name__ == '__main__':
    import sys
    topo_reader = TopologyReader()
    as_rel_f = sys.argv[1]
    as_country_f = sys.argv[2]
    topo_reader.read_topo(as_rel_f, as_country_file=as_country_f)

    gsolver = GreedySolver()
    gpsolver = GreedyPlusSolver()
    gppsolver = GreedyPPGraphSolver()
    solvers = {
        'Greedy': gsolver,
        'Greedy+': gpsolver,
        'Greedy++': gppsolver
    }

    if len(sys.argv) > 3:
        cc = sys.argv[3]
        topo = topo_reader.get_subtopo_by_country(cc, maximum=True)
        dst = None
        if len(sys.argv) > 4:
            dst = int(sys.argv[4])
        if len(topo):
            test_country(topo, cc, solvers, dst=dst)
    else:
        countries = [cc for cc, al in reversed(topo_reader.country_stat()) if 5 < al < 50]
        for cc in countries:
            topo = topo_reader.get_subtopo_by_country(cc, maximum=True)
            if len(topo):
                test_country(topo, cc, solvers, save_dir='pickle')
