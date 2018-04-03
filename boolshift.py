import sys
import string
import copy
import random
import pygame
from pygame.locals import *


game_title = "Boolshift"
board_size = 4
font = None
font_small = None
symbols = ['T', 'F', '&', '|', '^', '!', ' ']
tiles = {}
tiles_sliding = {}
board = [[]]
render_board = [[]]
slide_board = [[]]
bg_color = (250,250,250)
transition = 0.0
state = ""
score = 0
score_increment_1 = 1
score_increment_2 = 2
score_increment_3 = 4
score_increment_4 = 8
random_weigh = .5


def make_tile(symb, text_color, fill_color):
    tile_size = int(720 / board_size)
    surf = pygame.Surface((tile_size, tile_size))
    surf.fill(fill_color)
    
    if symb != ' ':
        text = font.render(symb, True, text_color)
        scale = 0.8 * tile_size / text.get_height()
        text = pygame.transform.smoothscale(text, (int(scale*text.get_width()), int(scale*text.get_height())))
        text_pos = text.get_rect()
        text_pos.center = surf.get_rect().center
        surf.blit(text, text_pos)
        
    pygame.draw.rect(surf, text_color, surf.get_rect(), 1)
    return surf

def make_tiles():
    global tiles
    for symb in symbols:
        if symb == ' ':
            color = bg_color
        elif symb == 'T' or symb == 'F':
            color = (180,180,180)
        else:
            color = (200,200,200)    
        tiles[symb] = make_tile(symb, (0,0,0), color)
    
    global tiles_sliding
    for symb in symbols:
        if symb == ' ':
            color = bg_color
        elif symb == 'T' or symb == 'F':
            color = (180,180,180)
        else:
            color = (200,200,200)    
        tiles_sliding[symb] = make_tile(symb, (150,150,150), color)

def draw_board():
    buffer = pygame.Surface((720,720))
    tile_size = 720 / board_size
    
    if state != "sliding":
        for i in range(board_size):
            for j in range(board_size):
                buffer.blit(tiles[render_board[i][j]], (int(i*tile_size), int(j*tile_size)))
    
    if state == "adding":
        overlay = pygame.Surface(tiles['T'].get_size(), SRCALPHA)
        a = int(256-256*transition) if int(256-256*transition) > 0 else 0
        overlay.fill((250,250,250,a))
        pygame.draw.rect(overlay, (0,0,0), overlay.get_rect(), 1)
        for i in range(board_size):
            for j in range(board_size):
                if render_board[i][j] != board[i][j]:
                    buffer.blit(tiles[board[i][j]], (int(i*tile_size), int(j*tile_size)))
                    buffer.blit(overlay, (int(i*tile_size), int(j*tile_size)))
    
    if state == "sliding":
        for i in range(board_size):
            for j in range(board_size):
                buffer.blit(tiles[' '], (int(i*tile_size), int(j*tile_size)))
        for i in range(board_size):
            for j in range(board_size):
                if render_board[i][j] == ' ':
                    continue
                (xslide, yslide) = slide_board[i][j]
                (ishift, jshift) = (xslide*transition, yslide*transition)
                if (xslide, yslide) == (0,0):
                    buffer.blit(tiles[render_board[i][j]], (int((i+ishift)*tile_size), int((j+jshift)*tile_size)))
                else:
                    buffer.blit(tiles_sliding[render_board[i][j]], (int((i+ishift)*tile_size), int((j+jshift)*tile_size)))
    
    if state == "removing":
        overlay = pygame.Surface(tiles['T'].get_size(), SRCALPHA)
        a = int(256*transition) if int(256*transition) < 256 else 255
        overlay.fill((250,250,250,a))
        pygame.draw.rect(overlay, (0,0,0), overlay.get_rect(), 1)
        for i in range(board_size):
            for j in range(board_size):
                if render_board[i][j] != board[i][j]:
                    buffer.blit(tiles[render_board[i][j]], (int(i*tile_size), int(j*tile_size)))
                    buffer.blit(overlay, (int(i*tile_size), int(j*tile_size)))
    
    if state == "gameover":
        overlay = pygame.Surface(buffer.get_size(), SRCALPHA)
        overlay.fill((250,250,250,int(220*transition)))
        text = font.render("GAME OVER", True, (0,0,0))
        text_pos = text.get_rect()
        text_pos.center = overlay.get_rect().center
        if transition > .9:
            overlay.blit(text, text_pos)
        buffer.blit(overlay, (0,0))
        
    pygame.draw.rect(buffer, (0,0,0), buffer.get_rect(), 5)
    
    return buffer

