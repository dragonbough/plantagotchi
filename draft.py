import pygame
import os
import pickle

pygame.init()

def return_frames_count(directory):
        return len(os.listdir(directory)) 

screen_size = screen_width, screen_height = 300, 300
screen = pygame.display.set_mode(screen_size)
screen_center = screen_width / 2, screen_height /2 
clock = pygame.time.Clock()
                
class RenderQueue(pygame.sprite.Group):
        def __init__(self, *args):
                pygame.sprite.RenderUpdates.__init__(self, *args)

on_screen = RenderQueue()

# --- plant class --- this contains the functionality that allows for animation
class GameSprite(pygame.sprite.Sprite):
        def __init__(self, name, size=(50, 50), position=(screen_center), file_format=".png"):
                pygame.sprite.Sprite.__init__(self)
                self.name = name
                self.file_format = file_format
                self.directory = f"sprites/{self.name}/"
                print(self.directory)
                self.size = size
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.name) + self.file_format).convert_alpha(), self.size)
                self.position = position
                self.rect = self.image.get_rect()
                self.rect.center = self.position
                
        def set_image(self):
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.name) + self.file_format).convert_alpha(), self.size)
                self.rect = self.image.get_rect()
                self.rect.center = self.position
                
        def update_frame(self):
                pass
                
class AnimSprite(GameSprite):
        def __init__(self, *args):
                super().__init__(*args)
                self.frame = 1
                
        def set_image(self):
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.frame) + self.file_format).convert_alpha(), self.size) #uses frames instead of name
                self.rect = self.image.get_rect()
                self.rect.center = self.position
                
        def update_frame(self):
                max_frame = return_frames_count(self.directory) - 1 # -1 as we are not considering the image with the plain name
                if self.frame == max_frame:
                        self.frame = 1
                else:
                        self.frame += 1 
                self.set_image()
                on_screen.remove([sprite for sprite in on_screen if sprite.name == self.name]) #only one of this plant can be on screen at a time
                on_screen.add(self)
                
                
class UIElement(GameSprite): 
        def __init__(self, name, size, position, file_format):
                self.directory = "sprites/ui"
                
                
current = AnimSprite("daisy", (150, 150)) #defining the current plant as a Plant object named "daisy"
running = True

while running:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False
                
        #main rendering stuff goes here:
        screen.fill("purple") #background
        current.update_frame() #updates the current plant object's animation and adds it to on_screen RenderQueue group
        on_screen.draw(screen) #draws all objects in the on_screen group 
        pygame.display.flip() #update display (required to see changes made on the screen)
        
        clock.tick(10) #limits game to 5fps -- i need to keep the game at decent fps while also limiting fps of animation, how?
pygame.quit()
