def dijkstra(starter, ender, vs, distance_func):
    ## dijkstra, with edge-length-dictionary as input
    ##
    ## WARNING: this design is flawed.
    ## When we attempt to find path for a starter in the middle of an edge, it could be
    ## so near (or virtually at) a graph vertex that the distance is judged to be 0.
    ##
    ##??? FIRST SNAP TO THE GRAPH VERTICES, THEN FIND THE PATH ????

    ## distance_func(v0, v1) = 0 if not connected, = d(v0,v1) otherwise
    ## returns (boolean_find_successful, result )

    openlist = [starter]
    backtrace = dict({})

    # distance from v to source
    dist = dict({starter: 0})

    neighbours = dict({x: [y for y in vs if distance_func(x, y) > 0] for x in vs})

    while openlist != []:

        min_val = None
        min_path = None
        for u in openlist:
            for v in neighbours[u]:
                if v in dist.keys():
                    neighbours[u].remove(v)
                    continue

                res = dist[u] + distance_func(u, v)
                if min_val is None or min_val > res:
                    min_val = res
                    min_path = (u, v)

        if min_val is None:
            ## somehow we don't find any possible expansions and the exploration fails
            break

        else:
            # do have some new min
            u = min_path[0]
            v = min_path[1]
            dist[v] = min_val
            backtrace[v] = u
            openlist.append(v)
            neighbours[u].remove(v)
            if neighbours[u] == []:
                openlist.remove(u)

            if v == ender:
                return (
                    True,
                    # trace_to(ender, starter, backtrace),
                    dist[v],
                )
            # by default gives [starter,...ender]

    return (False, None)
