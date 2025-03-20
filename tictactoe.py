from collections import namedtuple
from random import choice
from monte_carlo_tree_search import MCTS,Node

_TTTB=namedtuple('TicTacToeBoard','tup turn winner terminal')

class TicTacToeBoard(_TTTB,Node):
    def find_children(board):
        if board.terminal:
            return set()
        return {
            board.make_move(i) for i, value in enumerate(board.tup) if value is None
        }
    def find_random_child(board):
        if board.terminal:
            return None
        empty_spots=[i for i, value in enumerate(board.tup) if value is None]
        return board.make_move(choice(empty_spots))
    def reward(board):
        if not board.terminal:
            raise RuntimeError(f'reward called on nonterminal board {board}')
        if board.winner is board.turn:
            raise RuntimeError(f'reward called on unreachable board {board}')
        if board.turn is (not board.winner):
            return 0
        if board.winner is None:
            return 0.5
        raise RuntimeError(f'board has unkown winner type {board.winner}')
    def is_terminal(board):
        return board.terminal
    def make_move(board,index):
        tup=board.tup[:index]+(board.turn,)+board.tup[index+1:]
        #print(tup)
        turn=not board.turn
        winner=_find_winner(tup)
        is_terminal=(winner is not None) or not any(v is None for v in tup)
        return TicTacToeBoard(tup,turn,winner,is_terminal)
    def to_pretty_string(board):
        to_char=lambda v:('X' if v is True else ('O' if v is False else ' '))
        rows=[[to_char(board.tup[3*row+col])for col in range(3)]for row in range(3)]
        return('\n 1 2 3\n'+'\n'.join(str(i+1)+' '+' '.join(row) for i, row in enumerate(rows))+'\n')    
def play_game():
    tree=MCTS()
    for i in _winning_combos():
        print(i)
    board=new_tic_tac_toe_board()
    print(board.to_pretty_string())
    while True:
        row_col=input('enter row,col: ')
        row,col=map(int,row_col.split(','))
        index=3*(row-1)+(col-1)
        print(index)
        if board.tup[index] is not None:
            raise RuntimeError('Invalid move')
        board=board.make_move(index)
        print(board.to_pretty_string())
        print(board.terminal)
        print(board.winner)
        if board.terminal:
            break
        for _ in range(150):
            #print(board.to_pretty_string)
            tree.do_rollout(board)
        board=tree.choose(board)
        print(board.to_pretty_string())
        print(board.terminal)
        print(board.winner)
        if board.terminal:
            break
def _winning_combos():
    for start in range(0,9,3):
        yield (start,start+1,start+2)
    for start in range(3):
        yield (start,start+3,start+6)
    yield (0,4,8)
    yield (2,4,6)
def _find_winner(tup):
    for i1,i2,i3 in _winning_combos():
        v1,v2,v3=tup[i1],tup[i2],tup[i3]
        #print(str(v1)+str(v2)+str(v3))
        if False is v1 is v2 is v3:
            return False
        if True is v1 is v2 is v3:
            return True
    return None
def new_tic_tac_toe_board():
    return TicTacToeBoard(tup=(None,)*9,turn=True,winner=None,terminal=False)
if __name__=='__main__':
    play_game()