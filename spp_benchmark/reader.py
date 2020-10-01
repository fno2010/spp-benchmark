#!/usr/bin/env python3

from copy import deepcopy
import random
import networkx

from spp_benchmark.model import CustomerProviderAS

class TopologyReader(object):

    def __init__(self):
        self.dg = networkx.DiGraph()
        self.dg.dst = None
        self.country_list = dict()
    
    def read_topo(self, as_rel_file, as_type_file=None, as_country_file=None):
        self.read_topo_with_as_rel(as_rel_file)
        if as_type_file:
            self.load_as_type(as_type_file)
        if as_country_file:
            self.load_as_country(as_country_file)

    def read_topo_with_as_rel(self, filepath, dst=None):
        """
        Read AS business relationships from CAIDA dataset and augment it into a
        networkx directed graph.
        """
        self.dg.dst = dst
        with open(filepath, 'r') as as_rel:
            for line in as_rel.readlines():
                if line.startswith('#'):
                    continue
                src_as, dst_as, rel = line.strip('\n').split('|')
                src_asn = int(src_as)
                dst_asn = int(dst_as)
                self.dg.add_edge(src_asn, dst_asn)
                self.dg.add_edge(dst_asn, src_asn)
                if not self.dg._node[src_asn].get('as'):
                    self.dg._node[src_asn]['as'] = CustomerProviderAS(src_asn)
                if not self.dg._node[dst_asn].get('as'):
                    self.dg._node[dst_asn]['as'] = CustomerProviderAS(dst_asn)
                rel_type = int(rel)
                if not rel_type:
                    self.dg.edges[src_asn, dst_asn]['relationship'] = 'pp'
                    self.dg._node[src_asn]['as'].peers.add(dst_asn)
                    self.dg.edges[dst_asn, src_asn]['relationship'] = 'pp'
                    self.dg._node[dst_asn]['as'].peers.add(src_asn)
                else:
                    self.dg.edges[src_asn, dst_asn]['relationship'] = 'pc'
                    self.dg._node[src_asn]['as'].customers.add(dst_asn)
                    self.dg.edges[dst_asn, src_asn]['relationship'] = 'cp'
                    self.dg._node[dst_asn]['as'].providers.add(src_asn)
        if not self.dg.dst and self.dg.dst in self.dg.nodes():
            self.dg._node[self.dg.dst]['as'].unannounced_rib.append((self.dg.dst,))
        return self.dg

    def load_as_type(self, filepath):
        """
        Read AS types from CAIDA dataset and augment it into the network graph.
        """
        with open(filepath, 'r') as as_types:
            for line in as_types.readlines():
                if line.startswith('#'):
                    continue
                asn, _, as_type = line.strip('\n').split('|')
                asn = int(asn)
                if asn in self.dg.nodes():
                    self.dg.nodes[asn]['type'] = as_type[0]

    def load_as_country(self, filepath):
        """
        Read AS countries and augment it into the network graph.
        """
        with open(filepath, 'r') as as_country:
            for line in as_country.readlines():
                asn, country = line.strip('\n').split('|')
                asn = int(asn)
                if asn in self.dg.nodes():
                    self.dg.nodes[asn]['country'] = country
                    if country not in self.country_list:
                        self.country_list[country] = []
                    self.country_list[country].append(asn)
    
    def country_stat(self):
        return sorted([(c, len(al)) for c, al in self.country_list.items()],
                      key=lambda d: d[1], reverse=True)
    
    def print_country_stat(self, head=20):
        for c, num in self.country_stat()[:head]:
            print(c, num)

    def read_as_by_country(self, country):
        return [n for n in self.dg.nodes() if self.dg.nodes[n].get('country', '') == country]

    def get_subtopo_by_country(self, country, maximum=False):
        sub_nodes = self.read_as_by_country(country)
        return safe_connected_subgraph(self.dg, sub_nodes, maximum)
    
    def get_subtopo_by_degree(self, deg_threshold, maximum=False):
        sub_nodes = [n for n in self.dg.nodes() if self.dg.degree(n) >= 2*deg_threshold]
        return safe_connected_subgraph(self.dg, sub_nodes, maximum)
    
    def get_stub_networks_by_rel(self, dg=None):
        _dg = dg or self.dg
        return [n for n in _dg.nodes() if all([_dg.edges[e]['relationship'] != 'pc' for e in _dg.out_edges(n)])]

    def get_random_stub_network(self, dg=None):
        _dg = dg or self.dg
        stub_networks = self.get_stub_networks_by_rel(_dg)
        if not stub_networks:
            return None
        return random.choice(stub_networks)

