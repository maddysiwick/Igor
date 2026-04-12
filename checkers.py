import pygame
from pygame.locals import *
from monte_carlo_tree_search import MCTS,Node
from collections import namedtuple
from random import choice

_CB=namedtuple('CheckersBoard','tup prev turn move winner terminal advantage kings round')

class CheckersBoard(_CB,Node):
    def find_legal_moves(board,moves,king_moves,jumping):
        legal_moves=[]
        for s in range(len(board.tup)):
            if board.tup[s]==board.turn:
                if s in board.kings:
                    for i in king_moves:
                        if 63>=s+i>=0 and check_dark_square(s+i):
                            if (jumping==False or board.tup[int(s+i/2)]==(not board.turn)) and board.tup[s+i]==None:
                                legal_moves.append((s,s+i,jumping,s+i/2))
                else:
                    for i in moves:
                        if 63>=s+i>=0 and check_dark_square(s+i):
                            if (jumping==False or board.tup[int(s+i/2)]==(not board.turn)) and board.tup[s+i]==None:
                                legal_moves.append((s,s+i,jumping,s+i/2))
        
        return legal_moves
    def find_dirs(board):
        if board.turn:
            return (-9,-7)
        return (9,7)                
    def find_children(board):
        if board.terminal:
            return set()
        legal_moves=board.find_legal_moves((14,18),(14,18,-14,-18),True)
        if legal_moves==[]:
            legal_moves=board.find_legal_moves((7,9),(7,9,-7,-9),False)
        return {board.make_move(i) for i in legal_moves}
    def find_random_child(board):
        if board.terminal:
            return None
        legal_moves=board.find_legal_moves((14,18),(14,18,-14,-18),True)
        if legal_moves==[]:
            legal_moves=board.find_legal_moves((7,9),(7,9,-7,-9),False)
        if legal_moves==[]:
            return board
        return board.make_move(choice(legal_moves))
    def reward(board):
        '''if not board.terminal:
            raise RuntimeError(f'reward called on non terminal node {board}')
        if board.winner is board.turn:
            raise RuntimeError(f'reward called on unreachable node {board}')
        if board.turn is (not board.winner):
            return 0
        if board.winner is None:
            return 0.5
        '''
        '''if board.advantage==True:
            return 0
        elif board.advantage==False:
            return 1
        elif board.advantage==None:
            return 0
        raise RuntimeError(f'board has unknown advantage type {board.advantage()}')'''

        return (12-board.tup.count(True))-(12-board.tup.count(False))

    def is_terminal(board):
        return board.terminal
    def make_move(board,move):
        #print(move)
        if move[2]==True:
            if move[0]<move[1]:
                tup=board.tup[:move[0]]+(None,)+board.tup[move[0]+1:move[3]]+(None,)+board.tup[move[3]+1:move[1]]+(board.turn,)+board.tup[move[1]+1:]
            else:
                tup=board.tup[:move[1]]+(board.turn,)+board.tup[move[1]+1:move[3]]+(None,)+board.tup[move[3]+1:move[0]]+(None,)+board.tup[move[0]+1:]
        else:
            if move[0]<move[1]:
                tup=board.tup[:move[0]]+(None,)+board.tup[move[0]+1:move[1]]+(board.turn,)+board.tup[move[1]+1:]
            else:
                tup=board.tup[:move[1]]+(board.turn,)+board.tup[move[1]+1:move[0]]+(None,)+board.tup[move[0]+1:]
        #integrate multiple jumps and kimgs somehow
        prev=board.tup
        turn=not board.turn
        winner=_find_winner(tup)
        is_terminal=winner is not None
        advant=advantage(tup,prev)
        kings=list(board.kings)
        if move[0] in kings:
            kings[kings.index(move[0])]=move[1]
        if move[3] in kings:
            kings.remove(move[3])
        for i in range(8):
            if tup[i] == True and i not in kings:
                print('found a star king')
                kings.append(i)
        round=board.round+1
        for i in range(56, 64):
            if tup[i] == False and i not in kings: 
                print('found a moon king')
                kings.append(i)
        kings=tuple(kings)
        return CheckersBoard(tup,prev,turn,move,winner,is_terminal,advant,kings,round)
def advantage(tup,prev):
    if tup.count(True)<prev.count(True):
        return False
    elif tup.count(False)<prev.count(False):
        return True
    return None
