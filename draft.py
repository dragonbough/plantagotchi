import pygame

pygame.init()

screen = pygame.display.set_mode((300, 300))
clock = pygame.time.Clock()

#initializes the clock and the game screen

running = True

player_pos =  pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2) #sets the player position to the middle of the screen

while running:
        pygame.display.flip() #update display (required to see changes made on the screen)
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False #checks through the events registered, if the game is quit pygame stops
        screen.fill("purple")
        pygame.draw.circle(screen, "red", player_pos, 40)
