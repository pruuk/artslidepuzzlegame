"""
Game Objects file
"""
# imports
import pygame, math, random, os, time
from pygame import mixer
from itertools import repeat
from PIL import Image
import sqlite3

# globals
Images = ['images/coronation.jpg', 'images/gloriatiled1.jpg', 'images/jacktiled.jpg', 'images/rebirth.jpg', 'images/swim_with_fishies.jpg']
Music = ['sounds/music_loop_1.mp3', 'sounds/music_loop_2.mp3', 'sounds/music_loop_3.mp3', 'sounds/music_loop_4.mp3', 'sounds/music_loop_5.mp3']

class Game():
    "Game Object"
    def __init__(self):  
        # initialize pygame
        pygame.init()
        # create first level
        self.lvl_num = 1
        self.level = Level(self.lvl_num)
        # game params for starting
        self.running = True
        self.win = False
        self.pause_between_levels = 3
        
    
    def spawn_new_level(self):
        "Previous level defeated. spawn next level"
        # check to see if we need to update the best & worst score in the db
        if not isinstance(self.level.best_score, int):
            # new best score, no previous score
            self.level.db.replace_best(self.lvl_num, self.level.board.swap_moves)
        if self.level.best_score > self.level.board.swap_moves:
            # new best score
            self.level.db.replace_best(self.lvl_num, self.level.board.swap_moves)
        if not isinstance(self.level.worst_score, int):
            # new worst score, no previous score
            self.level.db.replace_worst(self.lvl_num, self.level.board.swap_moves)
        if self.level.worst_score < self.level.board.swap_moves:
            # new worst score
            self.level.db.replace_worst(self.lvl_num, self.level.board.swap_moves) 
        # pause game for a few seconds to congratulate the player
        self.level.display_congrats_text()
        time.sleep(self.pause_between_levels)
        # update the level
        self.lvl_num += 1
        # spawn a new game object for the next level
        self.level = Level(self.lvl_num)
        # reset win to False to avoid infinite loop
        self.win = False
        

class Level():
    "Level Object"
    def __init__(self, lvl_num):
        self.lvl_num = lvl_num
        # create a screen object
        self.screen = Game_screen()
        self.display = self.screen.setup_display()
        # create the board
        self.board = Board(random.choice(Images), self.screen.width, self.screen.height, (lvl_num + 1), (lvl_num + 1))
        # start the music
        music = Background_music(random.choice(Music))
        # create tiles from the mother image
        self.board.tile_up()
        # make one tile the empty tile
        self.board.pick_missing_tile()
        # shuffle the board
        self.board.shuffle_board()
        # create the table if it hasn't been already
        self.db = DB()
        # fetch the best and worst scores for this level
        self.best_score = self.db.query_scores_for_level(self.lvl_num)[0][1]
        self.worst_score = self.db.query_scores_for_level(self.lvl_num)[0][2]
        
        
    def game_loop(self, running):
        "Main game loop"
        # check for moveable tiles
        self.board.pick_moveable_tiles()
        
        # get the current mouse position & if the mouse button is currently pressed
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # check for key presses
        self.key_down = False
        self.key_state = pygame.key.get_pressed()
        for key in self.key_state:
            if key:
                self.key_down = True
                
        # check for win condition
        self.win = self.board.solved(True)
        
        for event in pygame.event.get():
        # check for user clicking the X to close the game
            if event.type == pygame.QUIT:
                # cleanup all the tile images we created
                self.cleanup_tile_image_files()
                running = False
            
        for i in range(len(self.board.tile_dict)):
            # ensure tile is valid, draw tile
            if self.board.tile_dict[i]:
                self.board.tile_dict[i].draw(self.display)
            else:
                raise IndexError
                
            # check to see if the tile is currently highlighted
            self.board.tile_dict[i].highlight(self.mouse_pos[0], self.mouse_pos[1])
            # draw an appropriately colored rectangle around highlighted tiles
            
            if self.board.tile_dict[i].mouse_highlight:
                color = (255, 0, 0)
                if self.board.tile_dict[i] in self.board.moveable_tiles.values():
                    color = (0, 255, 0)
                    if self.mouse_clicked:
                        # highlighting an swappable tile and pressing mouse, swap the tile!
                        self.board.swap_tiles(self.board.tile_dict[i], False)
                        self.mouse_clicked = False
            
                pygame.draw.rect(self.display, color, pygame.Rect((self.board.tile_dict[i].curX - 5, self.board.tile_dict[i].curY - 5), 
                                                                  (self.board.tile_dict[i].width + 5, self.board.tile_dict[i].height + 5)), 2)
                
        # show text for the level we're on, incorrect tiles, moves, scores
        self.display_text()     
                           
        pygame.display.update()
        return running, self.win
    
    
    def display_text(self):
        "display current level"
        # current level
        font = pygame.font.Font('freesansbold.ttf', 32)
        font_color = (255, 69, 0) # bright orange
        level_font = font.render(f"Level: {self.lvl_num}", True, (font_color))
        self.display.blit(level_font, (30, 30))
        # incorrect tiles
        self.board.num_of_incorrect_tiles()
        inc_t_font = font.render(f"Incorrect Tiles: {self.board.incorrect_tiles}", True, (font_color))
        self.display.blit(inc_t_font, (1575, 30))
        #moves
        moves_font = font.render(f"Moves: {self.board.swap_moves}", True, (font_color))
        self.display.blit(moves_font, (1575, 80))
        # best score
        best_font = font.render(f"Best Score: {self.best_score}", True, (font_color))
        self.display.blit(best_font, (30, 80))
        # worst score
        worst_font = font.render(f"Worst Score: {self.worst_score}", True, (font_color))
        self.display.blit(worst_font, (30, 130))
       
        
    def display_congrats_text(self):
        "display text for completing level"
        font = pygame.font.Font('freesansbold.ttf', 64)
        # bonus points for the Fight Club reference!
        level_over_font = font.render("Congratulations! Moving on to next level!", True, (100, 149, 237))
        self.display.blit(level_over_font, (200, 500))
        # sound for level completion
        completion_sound = mixer.Sound('sounds/complete_level.wav')
        completion_sound.play()
        # sound for next level
        n_lvl = mixer.Sound('sounds/next_level.mp3')
        n_lvl.play()
        pygame.display.update()
        
    
    def cleanup_tile_image_files(self):
        "removes tile images from image folder"
        for i in range(len(self.board.tile_dict)):
            os.remove(self.board.tile_dict[i].img_file_name)


