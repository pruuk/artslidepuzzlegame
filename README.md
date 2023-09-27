# The Art Slide Puzzle Game
#### Video Demo:

#### Requiremenmts:
    In order to run this program, you will need to install the following libraries:
        pygame
        pillow
        sqlite3

#### Description:
    This project was co-created by Calabe Davis and Malia Ambata as the final project for Harvard's
    CS50 Introduction to Computer Science Course. It is a simple game written in Python that allows
    the player to try to rearrange tiles to reform artworks back into their original tile positions.
    This is a clone of the classic slide puzzle games, written from scratch. The game engine used
    for the game is Pygame. 

    The game features five images of Malia Ambata's art. Three of the images are paintings and the
    remaining images are pictures of fired and hand painted clay sculpture busts. 
    
    Gameplay:
    1. The game randomly chooses one of the five images at the start of each level.
    2. The image is split into a number of tiles, starting with a 2 X 2 grid and increasing at later
       levels.
    3. A random tile is chosen to be 'empty' and the image is replaced with a plain background.
    4. The tiles are shuffled around until at least half of them are in an incorrect position
    5. The player then can click on tiles adjacent to the empty tile to swap them with the empty tile
    6. The level continues until the player rearranges the tiles into their original (correct)
       position.
    7. If the best or worst score are beat, it is stored in the scores DB
    8. A new level is spawned, with a new random art image (and a higher number of tiles)
    9. The game continues until the player gives up by closing the game window

    Game music and sounds were sourced from the following free websites:
        https://www.mixkit.co
        https://www.sounds-resource.com
        https://pixabay.com