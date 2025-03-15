import pygame
import os
import pickle
import sys
import random

pygame.init()

def return_frames_count(directory):
        return len(os.listdir(directory)) 
#returns number of frames/images in the sprite directory i assume


screen_size = screen_width, screen_height = 300, 300
screen = pygame.display.set_mode(screen_size)
screen_center = screen_width / 2, screen_height /2 
clock = pygame.time.Clock()
prev_fps = []


current_screen = None
visited_screens = [] 

#Sets screen and clock settings as well as an array of previous screens for backtracking

def switch_screen_to(screen):
        global current_screen, visited_screens
        for item in on_screen_sprites:
                item.kill()
        for item in on_screen_ui:
                item.kill()
        for item in on_screen_animations:
                if item.name != "countdown_anim":
                        item.kill()
        for item in on_screen_clones:
                item.kill()
        current_screen = screen 
        visited_screens.append(screen) 
        print(current_screen)
#Firstly, removes all sprites and UI elements. Then selects the last screen by excluding current screen and getting the last item
#if the screen isn't previous the screen is switched to the one described in the parameter and the current is added to the list

#this is a queue using the pygame Group structure that will be full of Sprites -- the queue can draw all the sprites at once and sprites can be removed/added at any time
class RenderQueue(pygame.sprite.Group):
        def __init__(self, *args):
                pygame.sprite.RenderUpdates.__init__(self, *args)

on_screen_sprites = RenderQueue()
on_screen_ui = RenderQueue()
on_screen_animations = RenderQueue()
on_screen_clones = RenderQueue()

#PLEASE DESCRIBE WHAT THIS DOES

# generic gamesprite class which allows for the display of an element anywhere on screen 
class GameSprite(pygame.sprite.Sprite):
        def __init__(self, name, size=(50, 50), position=screen_center, file_format=".png"):
                pygame.sprite.Sprite.__init__(self)
                self.name = name
                self.file_format = file_format
                self.directory = f"sprites/{self.name}/"
                self.width = size[0]
                self.height = size[1]
                self.size = self.width, self.height
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.name) + self.file_format).convert_alpha(), self.size)
                self.position_x = position[0]
                self.position_y = position[1]
                self.position = self.position_x, self.position_y 
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = self.position                
                self.group = on_screen_sprites
                self.clone = False
                self.mask = pygame.mask.from_surface(self.image)
                
        def resize(self, new_width, new_height):
                self.size = new_width, new_height
                
        def set_image(self): #this just sets the current image of the sprite to whatever the current self.NAME is
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.name) + self.file_format).convert_alpha(), self.size)
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = self.position
                
        def update_frame(self): #this just shows the image of the sprite, does not use the animation functionality seen in AnimSprite
                self.set_image()
                if self.clone == False:
                        self.group.remove([sprite for sprite in self.group if sprite.name == self.name])
                self.group.add(self)
        
        def set_position(self, position):
                self.position = position
                self.position_x = self.position[0]
                self.position_y = self.position[1]
        
        def move(self, index):
                #im cheating here, im moving the image rectangle by the index, clamping it to the size of the screen, and then setting the position to its new position
                self.rect.move_ip(index) 
                self.rect.clamp_ip(screen.get_rect())
                self.position_x = self.rect.x
                self.position_y = self.rect.y 
                self.position = self.position_x, self.position_y
                
# sprite class inherited from gamesprite class - this one overrides some methods and adds some attributes to allow for animation
class AnimSprite(GameSprite):
        def __init__(self, *args):
                super().__init__(*args)
                self.frame = 1
                self.max_frame = return_frames_count(self.directory) - 1 # -1 as we are not considering the image with the plain name
                self.playing = False
                
        def set_image(self): #this just sets the current image of the sprite to whatever the current self.FRAME (not self.name) is
                self.image = pygame.transform.scale(pygame.image.load(self.directory + str(self.frame) + self.file_format).convert_alpha(), self.size) #uses frames instead of name
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = self.position
                
        def update_frame(self): #updates the frame of the animated sprite and then adds it to the on_screen_sprites render queue
                self.set_image()
                self.group.remove([sprite for sprite in on_screen_sprites if sprite.name == self.name]) #only one of this plant can be on screen at a time
                self.group.add(self)
                if self.frame == self.max_frame:
                        self.frame = 1 
                        if self.playing == True:
                                self.playing = False #self.playing is only for animations that play once, recurring animations that don't change self.playing are fine
                        
                else:
                        self.frame += 1 
                                                
        def play(self): #functionality for playing single animations -- must be used in combination with the on_screen_animations codeblock in the game rendering
                self.frame = self.max_frame
                self.update_frame()
                self.playing = True
                
                
