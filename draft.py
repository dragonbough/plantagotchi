import pygame
import os
import pickle

pygame.init()

def return_frames_count(directory):
        return len(os.listdir(directory)) 
#returns number of frames/images in the sprite directory i assume


screen_size = screen_width, screen_height = 300, 300
screen = pygame.display.set_mode(screen_size)
screen_center = screen_width / 2, screen_height /2 
clock = pygame.time.Clock()


current_screen = None
visited_screens = [] 

#Sets screen and clock settings as well as an array of previous screens for backtracking

#this is a queue using the pygame Group structure that will be full of Sprites -- the queue can draw all the sprites at once and sprites can be removed/added at any time
class RenderQueue(pygame.sprite.Group):
        def __init__(self, *args):
                pygame.sprite.RenderUpdates.__init__(self, *args)

def switch_screen_to(screen):
        global current_screen, visited_screens
        for item in on_screen_sprites:
                item.kill()
        for item in on_screen_ui:
                item.kill()
        for item in on_screen_animations:
                item.kill()
        if screen == "prev":
                last_original_screens = [screen for screen in visited_screens if screen != visited_screens[len(visited_screens)-1]]
                current_screen = last_original_screens[len(last_original_screens)-1]
                visited_screens.pop()
        else:
                current_screen = screen 
                visited_screens.append(screen) 
        print(current_screen)
#Firstly, removes all sprites and UI elements. Then selects the last screen by excluding current screen and getting the last item
#if the screen isn't previous the screen is switched to the one described in the parameter and the current is added to the list

on_screen_sprites = RenderQueue()
on_screen_ui = RenderQueue()
on_screen_animations = RenderQueue()

#PLEASE DESCRIBE WHAT THIS DOES

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
                
        def set_image(self): #this just sets the current image of the sprite to whatever the current self.NAME is
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.name) + self.file_format).convert_alpha(), self.size)
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = self.position
                
        def update_frame(self): #this just shows the image of the sprite, does not use the animation functionality seen in AnimSprite
                self.set_image()
                self.group.remove([sprite for sprite in self.group if sprite.name == self.name])
                self.group.add(self)
        
        def set_position(self, position):
                self.position = position
                
# sprite class inherited from gamesprite class - this one overrides some methods and adds some attributes to allow for animation
class AnimSprite(GameSprite):
        def __init__(self, *args):
                super().__init__(*args)
                self.frame = 1
                self.playing = False
                
        def set_image(self): #this just sets the current image of the sprite to whatever the current self.FRAME (not self.name) is
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.frame) + self.file_format).convert_alpha(), self.size) #uses frames instead of name
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = self.position
                
        def update_frame(self): #updates the frame of the animated sprite and then adds it to the on_screen_sprites render queue
                max_frame = return_frames_count(self.directory) - 1 # -1 as we are not considering the image with the plain name
                self.set_image()
                self.group.remove([sprite for sprite in on_screen_sprites if sprite.name == self.name]) #only one of this plant can be on screen at a time
                self.group.add(self)
                if self.frame == max_frame:
                        self.frame = 1 
                        if self.playing == True:
                                self.playing = False #self.playing is only for animations that play once, recurring animations that don't change self.playing are fine
                        
                else:
                        self.frame += 1 
                                                
        def play(self): #functionality for playing single animations -- must be used in combination with the on_screen_animations codeblock in the game rendering
                self.playing = True
                self.update_frame()  
                
#on_screen_animations group, which handles single animations
waterAnim = AnimSprite("water_anim", (200, 200), (70, 40)) 
waterAnim.group = on_screen_animations 
quitAnim = AnimSprite("quit_anim", screen_size, (0, 0)) 
quitAnim.group = on_screen_animations 
                
class UIElement(GameSprite): 
        def __init__(self, *args):
                super().__init__(*args)
                self.group = on_screen_ui
                self.clickable = False
                
        #actions each UI element will do if perform() is called
        def perform(self):
                # honestly you're right this needs to be restructured, maybe we can just have a dict of every name to their function and call that, 
                # then we can define the functions ourselves?
                if self.name == "quit_button":
                        quitAnim.play() #.play() uses the self.playing functionality in AnimSprite so that the animation only plays once
                elif self.name == "plants_button":
                        switch_screen_to("plants")
                elif self.name == "back_button":
                        switch_screen_to("prev")
                elif self.name == "minigames_button":
                        switch_screen_to("minigames")
                elif self.name == "water_button":
                        waterAnim.play()
                elif self.name == "bonsai_select":
                        print("not yet")
                        return #just for testing reasons mb
                        #implementing the bonsai selection 
                        current = AnimSprite("bonsai", (200, 200), (70, 50))
                        switch_screen_to("prev")
                        #Sets the current sprite as the bonsai and would require the user to go back to the main screen to view it or i can set the screen back to main
                
current = AnimSprite("daisy", (200, 200), (70, 50)) #defining the current plant as a Plant object named "daisy"

bonsai_button = UIElement("bonsai_button", (80, 80), (150, 280)) #Defines the bonsai selction button, and sets the position as the middle top of the screen (There isn't a png yet)
bonsai_button.clickable = True

water_button = UIElement("water_button", (60, 60), (10, 10))
water_button.clickable = True

minigames_button = UIElement("minigames_button", (60, 60), (10, 70))
minigames_button.clickable = True

plants_button = UIElement("plants_button", (60,60), (10, 130))
plants_button.clickable = True


quit_button = UIElement("quit_button", (60, 60), (10, 230))
quit_button.clickable = True 

back_button = UIElement("back_button", (60, 60), (10, 230))
back_button.clickable = True


running = True

switch_screen_to("main")

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

        screen.fill("black") #background
        
        if current_screen == "main":
                current.update_frame() #updates the current plant object's animation and adds it to on_screen_sprites RenderQueue Group
                
                water_button.update_frame()
                minigames_button.update_frame()
                plants_button.update_frame()
                quit_button.update_frame()

        elif current_screen == "plants":
                back_button.update_frame()
                #maybe you want to add the bonsai_button.updateframe() here? you can select the bonsai on the "plants" screen
        else:
                back_button.update_frame() #every screen other than the main will have a back button              
        
        for anim in on_screen_animations: #all animations scheduled to be playing (added to the on_screen_animations Rendergroup) will play
                if anim.playing == True:
                        anim.update_frame()
                        print(anim.frame)
                else:
                        anim.kill()
                        if anim.name == "quit_anim":
                                pygame.quit()
                
        on_screen_sprites.draw(screen) #draws all objects in the on_screen_sprites group
        on_screen_ui.draw(screen)
        on_screen_animations.draw(screen)
        pygame.display.flip() #update display (required to see changes made on the screen)
        clock.tick(10) #limits game to 5fps -- i need to keep the game at decent fps while also limiting fps of animation, how?
        
pygame.quit()
