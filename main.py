import checkers
import pygame

def main():

    game = checkers.Game(loop_mode=True)
    game.setup()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    

if __name__ == '__main__':
    main()