#class plant(AnimSprite):
        #def __init__(self, cruelty, bonding, *args): ##surely this is needed so that we don't overwrite attributes with value of cruelty and bonding
                #self.__cruelty = cruelty
                #self.__bonding = bonding 
                #super.__init__(*args)
        #def access_cruelty(self):
                #return self.__cruelty

        #def access_bonding(self):
                #return self.__bonding

        #def update_cruelty(self, value):
                #self.__cruelty = self.__cruelty + value

        #def update_bonding(self, value):
                #self.__bonding = self.__bonding + value

        #def set_image(self):
                
                
#on_screen_animations group, which handles single animations
waterAnim = AnimSprite("water_anim", (200, 200), (70, 40)) 
waterAnim.group = on_screen_animations 
quitAnim = AnimSprite("quit_anim", screen_size, (0, 0)) 
quitAnim.group = on_screen_animations 
countdownAnim = AnimSprite("countdown_anim", screen_size, (0, 0))
countdownAnim.group = on_screen_animations
                
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
                        switch_screen_to("main")
                elif self.name == "minigames_button":
                        switch_screen_to("minigames")
                elif self.name == "minigames_play_button":
                        countdownAnim.play()
                        switch_screen_to("basket_game")
                elif self.name == "water_button":
                        waterAnim.play()
                elif self.name == "bonsai_select":
                        print("not yet")
                        #implementing the bonsai selection 
                        current_plant = AnimSprite("bonsai", (200, 200), (70, 50))
                        switch_screen_to("prev")
                        #Sets the current_plant sprite as the bonsai and would require the user to go back to the main screen to view it or i can set the screen back to main
                
current_plant = AnimSprite("daisy", (200, 200), (70, 50)) #defining the current_plant plant as a Plant object named "daisy"

minigames_basket = GameSprite("minigames_basket", (100, 100), current_plant.position)


# bonsai_button = UIElement("bonsai_button", (80, 80), (150, 280)) #Defines the bonsai selction button, and sets the position as the middle top of the screen (There isn't a png yet)
# bonsai_button.clickable = True
#just commenting it out for testing reasons mb

water_button = UIElement("water_button", (60, 60), (10, 10))
water_button.clickable = True

minigames_button = UIElement("minigames_button", (60, 60), (10, 70))
minigames_button.clickable = True

minigames_play_button = UIElement("minigames_play_button", (60, 60))
minigames_play_button.clickable = True

minigames_basket_button = UIElement("minigames_basket_button", (60, 60))
minigames_basket_button.clickable = False

plants_button = UIElement("plants_button", (60,60), (10, 130))
plants_button.clickable = True


quit_button = UIElement("quit_button", (60, 60), (10, 230))
quit_button.clickable = True 

back_button = UIElement("back_button", (60, 60), (10, 230))
back_button.clickable = True

