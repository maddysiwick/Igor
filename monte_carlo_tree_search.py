from abc import ABC,abstractmethod
from collections import defaultdict
import math

class MCTS:
    def __init__(self,exploration_weight=1):
        self.Q=defaultdict(int)
        self.N=defaultdict(int)
        self.children=dict()
        self.exploration_weight=exploration_weight
    def choose(self,node):
        if node.is_terminal():
            raise RuntimeError(f'choose called on terminal node {node}')
        if node not in self.children:
            return node.find_random_child()
        def score(n):
            if self.N[n]==0:
                return float('-inf')
            return self.Q[n]/self.N[n]
        return max(self.children[node], key=score)
    def do_rollout(self,node):
        path=self._select(node)
        leaf=path[-1]
        self._expand(leaf)
        reward=self._simulate(leaf)
        self._backpropagate(path,reward)
    def select(self,node):
        path=[]
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                return path
            unexplored=self.children[node]-self.children.keys()
            if unexplored:
                n=unexplored.pop()
                path.append(n)
                return path
            node=self._uct_select(node)
    def _expand(self,node):
        if node in self.children:
            return
        self.children[node]=node.find_children()
    def _simulate(self,node):
        invert_reward=True
        while True:
            if node.is_terminal():
                reward=node.reward()
                return 1 - reward if invert_reward else reward
            node=node.find_random_child()
            invert_reward=not invert_reward
    def _backpropagate(self,path,reward):
        for node in reversed(path):
            