def render_virtual():
    buffer = pygame.Surface((1000, 1000), SRCALPHA)
    buffer_rect = buffer.get_rect()
    
    buffer.fill((0,0,0,0))
    #pygame.draw.rect(buffer, (0,0,0), buffer.get_rect(), 1)
    
    text = font.render(game_title, True, (0, 0, 0))
    text_pos = text.get_rect()
    text_pos.centerx = buffer_rect.centerx
    text_pos.top = buffer_rect.top + 40
    buffer.blit(text, text_pos)
    
    board = draw_board()
    board_pos = board.get_rect()
    board_pos.centerx = buffer_rect.centerx
    board_pos.bottom = buffer_rect.bottom - 50
    buffer.blit(board, board_pos)
    
    text = font_small.render(str(score), True, (20, 20, 20))
    text_pos = text.get_rect()
    text_pos.topright = board_pos.topright
    text_pos.top -= 60
    buffer.blit(text, text_pos)
    
    return buffer

def render(screen):
    buffer = render_virtual()
    scale1 = screen.get_width() / buffer.get_width()
    scale2 = screen.get_height() / buffer.get_height()
    scale = min(scale1, scale2)
    
    screen.fill(bg_color)
    
    buffer = pygame.transform.smoothscale(buffer, (int(scale*buffer.get_width()), int(scale*buffer.get_height())))
    pos = buffer.get_rect()
    pos.center = screen.get_rect().center
    screen.blit(buffer, pos)
    
def render_fps(screen, clock):
    text = font_small.render(str(clock.get_fps()), True, (10,10,10))
    text = pygame.transform.smoothscale(text, (int(text.get_width()/4), int(text.get_height()/4)))
    textpos = text.get_rect()
    textpos.topright = screen.get_rect().topright
    screen.blit(text, textpos)

def transpose(board):
    return [ list(tuple) for tuple in zip(*board) ]
    
def rotate(board):
    board_reverse = [ list[::-1] for list in board ]
    return transpose(board_reverse)
    
def slide_tiles(board):
    stripped = [ [ item for item in row if item != ' ' ] for row in board ]
    padded = [ row + [' '] * (board_size - len(row)) for row in stripped ]
    return padded

def apply_not(board):
    global score
    prev_board = copy.deepcopy(board)
    for i in range(board_size):
        for j in range(board_size-1):
            if board[i][j] == 'T' and board[i][j+1] == '!':
                board[i][j] = 'F'
                board[i][j+1] = ' '
                score += score_increment_2
            if board[i][j] == 'F' and board[i][j+1] == '!':
                board[i][j] = 'T'
                board[i][j+1] = ' '
                score += score_increment_2
    return board != prev_board
    
def apply_and(board):
    global score
    prev_board = copy.deepcopy(board)
    for i in range(board_size):
        for j in range(board_size-2):
            if board[i][j] == 'T' and board[i][j+1] == '&' and board[i][j+2] == 'T':
                board[i][j] ='T'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
            if board[i][j] == 'T' and board[i][j+1] == '&' and board[i][j+2] == 'F':
                board[i][j] ='F'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
            if board[i][j] == 'F' and board[i][j+1] == '&' and board[i][j+2] == 'T':
                board[i][j] ='F'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
            if board[i][j] == 'F' and board[i][j+1] == '&' and board[i][j+2] == 'F':
                board[i][j] ='F'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
    return board != prev_board