class Game_screen():
    """
    Class for game screen object. This will be instantiated to form a screen for the player
    to play the game upon.
    """
    
    def __init__(self):
        self.width = 1920
        self.height = 1080
        self.title = "Art Slide Puzzle Game"
        self.icon = pygame.image.load('images/jack.jpg')
        self.fill_color = (125, 125, 125)
        
        
    def setup_display(self):
        """
        Set up display in python
        """
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        # set icon
        pygame.display.set_icon(self.icon)
        self.display.fill(self.fill_color)
        return self.display
    

class Background_music():
    "Class for instantiating background music object"
    
    def __init__(self, music_filename):
        mixer.music.load(music_filename)
        mixer.music.play(-1)
    

class Board():
    """
    Class for art image objects. These objects will be broken into tiles and shuffled from their original positions
    """
    def __init__(self, image_file, img_width, img_height, num_of_tile_columns, num_of_tile_rows):
        self.image_file = image_file
        self.img_w = img_width
        self.img_h = img_height
        self.num_of_tile_columns = num_of_tile_columns
        self.num_of_tile_rows = num_of_tile_rows
        self.num_of_tiles = num_of_tile_columns * num_of_tile_rows
        self.tile_dict = dict(zip(range(self.num_of_tiles), repeat(None)))
        self.empty_tile = None
        self.empty_tile_img = None
        self.swap_tile = None
        self.moveable_tiles = {}
        self.incorrect_tiles = 0
        self.swap_moves = 0
        
        
    def tile_up(self):
        """
        Create all of the individual tiles for the image, add them to the tile_dict
        """
        # calculate info about the tiles
        # note: we're creating a buffer between tiles of 5 pixels
        tile_width = (self.img_w / self.num_of_tile_columns) - 10
        tile_height = (self.img_h / self.num_of_tile_rows) - 10
        
        # load image into memory
        with Image.open(self.image_file) as img:
            img.load()
            # loop for creating tiles and adding them to the dictionary
            for i in range(self.num_of_tiles):
                index_col, index_row, x_pos, y_pos = self.get_x_and_y_from_index(i)
                tile_img = img.crop((x_pos, y_pos, x_pos + tile_width, y_pos + tile_height))
                tile_filename = f"images/tile_{i}.jpg"
                tile_img.save(tile_filename)
                self.tile_dict[i] = Tile(tile_filename, tile_width, tile_height, self.image_file, i, x_pos + 5, y_pos + 5)
   
                
    def get_x_and_y_from_index(self, index):
        """
        Get the x, y of the upper left corner of a tile by the index number
        
        Args:
            index (int): The index of the tile
        """
        index_col = index % self.num_of_tile_rows
        index_row = math.floor(index / self.num_of_tile_columns)
        x_pos = index_col * (self.img_w / self.num_of_tile_columns)
        y_pos = index_row  * (self.img_h / self.num_of_tile_rows)
        return index_col, index_row, x_pos, y_pos
    
    
    def pick_missing_tile(self):
        """
        This function randomly chooses a tile to be the 'missing' tile. This is required in order to allow the
        tiles to 'slide' around and be moved into an empty slot. One tile will be picked randomly and moved from
        the tile dict into a variable for the empty tile
        """
        # randomly pick a tile index
        missing_t = random.randint(0, self.num_of_tiles - 1)
        self.empty_tile = self.tile_dict[missing_t]
        self.empty_tile_img = self.tile_dict[missing_t].img
        self.tile_dict[missing_t].img = pygame.transform.scale(pygame.image.load('images/black_tile.jpg'), 
                                                               (self.tile_dict[missing_t].width, self.tile_dict[missing_t].height))
        
    
    def pick_moveable_tiles(self):
        """
        Determines which tiles are adjacent to the missing tile and adds them to the list. This will be used along
        with mouse button inputs to allow tiles to be swapped around
        """
        self.moveable_tiles = {'above': None, 'below': None, 'right': None, 'left': None}
        # determine if we're at an edge. If we are, constrain choices, otherwise add neighbors
        if self.empty_tile.cur_index > self.num_of_tile_columns - 1:
            # we're not in the first row. add the tile above us
            self.moveable_tiles['above'] = (self.tile_dict[self.empty_tile.cur_index - self.num_of_tile_columns])
        if self.empty_tile.cur_index < self.num_of_tiles - self.num_of_tile_columns:
            # we're not in the bottom row, add the tile below us
            self.moveable_tiles['below'] = (self.tile_dict[self.empty_tile.cur_index + self.num_of_tile_columns])
        if (self.empty_tile.cur_index + 1) % self.num_of_tile_columns != 0:
            # we're not on the right edge, add the tile to the right
            self.moveable_tiles['right'] = (self.tile_dict[self.empty_tile.cur_index + 1])
        if self.empty_tile.cur_index % self.num_of_tile_rows != 0:
            # we're not on the left edge, add the tile to the left
            self.moveable_tiles['left'] = (self.tile_dict[self.empty_tile.cur_index - 1])

            
    
    def swap_tiles(self, tile_to_swap_with_empty_tile, shuffling = False):
        """
        Moves a tile adjacent to the empty tile into the current position of the empty tile and moves
        the empty tile into the location of the swapping tile.

        Args:
            tile_to_swap_with_empty_tile (obj): A tile adjacent to the empty tile we want to swap
        """
        # if we're not shuffling, increment the move counter by 1
        # sound for tile swap if not shuffling
        if not shuffling:
            self.swap_moves += 1
            self.play_swap_tile_sound()
            
        # put the tile we're swapping into the temp variable if it is not None
        if tile_to_swap_with_empty_tile != None:
            self.swap_tile = tile_to_swap_with_empty_tile
        else:
            return
        # store the empty tile values to transfer to the swapping tile
        empty_tile_i = self.empty_tile.cur_index
        empty_tile_x = self.empty_tile.curX
        empty_tile_y = self.empty_tile.curY
        # move the empty tile into the new current index, update necessary attr 
        self.tile_dict[tile_to_swap_with_empty_tile.cur_index] = self.empty_tile
        self.empty_tile.cur_index = tile_to_swap_with_empty_tile.cur_index
        self.empty_tile.curX = tile_to_swap_with_empty_tile.curX
        self.empty_tile.curY = tile_to_swap_with_empty_tile.curY
        # move the swap tile into the former index of the empty tile, update necessary attr
        self.tile_dict[empty_tile_i] = self.swap_tile
        self.tile_dict[empty_tile_i].cur_index = empty_tile_i
        self.tile_dict[empty_tile_i].curX = empty_tile_x
        self.tile_dict[empty_tile_i].curY = empty_tile_y
        self.swap_tile = None           
        
    
    def shuffle_board(self):
        """
        Shuffles the board in order to make the puzzle fun to solve. This should only be called at the
        start of each level
        """
        # shuffle tiles until at least half of them are incorrect
        while True:
            self.num_of_incorrect_tiles() 
            self.pick_moveable_tiles()
            choice = random.choices(list(self.moveable_tiles.values()))
            if choice[0] != None:
                self.swap_tiles(choice[0], True)
                if self.incorrect_tiles >= self.num_of_tiles / 2:
                    # we're done shuffling this level, reset moves counter to 0
                    self.swap_moves = 0
                    break
                else:
                    self.shuffle_board()
                         
                
    def solved(self, show_tile):
        """
        Check to see if the puzzle is solved
        """
        for i in range(self.num_of_tiles):
            if self.tile_dict[i].cur_index != self.tile_dict[i].orig_index:
                return False
        if show_tile:
            self.empty_tile.img = self.empty_tile_img
        return True
    
    
    def num_of_incorrect_tiles(self):
        "Get # of incorrect tiles"
        self.incorrect_tiles = 0
        for i in range(self.num_of_tiles):
            if self.tile_dict[i].cur_index != self.tile_dict[i].orig_index:
                self.incorrect_tiles += 1
                
    
    def play_swap_tile_sound(self):
        "plays sound for swappping tiles"
        tile_swap_sound = mixer.Sound('sounds/tile_swap.mp3')
        tile_swap_sound.play()
        

