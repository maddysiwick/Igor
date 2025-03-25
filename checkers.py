import pygame
from pygame.locals import *
from monte_carlo_tree_search import MCTS,Node
from collections import namedtuple
from random import choice

_CB=namedtuple('CheckersBoard','tup prev turn winner terminal')

class CheckersBoard(_CB,Node):
    def find_legal_moves(board,jump):
        legal_moves=[]
        moves=(-9,-7,7,9)
        for s,square in enumerate(board.tup):
                if square==board.turn:
                    #if jump:
                        #legal_moves.append((s,s,False,0))
                    for i in moves:
                        if 63>=s+i>=0:
                            if board.tup[s+i]==None:
                                legal_moves.append((s,s+i,False,0))
                        elif 63>=s+i*2>=0:
                            if board.tup[s+i]==(not board.turn) and board.tup[s+2*i]==None:
                                legal_moves.append((s,s+2*i,True,s+i))
        return legal_moves                          
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
        #print(move)
        if move[2]==True:
            if move[0]<move[1]:
                tup=board.tup[:move[0]]+(None,)+board.tup[move[0]+1:move[2]]+(None,)+board.tup[move[2]+1:move[1]]+(board.turn,)+board.tup[move[1]+1:]
            else:
                tup=board.tup[:move[1]]+(board.turn,)+board.tup[move[1]+1:move[2]]+(None,)+board.tup[move[2]+1:move[0]]+(None,)+board.tup[move[0]+1:]
        else:
            if move[0]<move[1]:
                tup=board.tup[:move[0]]+(None,)+board.tup[move[0]+1:move[1]]+(board.turn,)+board.tup[move[1]+1:]
            else:
                tup=board.tup[:move[1]]+(board.turn,)+board.tup[move[1]+1:move[0]]+(None,)+board.tup[move[0]+1:]
        #integrate multiple jumps and kimgs somehow
        prev=board.tup
        turn=not board.turn
        winner=_find_winner(board)
        is_terminal=winner is not None
        return CheckersBoard(tup,prev,turn,winner,is_terminal)
class my_piece:
    def __init__(self,image,position,square):
        self.image=image
        self.rect=image.get_rect(topleft=position)
        self.square=square
    def on_hover(self,pos):
            return self.rect.collidepoint(pos)
    def on_click(self,board):
            s=self.square
            moves=(-9,-7,7,9)
            legal_moves=[]
            for i in moves:
                if 63>=s+i>=0:
                    if board.tup[s+i]==None:
                        legal_moves.append((s,s+i,False,0))
                elif 63>=s+i*2>=0:
                    if board.tup[s+i]==(not board.turn) and board.tup[s+2*i]==None:
                        legal_moves.append((s,s+2*i,True,s+i))
            return legal_moves
class empty_square:
    def __init__(self,image,position,square):
        self.image=image
        self.rect=image.get_rect(topleft=position)
        self.square=square
    def on_hover(self,pos):
        return self.rect.collidepoint(pos)
    def on_click(self,moves):
        print(self.square)
        for move in moves:
            if self.square==move[1]:
                return (True,move)
        return (False,)
def load_board(positionss,board,screen,moon,star,empty,imp):
    clean=Color(0,0,0,0)
    screen.fill(clean)
    my_pieces=[]
    empties=[]
    screen.blit(imp,(0,0))
    for i,pos in enumerate(positionss):
            value=board.tup[i]
            if value==False:
                screen.blit(moon,pos)
            elif value==True:
                piece=my_piece(image=star,position=pos,square=i)
                screen.blit(piece.image,piece.rect)
                my_pieces.append(piece)
            else:
                square=empty_square(image=empty,position=pos,square=i)
                screen.blit(square.image,square.rect)
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
    empty=pygame.image.load('assets\empty.png').convert_alpha()
    positionss=positions()
    clickables=load_board(positionss,board,screen,moon,star,empty,imp)
    my_pieces=clickables[0]
    empty_squares=clickables[1]
    legal_moves=[]
    while True:
        while board.turn==True:
            for event in pygame.event.get():
                if event.type==pygame.MOUSEBUTTONDOWN:
                    for piece in my_pieces:
                        if piece.on_hover(event.pos):
                            moves=piece.on_click(board)
                            if moves!=[]:
                                legal_moves=moves
                            #for move in legal_moves:
                                #print(move)
                    for square in empty_squares:
                        if square.on_hover(event.pos):
                            legal=square.on_click(legal_moves)
                            if legal[0]:
                                positionss=positions()
                                board=board.make_move(legal[1])
                                clickables=load_board(positionss,board,screen,moon,star,empty,imp)
                                my_pieces=clickables[0]
                                empty_squares=clickables[1]
        if board.terminal:
            break
        for _ in range(15):
            print(_)
            tree.do_rollout(board)
        board=tree.choose(board)
        clickables=load_board(positionss,board,screen,moon,star,empty,imp)
        my_pieces=clickables[0]
        empty_squares=clickables[1]
        if board.terminal:
            break
def _find_winner(board):
    if board.tup.count(True)==0:
        print('moons won :(')
        return False
    elif board.tup.count(False)==0:
        print('stars won :)')
        return True
    return None
def new_checkers_board():
    start=(False, None, False, None, False, None, False, None, None, False, None, False, None, False, None, False, False, None, False, None, False, None, False, None,None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, True, None, True, None, True, None, True, True, None, True, None, True, None, True, None, None, True, None, True, None, True, None, True)
    return CheckersBoard(tup=start,prev=start,turn=True,winner=None,terminal=False)
def positions():
    for i in range(0,8):
        for k in range(0,8):
            yield (44+k*89,44+i*89)
if __name__=='__main__':
    pygame.init()
    play_game()