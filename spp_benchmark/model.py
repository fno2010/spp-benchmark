#!/usr/bin/env python3

class AutonomousSystem(object):

    def __init__(self, asn, dst):
        self.asn = asn
        self.dst = dst
        self.announced_rib = []
        self.unannounced_rib = []

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


class CustomerProviderAS(AutonomousSystem):

    def __init__(self, asn, dst=None, customers=set(), providers=set(), peers=set()):
        self.customers = customers
        self.providers = providers
        self.peers = peers
        AutonomousSystem.__init__(self, asn, dst)
    
    def export_filter(self, p):
        if not AutonomousSystem.export_filter(self, p):
            return False
        if len(p) > 2 and p[-3] not in self.customers and p[-1] not in self.customers:
            return False
        return True