class Tile():
    """
    Class for tile objects. These tiles will be some smaller subset of the art image the player is trying to
    recreate by putting the tiles back into their original (correct) position
    """
    
    def __init__(self, img, width, height, mother_image, index, origX, origY):
        self.img = pygame.image.load(img)
        self.img_file_name = img
        self.width = int(width)
        self.height = int(height)
        self.mother_image = mother_image
        self.orig_index = index
        self.cur_index = index
        self.origX = int(origX)
        self.origY = int(origY)
        self.curX = int(origX)
        self.curY = int(origY)
        self.mouse_highlight = False
      
        
    def highlight(self, mouse_X, mouse_Y):
        """
        Takes in and X and Y position (hopefully for the mouse). If the mouse is currently within the bounds of the
        tile object, set self.mouse_highlight to True. Otherwise, set to False

        Args:
            mouse_X (int): X position of the mouse cursor
            mouse_Y (int): Y position of the mouse cursor
        """
        self.mouse_highlight = False
        if mouse_X >= self.curX and mouse_X <= self.curX + self.width and mouse_Y >= self.curY and mouse_Y <= self.curY + self.height:
            # mouse is on this tile
            self.mouse_highlight = True
            
            
    def draw(self, display):
        """
        Draw tile

        Args:
            display (obj): Surface for tile to be drawn upon
        """
        display.blit(self.img, (self.curX, self.curY))
                
           
        
