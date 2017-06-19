from collections import defaultdict


def to_graphviz(graph):
    """

    :param graph:
    :return:
    """
    ret = ['digraph g {']
    vertices = []

    node_ids = dict([(name, 'node' + idx) for (idx, name) in enumerate(list(graph))])

    for node in list(graph):
        ret.append('  "%s" [label="%s"];' % (node_ids[node], node))
        for target in graph[node]:
            vertices.append('  "%s" -> "%s";' % (node_ids[node], node_ids[target]))

    ret += vertices
    ret.append('}')
    return '\n'.join(ret)


def _dfs_cycle_detect(graph, node, path, visited_nodes):
    """
    search graph for cycle using DFS continuing from node
    path contains the list of visited nodes currently on the stack
    visited_nodes is the set of already visited nodes
    :param graph:
    :param node:
    :param path:
    :param visited_nodes:
    :return:
    """
    visited_nodes.add(node)
    for target in graph[node]:
        if target in path:
            #cycle found => return current path
            return path + [target]
        else:
            return _dfs_cycle_detect(graph, target, path + [target], visited_nodes)
    return None


def detect_cycle(graph):
    """
    search the given directed graph for cycles

    returns None if the given graph is cycle free
    otherwise it returns a path through the graph that contains a cycle
    :param graph:
    :return:
    """

    visited_nodes = set()

    for node in list(graph):
        if node not in visited_nodes:
            cycle = _dfs_cycle_detect(graph, node, [node], visited_nodes)
            if cycle:
                return cycle
    return None


def topsort(graph):
    """
    For the given graph, returns a list of nodes in topological order
    In py3 the behaviour of this function differs from py2,
    the resulting order will change with every execution in py3
    while in py2 the order stays the same
    :param graph:
    :return:
    """

    count = defaultdict(int)
    for feature, node in graph.items():
        for target in node:
            count[target] += 1
    # convert for list is necessary for py3 as in py3 the filter
    # function creates a filter object, in py2 it returns a list
    free_nodes = list(filter(lambda x: count[x] == 0, graph))
    result = []
    while free_nodes:
        node = free_nodes.pop()
        result.append(node)
        for target in graph[node]:
            count[target] -= 1
            if count[target] == 0:
                free_nodes.append(target)
    return result
