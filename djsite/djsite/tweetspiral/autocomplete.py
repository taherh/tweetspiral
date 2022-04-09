# Copyright (c) 2012 Taher Haveliwala
# All Rights Reserved
#
# See LICENSE for licensing
#

import bisect

class AutocompleteEngine(object):
    '''Per-request autocompletion handler'''
    
    def __init__(self, request):
        self.request = request
    
    def add_suggestions(self, terms):
        if isinstance(terms, str):
            terms = [terms]
            
        all_names = self.request.session.get('ac_screen_names', [])
        if len(all_names) > 2000:
            return
        for term in terms:
            term = term.lower()
            pos = bisect.bisect_left(all_names, term)
            # only add if not a dup
            if pos >= len(all_names) or all_names[pos] != term:
                all_names.insert(pos, term)
        self.request.session['ac_screen_names'] = all_names
        
    def suggest(self, term):
        term = term.lower()
        all_names = self.request.session['ac_screen_names']
        lower = bisect.bisect_left(all_names, term)
        upper_term = term[:-1] + chr(ord(term[-1])+1)  # fake term repr. upper bound
        upper = bisect.bisect_left(all_names, upper_term)
        return all_names[lower:upper]