last_second = 0

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
                current_plant.resize(200, 200)
                current_plant.set_position((70, 50))
                current_plant.update_frame() #updates the current_plant plant object's animation and adds it to on_screen_sprites RenderQueue Group
                
                water_button.update_frame()
                minigames_button.update_frame()
                plants_button.update_frame()
                quit_button.update_frame()

        elif current_screen == "plants":
                back_button.update_frame()
                #maybe you want to add the bonsai_button.updateframe() here? you can select the bonsai on the "plants" screen
                
        elif current_screen == "minigames":
                minigames_play_button.set_position((10, 10))
                minigames_basket_button.set_position((64, 10))
                minigames_play_button.update_frame()
                minigames_basket_button.update_frame()
                back_button.update_frame()
                start = False
                #setting the position of the plant in advance of entering the game
                current_plant.resize(95, 95)
                current_plant.set_position((50, 200))
                minigames_basket.set_position((current_plant.position_x, current_plant.position_y - 60))
                #####
                score = 0
                missed = 0
                
        elif current_screen == "basket_game":
                if countdownAnim not in on_screen_animations: #if countdown stops playing, we can start, and show the back button
                        start = True
                        back_button.update_frame()
                else:
                        back_button.kill()
                if start == True:
                        minigames_basket.update_frame()
                        current_plant.update_frame()
                        #checks for letter A or left arrow keyboard press, and moves left
                        if pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_LEFT]:
                                current_plant.move((-3,0))
                                minigames_basket.set_position((current_plant.position_x, current_plant.position_y - 60))
                        #checks for letter D or right arrow keyboard press, and moves left
                        if pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_RIGHT]:
                                current_plant.move((3, 0))
                                minigames_basket.set_position((current_plant.position_x, current_plant.position_y - 60))
                                
                        #spawns falling fruit in random position every two seconds, as a clone
                        falling_fruit = GameSprite(random.choice(["orange", "banana", "grape"]), (50, 50), (random.randrange(0, screen_width), 0))
                        falling_fruit.group = on_screen_clones
                        seconds = round(pygame.time.get_ticks() / 1000)
                        if seconds % 1 == 0:
                                if seconds != last_second:
                                        last_second = seconds
                                        fruit = random.choice(["orange", "grape", "banana"]) #fruit is a random selection of these sprites
                                        size = (40, 40)
                                        #different size allocations for different fruit, if not, size is size default above
                                        if fruit == "grape":
                                                size = (20, 20)
                                        elif fruit == "orange":
                                                size = (40, 40)
                                        falling_fruit = GameSprite(fruit, size, (random.randrange(0, screen_width-50), 0)) #creates falling_fruit sprite at random width across screen
                                        falling_fruit.group = on_screen_clones #adding to clone group
                                        falling_fruit.clone = True #defining as a clone
                                        falling_fruit.update_frame() 
                        
                        #iterates over every clone on screen, and checks if its colliding with the mask of the basket (meaning the actual coloured pixels, not transparent part)
                        for sprite in on_screen_clones:
                                        # initial = sprite.position
                                        colliding = pygame.sprite.spritecollideany(minigames_basket, on_screen_clones, pygame.sprite.collide_mask)
                                        if colliding: #if clone is colliding with minigames_basket, kill it and increment score by 1
                                                print("Caught!", colliding.name)
                                                score += 1
                                                print(score)
                                                colliding.kill()
                                        
                                        if sprite.position_y > 240: #if clone touches bottom of screen, kill it and increment missed score by 1
                                                print("Missed!", sprite.name)
                                                missed += 1
                                                sprite.kill()
                                        
                                        if missed > 5: #if missed score gets above limit, quit game
                                                print("Failed")
                                                on_screen_clones.empty()
                                                switch_screen_to("minigames")
                                                
                                        sprite.move((0, 3)) #inch each clone down
                                        
                                        if sprite in on_screen_clones: #if sprites have not been killed, update their frames
                                                sprite.update_frame()
                                        
                        on_screen_clones.draw(screen) #displays the clone

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
                                sys.exit()
                
        on_screen_sprites.draw(screen) #draws all objects in the on_screen_sprites group
        on_screen_ui.draw(screen)
        on_screen_animations.draw(screen)
        pygame.display.flip() #update display (required to see changes made on the screen)
        if current_screen == "basket_game":
                clock.tick(30)
        else:
                clock.tick(10) #limits game to 5fps -- i need to keep the game at decent fps while also limiting fps of animation, how?
        if countdownAnim in on_screen_animations:
                clock.tick(1)
                
        fps = round(clock.get_fps(), 1)
        if prev_fps:
                if prev_fps[len(prev_fps)-1] == fps:
                        prev_fps.pop()
                else:
                        print(f"{fps}FPS")
        prev_fps.append(round(clock.get_fps(), 1)) 
        #fps counter for testing reasons that only updates if the fps changes
        
pygame.quit()
