# -*- coding: utf-8 -*-
"""
@author: ania
"""

import os
import igraph as ig
import time


def getGenesFromGwas(cat):
    ll = [i.replace('.txt', '') for i in os.listdir(cat)
          if i.endswith('.txt')]
    ll.sort()
    D = {}
    for gwas_file in ll:
        snps = getSnpsFromGwas(gwas_file, cat)
        D[gwas_file.replace('.txt', '')] = snps
    return D


def getSnpsFromGwas(gwas_file, cat):
    f = open(cat + '/' + gwas_file + '.txt', 'r')
    ll = []
    for i in f.readlines():
        try:
            ll.append(i.split()[0].replace(';', ''))
        except Exception:
            print('cant parse', i)
    f.close()
    return ll


def get_dir(cat=False):
    D_home = '/'.join(os.getcwd().split('/')[:3])
    D_home_dir = D_home + '/Dropbox/DreamBEST/'
    if not cat:
        return D_home
    cat = cat.lower()
    if cat == 'modules':
        return D_home_dir + 'modules'
    if cat == 'modules_inputs':
        return D_home_dir + 'modules/inputs'
    if cat == 'modules_output':
        return D_home_dir + 'modules/outputs'
    if cat == 'figures':
        return D_home_dir + 'figures'
    if cat == 'networks':
        return D_home_dir + 'networks'
    if cat == 'gwas':
        return D_home_dir + 'gwas'
    if cat == 'sub1':
        return D_home + '/Dropbox/sub1'
    if cat == 'sub2':
        return D_home + '/Dropbox/sub2'
    if cat == 'chellenge':
        return D_home_dir + 'networks/dream_merge.graphml.tar.gz'
    if cat == 'exemplary':
        return D_home_dir + 'networks/4_exemplary_networks_pkl.gz'
    return D_home_dir


def get_files_with_ending(ending, dd='./'):
    return [i for i in os.listdir(dd) if i.endswith(ending)]


def perc(a, b):
    return a/b * 100


def get_networks_in_dir(ddir):
    ll = [i for i in os.listdir(ddir)
          if i.endswith('.txt') and i[0].isdigit()]
    ll.sort()
    return ll


def get_sub1_networks():
    return get_sub_networks('sub1')


def get_sub2_networks():
    return get_sub_networks('sub2')


def get_sub_networks(ddir, perc=0.05):
    DD = get_dir(ddir)
    D = {}
    for fname in get_networks_in_dir(DD):
        directed = False
        print('reading', fname)
        if 'directed' in fname:
            directed = True
        g = ig.Graph.Read_Ncol(DD + '/' + fname, directed=directed)
        filter_edges(g, perc, fname)
        D[fname.split('_anonym')[0]] = g
    return D


def filter_edges(g, perc, fname):
    before = len(g.es())
    ll = compute_weight(g.es['weight'], perc)
    g = g.subgraph_edges(g.es.select(weight_gt=ll))
    print(fname, 'edges:', before, '->', len(g.es()), 'level', round(ll, 2))


def compute_weight(ss, perc):
    mmax = max(ss)
    mmin = min(ss)
    return mmin + (mmax - mmin) * perc


def get_exemplary_networks():
    D = {}
    files = {'KEGG': '/signal/kegg/kegg_hsa_no_modifier_weights.sif',
             'PPI_ConsensusPathDB': '/ppi/ConsensusPathDB/ConsensusPathDB_human_PPI_2016-07-19_edge_list.tab',
             'PPI_irefindex': '/ppi/irefindex/9606.07042015.entrez_removed_outliers.csv',
             'HomologyKEGG': '/homology/kegg_entrez_edges.txt'}
    for f in files.keys():
        file_name = get_dir('networks') + files[f]
        directed = False
        if f == 'KEGG':
            directed = True
        D[f] = ig.Graph.Read_Ncol(file_name, directed=directed)
        print('read ' + f + ' network', 'vs:',
              len(D[f].vs), 'es:', len(D[f].es))
    return D
