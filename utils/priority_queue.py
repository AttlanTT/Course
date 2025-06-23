import heapq
from collections import deque

class BiPriorityQueue:
    def __init__(self):
        self.min_heap = []
        self.max_heap = []
        self.insertion_order = deque()

    def enqueue(self, item, priority):
        heapq.heappush(self.min_heap, (priority, item))
        heapq.heappush(self.max_heap, (-priority, item))
        self.insertion_order.append((item, priority))

    def dequeue(self, mode='lowest'):
        if mode == 'lowest':
            return heapq.heappop(self.min_heap)[1]
        elif mode == 'highest':
            return heapq.heappop(self.max_heap)[1]
        elif mode == 'oldest':
            return self.insertion_order.popleft()[0]
        elif mode == 'newest':
            return self.insertion_order.pop()[0]

    def peek(self, mode='lowest'):
        if mode == 'lowest':
            return self.min_heap[0][1]
        elif mode == 'highest':
            return self.max_heap[0][1]
        elif mode == 'oldest':
            return self.insertion_order[0][0]
        elif mode == 'newest':
            return self.insertion_order[-1][0]
