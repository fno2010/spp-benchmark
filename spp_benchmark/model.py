#!/usr/bin/env python3

class AutonomousSystem(object):

    def __init__(self, asn, dst):
        self.asn = asn
        self.dst = dst
        self.announced_rib = []
        self.unannounced_rib = []
        self.custom_local_pref = lambda p: None
    
    def set_local_pref(self, pref):
        self.custom_local_pref = pref

    def import_filter(self, p):
        if type(p) not in [list, tuple]:
            return False
        if len(p) < 2:
            return False
        if p[0] != self.dst:
            return False
        if p[-1] != self.asn:
            return False
        if self.asn in p[:-1]:
            return False
        return True

    def export_filter(self, p):
        if type(p) not in [list, tuple]:
            return False
        if len(p) < 2:
            return False
        if p[0] != self.dst:
            return False
        if p[-2] != self.asn:
            return False
        return True

    def permitted_paths(self):
        return self.announced_rib + self.unannounced_rib

    def default_local_pref(self, p):
        return 100
    
    def local_pref(self, p):
        c_local_pref = self.custom_local_pref(p)
        if c_local_pref is None:
            return self.default_local_pref(p)
        return c_local_pref

    def path_score(self, p):
        return (self.local_pref(p), len(p), p[-2] if len(p) > 2 else 0)

    def ranked_permitted_paths(self):
        return sorted(self.permitted_paths(), key=lambda p: self.path_score(p), reverse=True)


class CustomerProviderAS(AutonomousSystem):

    def __init__(self, asn, dst=None, customers=set(), providers=set(), peers=set()):
        AutonomousSystem.__init__(self, asn, dst)
        self.customers = customers
        self.providers = providers
        self.peers = peers

    def default_local_pref(self, p):
        if len(p) > 2 and p[-2] in self.customers:
            return 150
        else:
            return 100

    def export_filter(self, p):
        if not AutonomousSystem.export_filter(self, p):
            return False
        if len(p) > 2 and p[-3] not in self.customers and p[-1] not in self.customers:
            return False
        return True
