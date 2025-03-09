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
        
current_screen = None

def switch_screen(screen):
        global current_screen
        current_screen = screen        
        
class RenderQueue(pygame.sprite.Group):
        def __init__(self, *args):
                pygame.sprite.RenderUpdates.__init__(self, *args)

on_screen_sprites = RenderQueue()
on_screen_ui = RenderQueue()

# generic gamesprite class which allows for the display of an element anywhere on screen 
class GameSprite(pygame.sprite.Sprite):
        def __init__(self, name, size=(50, 50), position=(screen_center), file_format=".png"):
                pygame.sprite.Sprite.__init__(self)
                self.name = name
                self.file_format = file_format
                self.directory = f"sprites/{self.name}/"
                self.size = size
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.name) + self.file_format).convert_alpha(), self.size)
                self.position = position
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = self.position                
                self.group = on_screen_sprites
                
        def set_image(self):
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.name) + self.file_format).convert_alpha(), self.size)
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = self.position
                
        def update_frame(self):
                self.set_image()
                self.group.remove([sprite for sprite in self.group if sprite.name == self.name])
                self.group.add(self)
                
# sprite class inherited from gamesprite class - this one overrides some methods and adds some attributes to allow for animation
class AnimSprite(GameSprite):
        def __init__(self, *args):
                super().__init__(*args)
                self.frame = 1
                
        def set_image(self):
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.frame) + self.file_format).convert_alpha(), self.size) #uses frames instead of name
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = self.position
                
        def update_frame(self):
                max_frame = return_frames_count(self.directory) - 1 # -1 as we are not considering the image with the plain name
                if self.frame == max_frame:
                        self.frame = 1
                else:
                        self.frame += 1 
                self.set_image()
                self.group.remove([sprite for sprite in on_screen_sprites if sprite.name == self.name]) #only one of this plant can be on screen at a time
                self.group.add(self)
                
                
class UIElement(GameSprite): 
        def __init__(self, *args):
                super().__init__(*args)
                self.group = on_screen_ui
                self.clickable = False
        #actions each element will do once clicked
        def perform(self):
                if self.name == "quit_button":
                        pygame.quit()
                elif self.name == "plants_button":
                        switch_screen("plants")
                else:
                        print (self.name)
                        
                
current = AnimSprite("daisy", (150, 150)) #defining the current plant as a Plant object named "daisy"


quit_button = UIElement("quit_button", (50, 50), (10, 10))
quit_button.clickable = True 

plants_button = UIElement("plants_button", (50, 50), (10, 180))
plants_button.clickable = True

water_button = UIElement("water_button", (50, 50), (10, 230))
water_button.clickable = True


running = True

while running:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False
                
                #if the mouse button is clicked, for every element currently on screen, 
                # if the mouse is over the element and the element is clickable, the element's action is performed
                if event.type == pygame.MOUSEBUTTONDOWN: 
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        for element in on_screen_ui:
                                if element.clickable:
                                        element_x, element_y = element.position
                                        element_width, element_height = element.size
                                        if element_x <= mouse_x <= element_x + element_width and element_y <= mouse_y <= element_y + element_height:
                                                element.perform()
        
        
        #main rendering stuff goes here:
        
        switch_screen("main")
        
        screen.fill("black") #background
        if current_screen == "main":
                current.update_frame() #updates the current plant object's animation and adds it to on_screen_sprites RenderQueue group
                quit_button.update_frame()
                water_button.update_frame()
                plants_button.update_frame()
        
        on_screen_sprites.draw(screen) #draws all objects in the on_screen_sprites group
        on_screen_ui.draw(screen)
        pygame.display.flip() #update display (required to see changes made on the screen)
        clock.tick(10) #limits game to 5fps -- i need to keep the game at decent fps while also limiting fps of animation, how?
        
pygame.quit()
