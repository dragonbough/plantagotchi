import pygame
import os

pygame.init()

def return_frames_count(directory):
        return len(os.listdir(directory)) 

size = width, height = 300, 300
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

plant_folders = {"daisy":"daisy_frames"} # put plant names and their sprite folder in this dict

#plant class -- this contains the functionality that allows for animation
class Plant:
        def __init__(self, name, file_format=".png"):
                self.name = name
                self.file_format = file_format
                self.directory = f"sprites/{plant_folders[self.name]}/"
                self.frame = 1
                self.max_frame = return_frames_count(self.directory)
                self.sprite = pygame.image.load(self.directory + str(self.frame) + self.file_format).convert()
                self.size = (100, 100)
                pygame.transform.scale(self.sprite, self.size)
                self.rect = self.sprite.get_rect()
                
        def update_frame(self):
                if self.frame == self.max_frame:
                        self.frame = 1
                else:
                        self.frame += 1 
                self.sprite = pygame.image.load(self.directory + str(self.frame) + self.file_format).convert()
                screen.blit(self.sprite, self.rect)
                
running = True

current = Plant("daisy") #defining the current selected plant as a Plant object named "daisy"

while running:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False #
                
        #main rendering stuff goes here:
        screen.fill("purple")
        current.update_frame() #updates the current plant object's animation 
        pygame.display.flip() #update display (required to see changes made on the screen)
        
        clock.tick(10) #limits game to 5fps -- i need to keep the game at decent fps while also limiting fps of animation, how?
pygame.quit()
