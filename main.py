import checkers
import pygame
import sys

def main():
    game = checkers.Game(loop_mode=True)
    game.run()

if __name__ == '__main__':
    main()