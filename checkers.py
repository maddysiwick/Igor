import pygame
from pygame.locals import *
from monte_carlo_tree_search import MCTS,Node
from collections import namedtuple
from random import choice

_CB=namedtuple('CheckersBoard','tup turn winner terminal')

class CheckersBoard(_CB,Node):
    def find_legal_moves(board,jump):
            moves=(-9,-7,7,9)
            for s,square in enumerate(board.tup):
                    if square==board.turn:
                        if jump:
                            yield (s,s,False,0)
                        for i in moves:
                            if board.tup[s+i]==None and jump==False:
                                yield (s,s+i,False,0)
                            elif board.tup[s+i]==(not board.turn) and board.tup[s+2*i]==None:
                                    yield (s,s+2*i,True,s+i)
                                
    def find_children(board):
        if board.terminal:
            return set()
        legal_moves=board.find_legal_moves(board)
        return {board.make_move(i) for i in legal_moves}
    def find_random_child(board):
        if board.terminal:
            return None
        legal_moves=board.find_legal_moves(board)
        return board.make_move(choice(legal_moves))
    def reward(board):
        if not board.terminal:
            raise RuntimeError(f'reward called on non terminal node {board}')
        if board.winner is board.turn:
            raise RuntimeError(f'reward called on unreachable node {board}')
        if board.turn is (not board.winner):
            return 0
        if board.winner is None:
            return 0.5
        raise RuntimeError(f'board has unknown winner type {board.winner}')
    def is_terminal(board):
        return board.terminal
    def make_move(board,move):
        if move[2]==True:
            if move[0]<move[1]:
                tup=board.tup[:move[0]]+None+board.tup[move[0]+1:move[2]]+None+board.tup[move[2]+1:move[1]]+board.turn+board.tup[move[1]+1:]
            else:
                tup=board.tup[:move[1]]+board.turn+board.tup[move[1]+1:move[2]]+None+board.tup[move[2]+1:move[0]]+None+board.tup[move[0]+1:]
        else:
            if move[0]<move[1]:
                tup=board.tup[:move[0]]+None+board.tup[move[0]+1:move[1]]+board.turn+board.tup[move[1]+1:]
            else:
                tup=board.tup[:move[1]]+board.turn+board.tup[move[1]+1:move[0]]+None+board.tup[move[0]+1:]
        #integrate multiple jumps and kimgs somehow
        turn=not board.turn
        winner=_find_winner(board)
        terminal=winner is not None
        return CheckersBoard(tup,turn,winner,is_terminal)