def apply_xor(board):
    global score
    prev_board = copy.deepcopy(board)
    for i in range(board_size):
        for j in range(board_size-2):
            if board[i][j] == 'T' and board[i][j+1] == '^' and board[i][j+2] == 'T':
                board[i][j] ='F'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
            if board[i][j] == 'T' and board[i][j+1] == '^' and board[i][j+2] == 'F':
                board[i][j] ='T'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
            if board[i][j] == 'F' and board[i][j+1] == '^' and board[i][j+2] == 'T':
                board[i][j] ='T'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
            if board[i][j] == 'F' and board[i][j+1] == '^' and board[i][j+2] == 'F':
                board[i][j] ='F'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
    return board != prev_board
    
def apply_or(board):
    global score
    prev_board = copy.deepcopy(board)
    for i in range(board_size):
        for j in range(board_size-2):
            if board[i][j] == 'T' and board[i][j+1] == '|' and board[i][j+2] == 'T':
                board[i][j] ='T'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
            if board[i][j] == 'T' and board[i][j+1] == '|' and board[i][j+2] == 'F':
                board[i][j] ='T'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
            if board[i][j] == 'F' and board[i][j+1] == '|' and board[i][j+2] == 'T':
                board[i][j] ='T'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
            if board[i][j] == 'F' and board[i][j+1] == '|' and board[i][j+2] == 'F':
                board[i][j] ='F'
                board[i][j+1] = ' '
                board[i][j+2] = ' '
                score += score_increment_3
    return board != prev_board
    
def shift_up(board):
    prev_board = None
    while board != prev_board:
        prev_board = copy.deepcopy(board)
        board = slide_tiles(board)
        if apply_not(board): continue
        if apply_and(board): continue
        if apply_xor(board): continue
        if apply_or(board): continue
    return board
    
def shift_down(board):
    return rotate(rotate(shift_up(rotate(rotate(board)))))

def shift_left(board):
    return rotate(rotate(rotate(shift_up(rotate(board)))))
    
def shift_right(board):
    return rotate(shift_up(rotate(rotate(rotate(board)))))
    
def can_shift(board):
    global score
    score_copy = score
    shifted = False
    
    board_copy = copy.deepcopy(board)
    shifted = shifted or board != shift_up(board_copy)
    board_copy = copy.deepcopy(board)
    shifted = shifted or board != shift_down(board_copy)
    board_copy = copy.deepcopy(board)
    shifted = shifted or board != shift_left(board_copy)
    board_copy = copy.deepcopy(board)
    shifted = shifted or board != shift_right(board_copy)
    
    score = score_copy
    return shifted
    
def make_slide_board(board, dir_key):
    global slide_board
    slide_board = [ [ (0,0) for i in range(board_size) ] for j in range(board_size) ]
    
    if dir_key == K_UP:
        for i in range(board_size):
            out_pos = 0
            for j in range(board_size):
                if board[i][j] != ' ':
                    slide_board[i][j] = (0, out_pos-j)
                    out_pos += 1
    if dir_key == K_DOWN:
        for i in range(board_size):
            out_pos = board_size - 1
            for j in reversed(range(board_size)):
                if board[i][j] != ' ':
                    slide_board[i][j] = (0, out_pos-j)
                    out_pos -= 1
    if dir_key == K_LEFT:
        for j in range(board_size):
            out_pos = 0
            for i in range(board_size):
                if board[i][j] != ' ':
                    slide_board[i][j] = (out_pos-i, 0)
                    out_pos += 1
    if dir_key == K_RIGHT:
        for j in range(board_size):
            out_pos = board_size - 1
            for i in reversed(range(board_size)):
                if board[i][j] != ' ':
                    slide_board[i][j] = (out_pos-i, 0)
                    out_pos -= 1
                    