class DB():
    "database object to hold records for each level"
    def __init__(self):
        self.create_db()
        
    
    def create_db(self):
        try:
            # obj to connect to sqlite
            conn = sqlite3.connect('scores.db')
            
            # cursor obj
            cursor = conn.cursor()
            
            # create table
            table = """
            CREATE TABLE SCORES (
                Level INT UNIQUE,
                Best_Score INT UNIQUE,
                Worst_Score INT UNIQUE
                );
            """
            cursor.execute(table)
            
            for i in range(1, 1000):
                cursor.execute(f"INSERT INTO SCORES (Level) VALUES ({i})")
                
            # commit and close the connection
            conn.commit()
            conn.close()
        except:
            return
        
    
    def query_scores_for_level(self, lvl_num):
        "Return the best and worst completion scores for this level"
        # connection to sqlite, cursor
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        # query values for this level
        cursor.execute(f"SELECT * FROM SCORES WHERE Level = '{lvl_num}'")
        values = cursor.fetchall()
        conn.close()
        return values
    
    
    def replace_best(self, lvl_num, new_best_score):
        "insert a new value into Best_Score for this lvl"
        # connection to sqlite, cursor
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        # insert new value
        cursor.execute(f"UPDATE SCORES set Best_Score = {new_best_score} WHERE Level = {lvl_num}")
        conn.commit()
        new_values = cursor.execute(f"SELECT * FROM SCORES WHERE Level = {lvl_num}")
        conn.close()
        
    
    def replace_worst(self, lvl_num, new_worst_score):
        "insert a new value into Worst_Score for this lvl"
        # connection to sqlite, cursor
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        # insert new value
        cursor.execute(f"UPDATE SCORES set Worst_Score = {new_worst_score} WHERE Level = {lvl_num}")
        conn.commit()
        new_values = cursor.execute(f"SELECT * FROM SCORES WHERE Level = {lvl_num}")
        conn.close()