def set_dst(dg, dst):
    """
    Set destination AS for a graph.
    """
    if 'dst' not in dg.__dir__():
        dg.dst = None
    if dg.dst:
        return
    if dst not in dg.nodes():
        return
    dg.dst = dst
    for n in dg.nodes():
        dg._node[n]['as'].dst = dst
    dg._node[dg.dst]['as'].unannounced_rib.append((dg.dst,))

def safe_connected_subgraph(dg, nodes, maximum=False):
    sdg = dg.subgraph(nodes)
    sub_nodes = []
    if maximum:
        all_comps = [c for c in networkx.algorithms.components.connected_components(sdg.to_undirected())]
        sub_nodes = max(all_comps, key=lambda c: len(c)) if len(all_comps) else []
    else:
        c = random.choice(list(sdg.nodes()))
        sub_nodes = networkx.algorithms.components.node_connected_component(sdg.to_undirected(), c)
    return safe_subgraph(dg, sub_nodes)

def safe_subgraph(dg, nodes):
    """
    Return a deepcopy of subgraph of `dg` including vertices in `nodes`
    without redundant information.
    """
    sdg = deepcopy(dg.subgraph(nodes))
    ns = sdg.nodes()
    for n in sdg.nodes():
        sdg.nodes[n]['as'].customers.intersection_update(ns)
        sdg.nodes[n]['as'].providers.intersection_update(ns)
        sdg.nodes[n]['as'].peers.intersection_update(ns)
    set_dst(sdg, dg.dst)
    return sdg

def example_topology():
    dg = networkx.DiGraph()
    dg.dst = 0
    dg.add_edge(0, 1, relationship='cp')
    dg.add_edge(1, 0, relationship='pc')
    dg.add_edge(0, 2, relationship='cp')
    dg.add_edge(2, 0, relationship='pc')
    dg.add_edge(0, 3, relationship='cp')
    dg.add_edge(3, 0, relationship='pc')
    dg.add_edge(1, 2, relationship='cp')
    dg.add_edge(2, 1, relationship='pc')
    dg.add_edge(1, 3, relationship='cp')
    dg.add_edge(3, 1, relationship='pc')
    dg.add_edge(1, 4, relationship='cp')
    dg.add_edge(4, 1, relationship='pc')
    dg.add_edge(2, 3, relationship='cp')
    dg.add_edge(3, 2, relationship='pc')
    dg.add_edge(2, 4, relationship='cp')
    dg.add_edge(4, 2, relationship='pc')
    dg.add_edge(3, 4, relationship='pp')
    dg.add_edge(4, 3, relationship='pp')
    dg.add_edge(3, 5, relationship='pc')
    dg.add_edge(5, 3, relationship='cp')
    dg.add_edge(3, 6, relationship='pc')
    dg.add_edge(6, 3, relationship='cp')
    dg.add_edge(3, 7, relationship='pp')
    dg.add_edge(7, 3, relationship='pp')
    dg.add_edge(5, 6, relationship='pc')
    dg.add_edge(6, 5, relationship='cp')
    dg.add_edge(5, 7, relationship='cp')
    dg.add_edge(7, 5, relationship='pc')
    dg.add_edge(6, 7, relationship='cp')
    dg.add_edge(7, 6, relationship='pc')

    dg._node[0]['as'] = CustomerProviderAS(0, dst=0, providers={1, 2, 3})
    dg._node[1]['as'] = CustomerProviderAS(1, dst=0, customers={0}, providers={2, 3, 4})
    dg._node[2]['as'] = CustomerProviderAS(2, dst=0, customers={0, 1}, providers={3, 4})
    dg._node[3]['as'] = CustomerProviderAS(3, dst=0, customers={0, 1, 2, 5, 6}, peers={4, 7})
    dg._node[4]['as'] = CustomerProviderAS(4, dst=0, customers={1, 2}, peers={3})
    dg._node[5]['as'] = CustomerProviderAS(5, dst=0, customers={6}, providers={3, 7})
    dg._node[6]['as'] = CustomerProviderAS(6, dst=0, providers={3, 5, 7})
    dg._node[7]['as'] = CustomerProviderAS(7, dst=0, customers={5, 6}, peers={3})

    dg._node[dg.dst]['as'].unannounced_rib.append((dg.dst,))
    return dg

def example_pcg():
    from spp_benchmark.bgp import bgp_sim
    from spp_benchmark.pcgraph import PCGraph
    topo = example_topology()
    bgp_sim(topo)
    pcg = PCGraph()
    pcg.load(topo)
    pcg.build()
    return pcg
