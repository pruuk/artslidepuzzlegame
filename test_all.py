" Tests related to game objects and functions"

from objects import Game, Tile, Board, Images
import random

## GAME OBJECT TESTS
def test_game_object_creation() -> None:
    "Create a game object. Verify it exists and has correct initial attributes"
    game = Game()
    assert (game.lvl_num == 1 and
            game.running == True and
            game.win == False)


# def test_game_spawn_new_level_func() -> None:
#     "Create a new level. This is also a good test of ccreating a Level object"
#     game = Game()
#     # patching in a win on level 1 by swapping tiles until we have a win
#     while not game.win:
#         # swap an adjacent tile with the empty one
#         choice = random.choice(list(game.level.board.moveable_tiles.values()))
#         # note that we're telling the func we're shuffling in order to prevent calling the swap board sound
#         game.level.board.swap_tiles(choice, True)
#     assert game.lvl_num == 2



## BOARD AND TILE OBJECT TESTS
def test_board_creation() -> None:
    "Test to create board object"
    # create a board object to run tests on
    board = Board(image_file= random.choice(Images), 
                      img_width = 1920,
                      img_height = 1080, 
                      num_of_tile_columns = 5, 
                      num_of_tile_rows = 5)
    assert (board.img_w == 1920 and
        board.img_h == 1080 and
        board.num_of_tile_columns == 5 and
        board.num_of_tile_rows == 5 and
        len(board.tile_dict) == 25 and
        board.num_of_tiles == 25)
    
    
def test_tile_creation() -> None:
    "Test first tile is created in board's tile dict"
    # create a board object to run tests on
    board = Board(image_file= random.choice(Images), 
                      img_width = 1920,
                      img_height = 1080, 
                      num_of_tile_columns = 5, 
                      num_of_tile_rows = 5)
    # run function to create tiles for the board
    board.tile_up()
    assert (board.tile_dict[0].mother_image == board.image_file and
            board.tile_dict[0].width == (board.img_w / board.num_of_tile_rows) - 10 and
            board.tile_dict[0].height == (board.img_h / board.num_of_tile_columns) - 10 and
            board.tile_dict[0].orig_index == 0 and
            board.tile_dict[0].origX == 5 and
            board.tile_dict[0].origY == 5)
    

def test_board_xy_from_index_func() -> None:
    "Check to see if index func works correctly"
    # create a board object to run tests on
    board = Board(image_file= random.choice(Images), 
                      img_width = 1920,
                      img_height = 1080, 
                      num_of_tile_columns = 5, 
                      num_of_tile_rows = 5)
    # get values to test for index 0
    index_col_a, index_row_a, x_pos_a, y_pos_a = board.get_x_and_y_from_index(0)
    # get values to test for index 24
    index_col_z, index_row_z, x_pos_z, y_pos_z = board.get_x_and_y_from_index(24)
    assert (index_col_a == 0 and
            index_row_a == 0 and
            x_pos_a == 0.0 and
            y_pos_a == 0.0 and
            index_col_z == 4 and
            index_row_z == 4 and
            x_pos_z == 1536.0 and
            y_pos_z == 864.0)
    

def test_board_pick_missing_tile_func() -> None:
    "Ensure we picked a missing file"
    # create a board object to run tests on
    board = Board(image_file= random.choice(Images), 
                      img_width = 1920,
                      img_height = 1080, 
                      num_of_tile_columns = 5, 
                      num_of_tile_rows = 5)
    # run function to create tiles for the board
    board.tile_up()
    # run function to pick missing tile
    board.pick_missing_tile()
    assert board.empty_tile in board.tile_dict.values()
    

def test_board_pick_moveable_tiles_func() -> None:
    "Ensure we don't give an out of index tile"
    # create a board object to run tests on
    board = Board(image_file= random.choice(Images), 
                      img_width = 1920,
                      img_height = 1080, 
                      num_of_tile_columns = 5, 
                      num_of_tile_rows = 5)
    # run function to create tiles for the board
    board.tile_up()
    # run function to pick missing tile
    board.pick_missing_tile()
    # run func to determine moveable tiles
    board.pick_moveable_tiles()
    assert (len(board.moveable_tiles) != 0 and
            board.empty_tile not in board.moveable_tiles)
    

def test_board_swap_tiles_func() -> None:
    "Ensure tiles are in a new position after swap"
    # create a board object to run tests on
    board = Board(image_file= random.choice(Images), 
                      img_width = 1920,
                      img_height = 1080, 
                      num_of_tile_columns = 5, 
                      num_of_tile_rows = 5)
    # run function to create tiles for the board
    board.tile_up()
    # run function to pick missing tile
    board.pick_missing_tile()
    # run func to determine moveable tiles
    board.pick_moveable_tiles()
    # swap an adjacent tile with the empty one
    choice = None
    while choice == None:
        choice = random.choice(list(board.moveable_tiles.values()))
    # note that we're telling the func we're shuffling in order to prevent calling the swap board sound
    board.swap_tiles(choice, True)
    assert board.empty_tile.orig_index == choice.cur_index
    

def test_board_shuffle_board_func() -> None:
    "Ensure the board got shuffled"
    # create a board object to run tests on
    board = Board(image_file= random.choice(Images), 
                      img_width = 1920,
                      img_height = 1080, 
                      num_of_tile_columns = 5, 
                      num_of_tile_rows = 5)
    # run function to create tiles for the board
    board.tile_up()
    # run function to pick missing tile
    board.pick_missing_tile()
    # run func to determine moveable tiles
    board.pick_moveable_tiles()
    # shuffle the board to prepare it for the player
    board.shuffle_board()
    solved = board.solved(False)
    assert solved == False
    

def test_board_solved_func() -> None:
    "Ensure we correctly identify when the board is solved, if it is solved"
    # create a board object to run tests on
    board = Board(image_file= random.choice(Images), 
                      img_width = 1920,
                      img_height = 1080, 
                      num_of_tile_columns = 5, 
                      num_of_tile_rows = 5)
    # run function to create tiles for the board
    board.tile_up()
    # run function to pick missing tile
    board.pick_missing_tile()
    # run the solved function on the newly created tiles
    assert board.solved(True) == True
    
    
def test_num_of_incorrect_tiles_func() -> None:
    "Ensure we're getting a good count on the number of incorrect tiles"
    # create a board object to run tests on
    board = Board(image_file= random.choice(Images), 
                      img_width = 1920,
                      img_height = 1080, 
                      num_of_tile_columns = 5, 
                      num_of_tile_rows = 5)
    # run function to create tiles for the board
    board.tile_up()
    # run function to pick missing tile
    board.pick_missing_tile()
    # run func to determine moveable tiles
    board.pick_moveable_tiles()
    # swap an adjacent tile with the empty one
    choice = random.choice(list(board.moveable_tiles.values()))
    # note that we're telling the func we're shuffling in order to prevent calling the swap board sound
    board.swap_tiles(choice, True)
    # we've only done one swap, so we should only have 2 incorrect tiles
    board.num_of_incorrect_tiles()
    assert board.incorrect_tiles == 2

