# Implement Queue using Stacks
#
# LeetCode: 232
# Difficulty: Easy
# Pattern: Queue via stacks / vice-versa
#
# Problem:
# Implement a first in first out (FIFO) queue using only two stacks. The implemented queue
# should support all the functions of a normal queue (push, peek, pop, and empty).
#
# Implement the MyQueue class:
# - void push(int x) Pushes element x to the back of the queue.
# - int pop() Removes the element from the front of the queue and returns it.
# - int peek() Returns the element at the front of the queue.
# - boolean empty() Returns True if the queue is empty, False otherwise.
#
# Notes:
# - You must use only standard operations of a stack, which means only push to top, peek/pop
#   from top, size, and is empty operations are valid.
# - Depending on your language, the stack may not be supported natively. You may simulate a
#   stack using a list or deque (double-ended queue) as long as you use only a stack's standard
#   operations.
#
# Example 1:
# Input:
# ["MyQueue", "push", "push", "peek", "pop", "empty"]
# [[], [1], [2], [], [], []]
# Output: [null, null, null, 1, 1, false]
#
# Constraints:
# - 1 <= x <= 9
# - At most 100 calls will be made to push, pop, peek, and empty
# - All the calls to pop and peek are valid

class MyQueue:
    def __init__(self):
        pass

    def push(self, x):
        pass

    def pop(self):
        pass

    def peek(self):
        pass

    def empty(self):
        pass


if __name__ == '__main__':
    q = MyQueue()
    q.push(1)
    q.push(2)
    print(q.peek())
    print(q.pop())
    print(q.empty())
