# Copyright (c) 2012 Taher Haveliwala
# All Rights Reserved
#
# See LICENSE for licensing
#

class FakeError(Exception):
    pass

class RateLimitError(Exception):
    logged_in = None
    def __init__(self, logged_in=False):
        self.logged_in = logged_in

class UnsupportedRelationError(Exception):
    relation_type = None
    def __init__(self, relation_type=""):
        self.relation_type = ""