def has_full_row(board):
    b1 = [ all(map(lambda x: x == 'T', row)) for row in board ]
    b2 = [ all(map(lambda x: x == 'F', row)) for row in board ]
    b3 = [ all(map(lambda x: x == 'T', row)) for row in transpose(board) ]
    b4 = [ all(map(lambda x: x == 'F', row)) for row in transpose(board) ]
    return any(b1) or any(b2) or any(b3) or any(b4)
    
def remove_full_rows(board):
    global score
    def full_row(row):
        return all(map(lambda x: x == 'T', row)) or all(map(lambda x: x == 'F', row))
    board1 = [ [ ' ' if full_row(row) else item for item in row ] for row in board ]
    board2 = [ [ ' ' if full_row(row) else item for item in row ] for row in transpose(board1) ]
    score += score_increment_4 * (sum([ full_row(row) for row in board]) + sum([ full_row(row) for row in transpose(board) ]))
    return transpose(board2)
    
def random_symbol():
    if random.random() < random_weigh:
        return random.choice(['T', 'F'])
    else:
        return random.choice(['&', '|', '^', '!'])

def add_tile(board):
    n_empty = sum([ tile == ' ' for row in board for tile in row ])
    if n_empty == 0:
        return board
        
    rand = random.randrange(n_empty)
    n = 0
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] != ' ':
                continue
            if n == rand:
                board[i][j] = random_symbol()
            n += 1
    
    global score
    score += score_increment_1
    
    return board
    
def init():
    global score
    score = 0
    global board
    board = add_tile([ [ ' ' for i in range(board_size) ] for j in range(board_size) ])
    global render_board
    render_board = copy.deepcopy(board)
    global state
    state = "waiting"

def main():
    pygame.init()
    screen_flags = pygame.RESIZABLE
    screen = pygame.display.set_mode((500,500), screen_flags)
    pygame.display.set_caption(game_title)
    
    global font
    font = pygame.font.SysFont("monospace", 120)
    global font_small
    font_small = pygame.font.SysFont("monospace", 48)
    make_tiles()
    
    global score
    global board
    global render_board
    global state
    global transition
    init()
    
    clock = pygame.time.Clock()
    
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == VIDEORESIZE:
                screen = pygame.display.set_mode((event.w,event.h), screen_flags)
            if event.type == MOUSEBUTTONDOWN:
                if state == "gameover":
                    init()
                    continue
            if event.type == KEYDOWN:
                if state == "waiting" or state == "adding":
                    prev_board = copy.deepcopy(board)
                    if event.key == K_UP:
                        board = shift_up(board)
                    if event.key == K_DOWN:
                        board = shift_down(board)
                    if event.key == K_LEFT:
                        board = shift_left(board)
                    if event.key == K_RIGHT:
                        board = shift_right(board)
                    
                    if board != prev_board:
                        render_board = prev_board
                        make_slide_board(render_board, event.key)
                        state = "sliding"
                        transition = 0
                    elif has_full_row(board):
                        render_board = copy.deepcopy(board)
                        board = remove_full_rows(board)
                        state = "removing"
                        transition = .2
                    
                        
        if state == "waiting":    
            if not can_shift(board) and not has_full_row(board):
                state = "gameover"
                transition = 0
                
        if state == "sliding":
            if transition < 1:
                transition += .2
            else:
                if has_full_row(board):
                    render_board = copy.deepcopy(board)
                    board = remove_full_rows(board)
                    state = "removing"
                    transition = .2
                else:
                    render_board = copy.deepcopy(board)
                    board = add_tile(board)
                    state = "adding"
                    transition = .2
        
        if state == "removing":
            if transition < 1:
                transition += .05
            else:
                render_board = copy.deepcopy(board)
                board = add_tile(board)
                state = "adding"
                transition = .2
        
        if state == "adding":
            if transition < 1:
                transition += .05
            else:
                render_board = copy.deepcopy(board)
                state = "waiting"
                transition = 0
            
        if state == "gameover":
            if transition < 1:
                transition += .05

        render(screen)
        #render_fps(screen, clock)
        pygame.display.flip()
        clock.tick(60)
    
        
if __name__ == "__main__":
    main()


