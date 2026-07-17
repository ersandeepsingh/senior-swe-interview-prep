#!/bin/python3

import math
import os
import random
import re
import sys



#
# Complete the 'getBinarySearchTreeHeight' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER_ARRAY values
#  2. INTEGER_ARRAY leftChild
#  3. INTEGER_ARRAY rightChild
#

def getBinarySearchTreeHeight(values, leftChild, rightChild):
    """
    We are given a flat array representation of a binary search tree:
    - values: list of node values
    - leftChild: leftChild[i] is the index of values[] of the left child of node i or -1 if no left child
    - rightChild: rightChild[i] is the index of the right child or -1

    The task is to return the height of the BST.
    - Height is the number of nodes on the longest path from root to any leaf minus 1 (edges count).
    - Root is always at index 0.

    We use a simple recursive function to compute the height at each node.
    """

    def height(index):
        if index == -1:
            return -1  # Base: Empty child links contribute -1 so leaf node returns 0
        left_h = height(leftChild[index])
        right_h = height(rightChild[index])
        return 1 + max(left_h, right_h)
    
    return height(0)

if __name__ == '__main__':
    values_count = int(input().strip())

    n = 7
    values = [4, 2, 6, 1, 3, 5, 7]
    leftChild = [1, 3, 5, -1, -1, -1, -1]
    rightChild = [2, 4, 6, -1, -1, -1, -1]

    result = getBinarySearchTreeHeight(values, leftChild, rightChild)

    # Visualize the tree structure
    def print_tree(index, level=0, prefix="Root: "):
        if index == -1:
            return
        print(" " * (level * 4) + prefix + str(values[index]))
        if leftChild[index] != -1 or rightChild[index] != -1:
            if leftChild[index] != -1:
                print_tree(leftChild[index], level + 1, prefix="L--- ")
            else:
                print(" " * ((level+1)*4) + "L--- None")
            if rightChild[index] != -1:
                print_tree(rightChild[index], level + 1, prefix="R--- ")
            else:
                print(" " * ((level+1)*4) + "R--- None")

    print("Tree structure:")
    print_tree(0)
    print("BST Height:", result)
