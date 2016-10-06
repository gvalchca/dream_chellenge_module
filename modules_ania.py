import UTILITIES as UT
import sys
import os
import math
import igraph as ig
import merge_graphs as merge
from collections import Counter

max_level = 2


def main():
    # max_level = int(sys.argv[2])
    if sys.argv[1] == 'sub1':
        for_production(UT.get_sub1_networks())
    if sys.argv[1] == 'sub2':
        # UT.get_sub2_networks()
        for_production2()


def run_multiple_for_nework(G, func, nn):
    M = []
    one_round(M, G, func, 'community_walktrap', 0, nn)
    #one_round(M, G, func, 'community_multilevel', 0, nn)
    return M


def for_production2(DD=False):
    print('running for sub2')
    G = ig.Graph.Read_GraphML(UT.get_dir('networks') + '/dream_merge.graphml')
    print('read merged!')
    KK = list(list(G.es)[0].attributes().keys())
    # new_KK = [scale_parameter_and_add(G, k, 10) for k in KK]
    add_attribute(G, KK, my_power)
    # G.write_graphml(UT.get_dir('networks') + '/dream_merge_scaled_added.graphml')
    M = run_multiple_for_nework(G, 'my_power', 'id')
    modules_to_gmt(M, 'sub2_my_power_multilevel_' + str(max_level) + '.gmt')


def for_production(DD):
    print('running for sub1')
    # ddir = 'com_walktr_down_05_' + str(max_level)
    ddir = 'com_multilevel_05_' + str(max_level)
    try:
        os.system('mkdir ' + ddir)
    except Exception:
        pass
    for nname in DD.keys():
        print('runing for network', nname)
        for_single(DD[nname].to_undirected(), nname, ddir)


def for_single(G, nname, ddir):
    modules_to_gmt(run_multiple_for_nework(G, 'weight', 'name'),
                   ddir + '/' + nname + '.gmt')
    return nname


def one_round(M, G, func, method, level, nn):
    func_graph = getattr(G, method)
    if not isinstance(func, str):
        ff = func.__name__
    else:
        ff = func
    for g in get_modules(G, ff, func_graph, 5 - level).subgraphs():
        if len(g.vs()) < 3:
            continue
        elif len(g.vs()) < 70 or level > max_level:
            M.append(get_v_to_module(g.vs(), nn))
        else:
            one_round(M, g, func, method, level+1, nn)


def get_v_to_module(ll, nn):
    m = [i[nn] for i in ll]
    return m


def get_modules_leghts(modules):
    return Counter([len(m) for m in modules])


def megre_networks(dd):
    merged = merge.merge_graphs(dd)
    merged.write_graphml(UT.get_dir() + '/out_networks_merged.graphml')
    return merged


def scale_parameter_and_add(G, k, N=5.0):
    new_attr = k + '_scaled'
    if k == 'KEGG':
        for e in G.es:
            e[new_attr] = e.attributes()[k]
    else:
        values = [e.attributes()[k] for e in G.es
                  if not math.isnan(e.attributes()[k])]
        mmin = min(values)
        for e in G.es:
            val = e.attributes()[k]
            if val is None:
                e[new_attr] = val
            else:
                e[new_attr] = scale_val(val, mmin, (max(values) - mmin)/N)
    return new_attr


def scale_val(val, mmin, rr):
    if not math.isnan(val):
        return int((val - mmin)/rr)
    return val


def add_attribute(G, KK, func):
    print('adding ', func.__name__)
    for e in G.es:
        tmp = func([e.attributes()[k] for k in KK])
        e[func.__name__] = tmp


def my_max(tmp):
    return max([i for i in tmp if i is not None])


def my_sum(tmp):
    tmp = [i for i in tmp if i is not None]
    return sum(tmp)


def my_average(tmp):
    tmp = [i for i in tmp if i is not None]
    return sum(tmp)/4.0


def my_power(tmp):
    return sum([1 for i in tmp if i is not None])


def get_modules(G, func, method, steps):
    nn = method.__name__.split('_')[1]
    # modules = method(weights=func, steps=steps)
    modules = method(weights=func)
    if nn == 'walktrap':
        modules = modules.as_clustering()
    return modules


def translate_module(m, G):
    for v in m:
        new_v = G.vs(v)
        print(v, new_v, new_v.name)
        input('?')


def no_single_modules(modules):
    modules_filtered = [m for m in modules if len(m) >= 3]
    return modules_filtered


def modules_to_gmt(vertex_sets, outfile):
    with open(outfile, 'wt') as fp:
        for i, vset in enumerate(vertex_sets):
            tmp = [str(i), '1']
            tmp.extend([str(i) for i in vset])
            fp.writelines('\t'.join(tmp) + "\n")
    print('written to file', outfile)


def read_merged_network_all():
    return ig.Graph.Read_GraphML('/Users/agorska/Desktop/dream_merge.graphml')


if __name__ == '__main__':
    main()
