"""
Main file for the Tile game built by Calabe Davis & Malia Ambata for the CS50 Intro to CS final project.

This game will use a series of images, breaking them into N number of tiles, and shuffling the tiles around
with one tile ommitted. The player will need to shuffle the tiles back into order to reform the image to pass
any given level.

This game will be using 5 images of art produced by Malia Ambata. In some cases, the images will be altered
to provide additional levels.    
"""
# imports
import time
from objects import Level, Game

    
def main():
    """
    Main game function to control the others
    """
    # create game object
    game = Game()
    # start inifinite loop
    while game.running:
        if game.win:
            game.spawn_new_level()
            
        game.running, game.win = game.level.game_loop(game.running)
    
    
     
if __name__ == "__main__":
    print("starting game")
    main()