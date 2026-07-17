#!/bin/python3

import math
import os
import random
import re
import sys



#
# Complete the 'countIsolatedCommunicationGroups' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. 2D_INTEGER_ARRAY links
#  2. INTEGER n
#
def dfs(adj, start, visited):
    stack = [start]
    visited[start] = True
    while stack:
        node = stack.pop()
        for neighbour in adj[node]:
            if not visited[neighbour]:
                visited[neighbour] = True
                stack.append(neighbour)
        
        
def countIsolatedCommunicationGroups(links, n):
    adj_list = [[] for _ in range(n)]
    for link in links:
        adj_list[link[0]].append(link[1]) 
        adj_list[link[1]].append(link[0]) 
    visited = [False]*n
    count = 0
    for i in range(len(visited)):
        if not visited[i]:
            count+=1
            dfs(adj_list,i,visited)
    return count

if __name__ == '__main__':
    n = 4
    links = [[0, 1], [2, 3]]

    result = countIsolatedCommunicationGroups(links, n)

    print(result)
