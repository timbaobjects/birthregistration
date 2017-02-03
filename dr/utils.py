# -*- coding: utf-8 -*-
def pick(keys, dictlike):
	return {k: dictlike[k] for k in keys if k in dictlike}


def values(dictlike):
	return dictlike.values()