class my_piece:
    def __init__(self,image,position,square):
        self.image=image
        self.rect=image.get_rect(topleft=position)
        self.square=square
    def on_hover(self,pos):
            return self.rect.collidepoint(pos)
    def on_click(self,board):
            return None
class empty_square:
    def __init__(self,position,square):
        self.rect=pygame.Rect(position,(87,87))
        self.square=square
    def on_hover(self,pos):
        return self.rect.collidepoint(pos)
    def on_click(self,moves):
        for move in moves:
            if self.square==move[1]:
                return (True,move)
        return (False,)
def load_board(board,screen,moon,star,king,imp):
    print('kings',board.kings)
    positionss=positions()
    clean=Color(0,0,0,0)
    screen.fill(clean)
    my_pieces=[]
    empties=[]
    screen.blit(imp,(0,0))
    for i,pos in enumerate(positionss):
            value=board.tup[i]
            if value==False:
                if i in board.kings:
                    screen.blit(king,pos)
                else:
                    screen.blit(moon,pos)
            elif value==True:
                if i in board.kings:
                    piece=my_piece(king,pos,i)
                else:
                    piece=my_piece(star,pos,i)
                screen.blit(piece.image,piece.rect)
                my_pieces.append(piece)
            else:
                square=empty_square(pos,i)
                empties.append(square)
    pygame.display.flip()
    return (my_pieces,empties)
def play_game():
    tree=MCTS()
    board=new_checkers_board()
    screen=pygame.display.set_mode((800,800))
    imp=pygame.image.load('assets\Checkerboard_.png').convert_alpha()
    moon=pygame.image.load('assets\Moon_Basic.png').convert_alpha()
    star=pygame.image.load('assets\star.png').convert_alpha()
    king=pygame.image.load('assets\king.jpg').convert_alpha()
    clickables=load_board(board,screen,moon,star,king,imp)
    my_pieces=clickables[0]
    empty_squares=clickables[1]
    legal_moves=[]
    while True:
        while board.turn==True:
            for event in pygame.event.get():
                if event.type==pygame.MOUSEBUTTONDOWN:
                    legal_moves=board.find_legal_moves((-14,-18),(-14,-18,14,18),True)
                    if legal_moves==[]:
                        legal_moves=board.find_legal_moves((-7,-9),(-7,-9,7,9),False)
                    print(legal_moves)
                    for piece in my_pieces:
                        if piece.on_hover(event.pos):
                            start=piece.square
                    for square in empty_squares:
                        if square.on_hover(event.pos):
                            end=square.square
                            eat=start+(end-start)/2
                            if -9>end-start>9:
                                move=(start,end,True,eat)
                            else:
                                move=(start,end,False,eat)
                            print(move)
                            if move in legal_moves:
                                board=board.make_move(move)   
                                clickables=load_board(board,screen,moon,star,king,imp)
                                my_pieces=clickables[0]
                                empty_squares=clickables[1]
        if board.terminal:
            if board.winner==True:
                print('stars won :)')
            else:
                print('moons won :(')
            break
        for _ in range(60):
            print(_)
            tree.do_rollout(board)
        board=tree.choose(board)
        clickables=load_board(board,screen,moon,star,king,imp)
        my_pieces=clickables[0]
        empty_squares=clickables[1]
        if board.terminal:
            break
def _find_winner(tup):
    if tup.count(True)==0:
        return False
    elif tup.count(False)==0:
        return True
    return None
def new_checkers_board():
    start=(False, None, False, None, False, None, False, None, None, False, None, False, None, False, None, False, False, None, False, None, False, None, False, None,None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, True, None, True, None, True, None, True, True, None, True, None, True, None, True, None, None, True, None, True, None, True, None, True)
    ex=(None, None, None, None, None, None, False, None, None, False, None, False, None, False, None, False, False, None, False, None, False, None, False, None,None, None, None, None, None, None, None, None, None, None, False, None, False, None, False, None, None, True, None, True, None, True, None, True, True, None, True, None, True, None, True, None, None, True, None, True, None, True, None, True)
    return CheckersBoard(tup=start,prev=start,turn=True, move=(None,), winner=None,terminal=False,advantage=None,kings=(),round=0)
def positions():
    for i in range(0,8):
        for k in range(0,8):
            yield (44+k*89,44+i*89)
def check_dark_square(square):
    even=True
    for i in range(0,63,8):
        if square in range(i,i+8):
            return (square%2==0)==even
        even=not even
if __name__=='__main__':
    pygame.init()
    play_game()