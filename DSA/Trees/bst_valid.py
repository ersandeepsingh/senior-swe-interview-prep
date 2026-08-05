class Node:
    def __init__(self, val) -> None:
        self.val = val
        self.left = None
        self.right = None

def valid_binary(root, min_val=float('-inf'), max_val=float('inf')):
    if root is None:
        return True
    if not (min_val < root.val < max_val):
        return False
    return valid_binary(root.left, min_val, root.val) and valid_binary(root.right, root.val, max_val)




if __name__=='__main__':
    # Forming a valid binary search tree:
    t = Node(10)
    t.left = Node(5)
    t.right = Node(15)
    t.left.left = Node(2)
    t.left.right = Node(7)
    t.right.left = Node(12)
    t.right.right = Node(18)
    
    result = valid_binary(t)
    print(result)