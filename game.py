import pygame
import os
import pickle
import sys
import random
import math

screen_size = screen_width, screen_height = 300, 300


def load():
        with open('save.pkl', 'rb') as f:
                try:
                        SaveDict = pickle.load(f)
                        #might change this to just return the entrie dictionary rather than splitting it
                        return SaveDict
                except:
                        SaveDict = {"bonsai": {"Cruelty": 0, "Bonding": 0}, "daisy": {"Cruelty": 0, "Bonding": 0}}
                        return SaveDict
def set_attribute(Plant, Att):
        try:
                return SaveDict[Plant][Att]
        except:
                return 0
        
def save(Plant, cruelty, bonding):
                try:
                        with open('save.pkl', 'wb') as f:
                                SaveDict[Plant]["Cruelty"] = SaveDict[Plant]["Cruelty"] + cruelty
                                SaveDict[Plant]["Bonding"] = SaveDict[Plant]["Cruelty"] + bonding
                                pickle.dump(SaveDict, f)
                except:
                        print("Error in save")
                        return 0
                        
                                
                                
                
SaveDict = load()
xp = 0


        
#SCREEN POSITION STUFF? I DON'T KNOW IF I LIKE THIS

# window_x = 1920 - screen_width - 50
# window_y = 1080 - screen_height - 50 #factoring in taskbar height

# os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (window_x, window_y)

pygame.init()


screen = pygame.display.set_mode(screen_size) #pygame.NOFRAME?
pygame.display.set_caption("plantagotchi") #setting window text
pygame.display.set_icon(pygame.image.load("sprites/plantagotchi_icon.png")) #setting icon for the game
screen_center = screen_width / 2, screen_height /2 
screen_colour = "black" 
screen_mode = "dark"
clock = pygame.time.Clock()
game_fps = 60
delta = 1

current_screen = None
visited_screens = [] 

#returns number of frames/images in the sprite directory
def return_frames_count(directory):
        return len(os.listdir(directory)) 

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
        for item in on_screen_text:
                item.kill()
        #if switching to the previous screen, it will remove the screen you're on from the visited_screens list and then switch to the last one
        if screen == "prev":
                visited_screens.pop()
                current_screen = visited_screens[len(visited_screens)-1]
        else:
                current_screen = screen 
                visited_screens.append(screen) 
#Removes all game objects from previous screen before changing current_screen

#Queue using the pygame Group structure that will be full of Sprites -- the queue can draw all the sprites at once and sprites can be removed/added at any time
class RenderQueue(pygame.sprite.Group):
        def __init__(self, *args):
                pygame.sprite.RenderUpdates.__init__(self, *args)

cursors = RenderQueue()
on_screen_sprites = RenderQueue()
on_screen_ui = RenderQueue()
on_screen_animations = RenderQueue()
on_screen_clones = RenderQueue()
on_screen_text = RenderQueue()

def clear_screen():
        on_screen_sprites.empty()
        on_screen_ui.empty()
        on_screen_animations.empty()
        on_screen_clones.empty()
        on_screen_text.empty()

class GameObject():
        def __init__(self, name, size=(50, 50), position=screen_center):
                self.name = name
                self.size = self.width, self.height = size[0], size[1]
                self.position = self.position_x, self.position_y = position[0], position[1]
                self.rect = pygame.Rect(self.position, self.size)
                
        def set_position(self, position, center=False):
                if center == False:
                        self.position = position
                        self.position_x = self.position[0]
                        self.position_y = self.position[1]
                else:
                        self.rect.center = position
                        self.position = self.position_x, self.position_y = self.rect.x, self.rect.y
        
        def move(self, index, collision=True):
                #im cheating here, im moving the image rectangle by the index, clamping it to the size of the screen, and then setting the position to its new position
                self.rect.move_ip(index) 
                if collision == True:
                        self.rect.clamp_ip(screen.get_rect())
                self.position_x = self.rect.x
                self.position_y = self.rect.y 
                self.position = self.position_x, self.position_y
        
        def resize(self, size=(50, 50)):
                self.size = size[0], size[1]
                
class Text(GameObject, pygame.sprite.Sprite):
        def __init__(self, name, font_size=15, colour="white", text="NULL", position=(screen_center)):
                default_font_path = "fonts/Tamagotchi/TamagotchiNormal.ttf"
                self.text = text 
                self.font = pygame.font.Font(default_font_path, font_size)
                self.size = self.font.size(self.text)
                self.colour = colour
                self.background = screen_colour
                self.group = on_screen_text
                self.static = False
                super().__init__(name, self.size, position)
                pygame.sprite.Sprite.__init__(self)
                
        def set_text(self, new_text):
                self.text = new_text
                self.size = self.font.size(self.text)
                self.rect = pygame.Rect(self.position, self.size)
        
        def set_font(self, font, size):
                if font == "pygame_default":
                        self.font = pygame.font.Font(None, size)
                try:
                        font_path = pygame.font.match_font(font)
                except:
                        print("Invalid font")
                self.font = pygame.font.Font(font_path, size)
        
        def update_frame(self):
                #if the text is staying static, it wont need to update any frame -- as long as its in its RenderClass currently it'll just return
                if self.static == True: 
                        if self in self.group:
                                return
                self.image = self.font.render(self.text, True, self.colour, self.background)
                self.rect.x, self.rect.y = self.position_x, self.position_y
                self.group.add(self)
        
        def set_bg_colour(self, colour):
                if colour == "transparent":
                        self.background = None
                else:
                        self.background = colour
                
                
# generic gamesprite class which allows for the display of an element anywhere on screen 
class GameSprite(GameObject, pygame.sprite.Sprite):
        def __init__(self, name, size=(50, 50), position=screen_center, clone=False, angle=0):
                super().__init__(name, size, position) 
                pygame.sprite.Sprite.__init__(self)
                self.file_format = ".png"
                self.directory = f"sprites/{self.name}/"
                self.cached_image = pygame.image.load(self.directory + str(self.name) + self.file_format).convert_alpha() #preloads image
                self.angle = angle
                self.image = pygame.transform.rotate(pygame.transform.scale(self.cached_image, self.size), self.angle)#sets the image to the preloaded image
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = self.position                
                self.group = on_screen_sprites
                self.clone = clone
                self.cloneid = None
                if self.clone == True:
                        self.cloneid = 0
                self.mask = pygame.mask.from_surface(self.image)
                self.flip_x = False
                self.flip_y = False
                
        def set_rotation(self, angle=0):
                self.angle = angle       
                
        def rotate_by(self, angle=0):
                self.angle += angle
                if self.angle >= 360:
                        self.angle -= 360
                        
        def set_flip(self, flip_x=False, flip_y=False):
                self.flip_x, self.flip_y = flip_x, flip_y  
                self.set_image()
                self.mask = pygame.mask.from_surface(self.image)      
                
        def set_image(self): #this just sets the current image of the sprite to the right size 
                self.image = pygame.transform.flip(pygame.transform.rotate(pygame.transform.scale(self.cached_image, self.size), self.angle), self.flip_x, self.flip_y)
                self.rect.x, self.rect.y = self.position
                
        def update_frame(self): #this just shows the image of the sprite, does not use the animation functionality seen in AnimSprite
                self.set_image()
                if self.clone == False:
                        self.group.remove([sprite for sprite in self.group if sprite.name == self.name])
                else:
                        self.cloneid = len([sprite for sprite in self.group if sprite.name == self.name])
                self.group.add(self)
                
# sprite class inherited from gamesprite class - this one overrides some methods and adds some attributes to allow for animation
class AnimSprite(GameSprite, pygame.sprite.Sprite):
        def __init__(self, name, size=(50, 50), position=screen_center, fps=10, cruelty=0, bonding=0):
                super().__init__(name, size, position)
                self.__cruelty = cruelty
                self.__bonding = bonding
                self.frame = 1
                self.max_frame = return_frames_count(self.directory) - 1 # -1 as we are not considering the image with the plain name
                self.playing = False
                self.fps = 1000 / fps
                self.previous_time = 0
                self.cached_images = {}
                for i in range(self.max_frame):
                        self.cached_images[i+1] = pygame.image.load(self.directory + str(i+1) + self.file_format).convert_alpha()
                #creates a cache of all the frames in the animation, adding them to a dictionary of item corresponding to image
        def access_cruelty(self):
                return self.__cruelty

        def access_bonding(self):
                return self.__bonding

        def update_cruelty(self, value):
                self.__cruelty = self.__cruelty + value

        def update_bonding(self, value):
                self.__bonding = self.__bonding + value
                
        def set_image(self): #this just sets the current image of the sprite to whatever the current frame is in the dictionary
                self.image = pygame.transform.scale(self.cached_images[self.frame], self.size)
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = self.position
                
        def update_frame(self, static=False, frame=1): #updates the frame of the animated sprite and then adds it to the on_screen_sprites render queue
                if not static:
                        self.set_image()
                        self.group.remove([sprite for sprite in on_screen_sprites if sprite.name == self.name]) #only one of this plant can be on screen at a time
                        self.group.add(self)
                        #fps manager
                        current_time = pygame.time.get_ticks()  # Get the current time
                        if current_time - self.previous_time >= self.fps: #checks if time between previous update and current time is more than the fps -- if so, updates
                                self.previous_time = current_time #updates time of previous update 
                                if self.frame == self.max_frame:
                                        self.frame = 1 
                                        if self.playing == True:
                                                self.playing = False #self.playing is only for animations that play once, recurring animations that don't change self.playing are fine
                                        
                                else:
                                        self.frame += 1
                else:
                        self.frame = frame
                        self.set_image()
                        self.group.remove([sprite for sprite in self.group if sprite.name == self.name])
                        self.group.add(self)
                                                
        def play(self): #functionality for playing single animations -- must be used in combination with the on_screen_animations codeblock in the game rendering
                self.frame = self.max_frame
                self.update_frame()
                self.playing = True
                
        
                
#class plant(AnimSprite):
        #def __init__(self, cruelty, bonding, *args): ##honestly just for readability and so its easier to understand, replace args with each parameter from animsprite
                #self.__cruelty = cruelty
                #self.__bonding = bonding 
                #super.__init__(*args) #and pass in, explicitly, the parameters explicitly into super()
        #def access_cruelty(self):
                #return self.__cruelty

        #def access_bonding(self):
               # return self.__bonding

        #def update_cruelty(self, value):
               # self.__cruelty = self.__cruelty + value

       # def update_bonding(self, value):
               # self.__bonding = self.__bonding + value

#when creating an instance of this class please specify the cruelty and bonding using cruelty=value so that you don't overwrite inherited attributes or use the function further up for
#assigning attributes using data from the save file
                
class UIElement(GameSprite): 
        def __init__(self, name, size=(50, 50), position=screen_center):
                super().__init__(name, size, position)
                self.group = on_screen_ui
                self.clickable = False
                self.toggled = False
                
        def toggle(self, toggle_element):
                self.toggled = not self.toggled
                toggle_element.toggled = not toggle_element.toggled

        #actions each UI element will do if perform() is called
        def perform(self):
                global current_plant

                if self.name == "quit_button":
                        global show_cursor
                        save(current_plant.name, current_pant.access_cruelty(), xp)
                        show_cursor = False
                        quitAnim.play() #.play() uses the self.playing functionality in AnimSprite so that the animation only plays once
                        
                elif self.name == "plants_button":
                        switch_screen_to("plants")
                        
                elif self.name == "settings_button":
                        switch_screen_to("settings")
                        
                elif self.name == "back_button":
                        switch_screen_to("prev")
                
                elif self.name == "home_button":
                        switch_screen_to("main")
                        
                elif self.name == "minigames_button":
                        switch_screen_to("minigames")
                        
                elif self.name == "minigames_play_button":
                        if self.cloneid == None:
                                countdownAnim.play()
                                switch_screen_to("basket_game")
                        elif self.cloneid == 1:
                                countdownAnim.play()
                                switch_screen_to("baseball_game")
                        
                elif self.name == "water_button":
                        global xp
                        xp += 2
                        if waterAnim.playing == False:
                                pygame.mixer.Sound.play(watering_sound)
                                waterAnim.play()
                        
                elif self.name == "bonsai":
                        #implementing the bonsai selection 
                        save(current_plant.name, current_plant.access_cruelty(), xp)
                        current_plant = bonsai
                        switch_screen_to("prev")
                        
                elif self.name == "daisy":
                        save(current_plant.name, current_plant.access_cruelty(), xp)
                        current_plant = daisy
                        switch_screen_to("prev")
                        #Sets the current_plant sprite as the bonsai and would require the user to go back to the main screen to view it
                        #or i can set the screen back to main
                        
                elif self.name == "music_on":
                        self.toggle(music_off)
                elif self.name == "music_off":
                        self.toggle(music_on)
                        
                elif self.name == "light_mode":
                        self.toggle(dark_mode)
                elif self.name == "dark_mode":
                        self.toggle(light_mode)
           
          
     
#SPRITES #################################################################

daisy = AnimSprite("daisy", (200, 200), (70, 50), cruelty=set_attribute("Daisy_Dict", "Cruelty"), bonding=set_attribute("Daisy_Dict", "Bonding")) 
bonsai = AnimSprite("bonsai", (200, 200), (70, 50), cruelty=set_attribute("Bonsai_Dict", "Cruelty"), bonding=set_attribute("Bonsai_Dict", "Bonding"))

current_plant = daisy

minigames_basket = GameSprite("minigames_basket", (100, 100), current_plant.position)

minigames_bat = GameSprite("baseball_bat", (140, 140), current_plant.position)


#ANIMATIONS ###############################################################

waterAnim = AnimSprite("water_anim", (200, 200), (70, 40), 30) 
waterAnim.group = on_screen_animations 

quitAnim = AnimSprite("quit_anim", screen_size, (0, 0), 10) 
quitAnim.group = on_screen_animations 

countdownAnim = AnimSprite("countdown_anim", screen_size, (0, 0), 1)
countdownAnim.group = on_screen_animations


#SOUNDS ##################################################################
ball_sound = pygame.mixer.Sound("sounds/ball/ball.wav")
game_over_sound = pygame.mixer.Sound("sounds/game_over/game_over.wav")
glove_sound = pygame.mixer.Sound("sounds/glove/glove.wav")
life_lost_sound = pygame.mixer.Sound("sounds/life_lost/life_lost.wav")
pop_sound = pygame.mixer.Sound("sounds/pop/pop.wav")
watering_sound = pygame.mixer.Sound("sounds/watering/watering.wav")

pygame.mixer.music.load('sounds/bg_music/bg_music.mp3')

#BUTTONS ##################################################################

bonsai_button = UIElement("bonsai", (80, 80), (150, 280)) #Defines the bonsai selction button, and sets the position as the middle top of the screen (There isn't a png yet)
bonsai_button.clickable = True

daisy_button = UIElement("daisy", (80, 80), (150, 280))
daisy_button.clickable = True

water_button = UIElement("water_button", (60, 60), (10, 10))
water_button.clickable = True

minigames_button = UIElement("minigames_button", (60, 60), (10, 70))
minigames_button.clickable = True

minigames_play_button = UIElement("minigames_play_button", (60, 60))
minigames_play_button.clickable = True

minigames_play_button2 = UIElement("minigames_play_button", (60, 60))
minigames_play_button2.clickable = True
minigames_play_button2.clone = True

minigames_basket_button = UIElement("minigames_basket_button", (60, 60))
minigames_basket_button.clickable = False

minigames_baseball_button = UIElement("minigames_baseball_button", (60, 60) )
minigames_baseball_button.clickable = False

plants_button = UIElement("plants_button", (60,60), (10, 130))
plants_button.clickable = True

settings_button = UIElement("settings_button", (50, 50), (240, 235))
settings_button.clickable = True 

dark_mode = UIElement("dark_mode", (60,60), (150, 170))
dark_mode.clickable = True
dark_mode.toggled = True #by default, game starts in dark mode

light_mode = UIElement("light_mode", (60, 60),(150, 170))
light_mode.clickable = True

music_on = UIElement("music_on", (60, 60),(150, 100))
music_on.clickable = True

music_off = UIElement("music_off", (60, 60),(150, 100))
music_off.clickable = True
music_off.toggled = True #by default, game starts with music

quit_button = UIElement("quit_button", (60, 60), (10, 230))
quit_button.clickable = True 

back_button = UIElement("back_button", (60, 60), (10, 230))
back_button.clickable = True

home_button = UIElement("home_button", (60, 60), (10, 230))
home_button.clickable = True


#TEXT ######################################################################

plant_name = Text("plant_name", 20, "white", current_plant.name, (current_plant.position_x - 20, current_plant.position_y + 20))
plant_name.static = True
plant_name.set_bg_colour("transparent")

score_screen_text = Text("score_screen_text", 10, "white", "achieved a score of:", screen_center)
score_screen_text.static = True
score_screen_text.set_position(screen_center, True)

debug_text = Text("debug_text", 20, "green", "DEBUG MODE TRUE", (165, 10))
debug_text.static = True
debug_text.set_bg_colour("black")
debug_text.set_font("pygame_default", 20)

fps_counter = Text("fps_counter", 20, "green", "FPS: 0", (237.5, 22.5))
fps_counter.set_bg_colour("black")
fps_counter.set_font("pygame_default", 20)

#OTHER #####################################################################

cursor = GameSprite("cursor", (30, 30))
cursor.group = cursors
on_hover_cursor = GameSprite("on_hover_cursor", (30, 30))
on_hover_cursor.group = cursors

############################################################################

last_second = 0
mouse_reset_time = 1000 #1000 ms -- 1 second

running = True
debug_mode = False

pygame.mouse.set_visible(False) #hide real cursor
show_cursor = True #show custom cursor

switch_screen_to("main")


music = True


# MAIN GAME LOOP ###########################################################

while running:
        
        if music == True:
                pygame.mixer.music.play(-1)
        else:
                pygame.mixer.music.stop()
        
        # CURSOR #####################################################
        
        hovering = []
        
        # functionality to hide mouse after a second of inactivity 
        if pygame.mouse.get_rel() == (0, 0):
                mouse_reset_time -= clock.get_time()
                if mouse_reset_time < 0:
                        show_cursor = False
        else:
                mouse_reset_time = 3000 #time before cursor disappears when idle, in milliseconds
                show_cursor = True 
                      
        pygame.mouse.get_rel()
        
        if pygame.mouse.get_focused():
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for element in on_screen_ui:
                        if element.clickable:
                                element_x, element_y = element.position
                                element_width, element_height = element.size
                                if element_x <= mouse_x <= element_x + element_width and element_y <= mouse_y <= element_y + element_height:
                                        hovering.append(True)
        
                mouse_pos = mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_offset = mouse_offset_x, mouse_offset_y = 3, 10
                if not hovering:
                        on_hover_cursor.kill()
                        cursor.set_position((mouse_x+mouse_offset_x, mouse_y+mouse_offset_y), True)
                        cursor.update_frame()
                elif hovering:
                        cursor.kill()
                        on_hover_cursor.set_position((mouse_x+mouse_offset_x, mouse_y+mouse_offset_y), True)
                        on_hover_cursor.update_frame()
        else:
                cursors.empty()
        
        # EVENTS ###################################################
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
                
                if event.type == pygame.KEYUP:
                        if event.key == pygame.K_F7:
                                debug_mode = not debug_mode
                                if debug_mode == False:
                                        debug_text.kill()
                                        fps_counter.kill()
                
                if current_screen == "baseball_game":
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                minigames_bat.set_flip(not minigames_bat.flip_x, False)
        
        #SCREEN APPEARANCE ##########################################
        
        if screen_mode == "dark":
                screen_colour = "black"
        elif screen_mode == "light":
                screen_colour = "#a8dea0"
                
        screen.fill(screen_colour) 
        
        # MAIN #######################################################
        
        if current_screen == "main":
                
                current_plant.resize((235, 235))
                current_plant.set_position((30, 60))
                current_plant.update_frame() #updates the current_plant plant object's animation and adds it to on_screen_sprites RenderQueue Group
                
                waterAnim.resize((current_plant.width, current_plant.height))
                waterAnim.set_position((current_plant.position_x+22.5, current_plant.position_y+21))
                
                if waterAnim in on_screen_animations or quitAnim in on_screen_animations:
                        on_screen_sprites.empty()
                        on_screen_clones.empty()
                        on_screen_text.empty()
                        on_screen_ui.empty()
                        cursors.empty()
                else:
                        plant_name = Text("plant_name", 20, "white", current_plant.name)
                        plant_name.set_position((current_plant.position_x + 132.5, current_plant.position_y-10), True)
                        plant_name.update_frame()
                
                water_button.update_frame()
                minigames_button.update_frame()
                plants_button.update_frame()
                settings_button.update_frame()
                quit_button.update_frame()

        elif current_screen == "plants":
                # PLANT SELECTION FUNCTIONALITY HERE
                back_button.set_position((10, 230))
                back_button.update_frame()
                bonsai_button.set_position((70, 10))
                bonsai_button.update_frame()
                #maybe you want to add the bonsai_button.update_frame() here?
                daisy_button.set_position((10, 30))
                daisy_button.update_frame()
        
        # MINIGAME SELECT SCREEN #############################################
                
        elif current_screen == "minigames":
                current_plant.resize((200, 200))
                current_plant.set_position((100, 50))
                current_plant.update_frame() 
                
                #BASKET MINIGAME BUTTON
                minigames_play_button.set_position((10, 10))
                minigames_basket_button.set_position((64, 10))
                minigames_play_button.update_frame()
                minigames_basket_button.update_frame()
                
                #BASEBALL MINIGAME BUTTON
                minigames_play_button2.set_position((10, 70))
                minigames_baseball_button.set_position((64, 70))
                minigames_play_button2.update_frame()
                minigames_baseball_button.update_frame()
                
                back_button.set_position((10, 230))
                back_button.update_frame()
                
                previous_time = 0 #needed by all the minigames for some calculations (spawn interval)
                
        # BASKET MINIGAME #############################################
                
        elif current_screen == "basket_game":
                if countdownAnim in on_screen_animations: #while countdown is playing, we can prepare for the game to start
                        start = False
                        current_plant.resize((95, 95))
                        current_plant.set_position((50, 200))
                        minigames_basket.set_position((current_plant.position_x, current_plant.position_y - 60))
                        score = 0
                        score_text = Text("score", 30, "white", str(score), (20, 10))
                        score_text.set_bg_colour("transparent")
                        missed = 5
                        missed_text = Text("missed", 30, "red", f"Remaining misses: {missed}", (265, 10))
                        missed_text.set_bg_colour("transparent")
                        previous_time_anim = 0
                        
                        cursors.empty()
                        back_button.kill()
        
                else:
                        start = True
                        back_button.update_frame()
                        
                          
                if start == True and missed > 0:
                        
                        score_text.set_text(str(score))
                        score_text.update_frame()
                        missed_text.set_text(str(missed))
                        missed_text.update_frame()
                        minigames_basket.update_frame()
                        current_plant.update_frame()
                        
                        #multiplying this quantity by delta means that the speed stays consistent between fps -- delta is the time between frames
                        #this now means player_speed pixels per SECOND instead of pixels per FRAME
                        speed_multiplier = 1 + (0.005 * score) 
                        player_speed = 200 * speed_multiplier * delta 
                        starting_spawn_interval = 1 #starting interval at which fruit are spawned 
                        gradient = 0.03 #speed at which spawn interval decreases
                        spawn_interval = (starting_spawn_interval) / (1 + (gradient * score))
                        #this makes the spawn interval of the fruit decrease as the user's score increases
                        
                        #checks for letter A or left arrow keyboard press, and moves left
                        if pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_LEFT]:
                                current_plant.move((-player_speed,0))
                                minigames_basket.set_position((current_plant.position_x, current_plant.position_y - 60))
                        #checks for letter D or right arrow keyboard press, and moves left
                        if pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_RIGHT]:
                                current_plant.move((player_speed, 0))
                                minigames_basket.set_position((current_plant.position_x, current_plant.position_y - 60))
                                
                        #spawns falling fruit in random position every spawn_interval seconds
                        falling_fruit = GameSprite(random.choice(["orange", "banana", "grape"]), (50, 50), (random.randrange(0, screen_width), 0))
                        falling_fruit.group = on_screen_clones
                        current_time = pygame.time.get_ticks() 
                        #the spawn interval is converted into milliseconds
                        if current_time - previous_time  > (spawn_interval * 1000):
                                previous_time = current_time
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
                                                score += 1
                                                colliding.kill()
                                                pygame.mixer.Sound.play(pop_sound)

                                        
                                        if sprite.position_y > 240: #if clone touches bottom of screen, kill it and increment missed score by 1
                                                missed -= 1
                                                sprite.kill()
                                                pygame.mixer.Sound.play(life_lost_sound)

                                        
                                        if missed < 1: #if missed score gets above limit, quit game
                                                on_screen_clones.empty()
                                                switch_screen_to("score")
                                                pygame.mixer.Sound.play(game_over_sound)

                                        sprite.move((0, 3)) #inch each clone down
                                        
                                        if sprite in on_screen_clones: #if sprites have not been killed, update their frames
                                                sprite.update_frame()
                                         #displays the clone
                                         
        # BASEBALL MINIGAME #############################################################
        
        elif current_screen == "baseball_game":
                if countdownAnim in on_screen_animations:
                        start = False
                        current_plant.resize((200, 200))
                        current_plant.set_position((-50, 100))
                        minigames_bat.group = cursors
                        previous_mouse_pos = previous_mouse_x, previous_mouse_y = (0, 0) 
                        time_stationary = 0
                        ball_velocity = ball_velocity_x, ball_velocity_y = (0, 0)
                        velocity_dict = {}
                        hit = []
                        score = 0 
                        missed = 0
                        
                        score_text = Text("score", 30, "white", str(score), (210, 10))
                        score_text.set_bg_colour("transparent")
                        missed = 5
                        missed_text = Text("missed", 30, "red", f"Remaining misses: {missed}", (265, 10))
                        missed_text.set_bg_colour("transparent")
                        
                        baseball_glove_static = GameSprite("baseball_glove", (75, 75))
                        baseball_glove_anim = AnimSprite("baseball_glove", (75, 75), screen_center, 5) 
                        
                        previous_time_anim = 0   
                        current_time_anim = 0
                        spawn = True   
                        caught = False 
                        
                        off_screen = []
                        
                        cursors.empty()                                 
                        
                else:
                        start = True 
                        back_button.update_frame()
                        
                if start == True:
                        
                        mouse_pos = mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        minigames_bat.set_position((mouse_x-70, mouse_y-70)) #updates position of baseball bat according to mouse position
                        
                        current_plant.update_frame()
                        
                        mouse_reset_time = 1000000 #stops the mouse from resetting
                        cursor.kill() #stops the normal game cursor from displaying
                        
                        score_text.set_text(str(score))
                        score_text.update_frame()
                        missed_text.set_text(str(missed))
                        missed_text.update_frame()
                        
                        #when hovering over the back button the baseball bat disappears
                        if not hovering: 
                                minigames_bat.update_frame()
                        else:
                                minigames_bat.kill()
                                
                        mouse_x_threshold = 200        
                        
                        if mouse_x > mouse_x_threshold:
                                pygame.mouse.set_pos((mouse_x_threshold, mouse_y))
                                
                        current_time = pygame.time.get_ticks()
                        
                        if previous_mouse_pos != mouse_pos:
                                time_stationary = 0
                                mouse_x_velocity = (mouse_x - previous_mouse_x) / delta
                                mouse_y_velocity = (mouse_y - previous_mouse_y) / delta

                        else:
                                time_stationary += 1 * delta
                                if time_stationary > 50:
                                        mouse_x_velocity, mouse_y_velocity = (0, 0)                 
                        
                        previous_mouse_pos = previous_mouse_x, previous_mouse_y = mouse_pos                                                
                        previous_time_distance = current_time
                                
                        spawn_interval = 1.5 #seconds
                        
                        #spawns baseball every spawn interval
                        if current_time - previous_time  > (spawn_interval * 1000):
                                        print("time", current_time, previous_time, current_time-previous_time)
                                        previous_time = current_time
                                        
                                        baseball = GameSprite("baseball", (50, 50), screen_center, True)
                                        baseball.group = on_screen_clones

                                        ball_velocity = ball_velocity_x, ball_velocity_y = (-5, random.randrange(1, 3))
                                        velocity_dict[len(velocity_dict)] = ball_velocity

                                        baseball.set_position((300, random.randrange(30, 160)))
                                        baseball.update_frame()                        

                                        
                        #simulates collision for each ball colliding with bat and applies a velocity onto it's key in velocity_dict based on the velocity of the mouse
                        for baseball in on_screen_clones:
                                colliding = pygame.sprite.spritecollideany(minigames_bat, on_screen_clones, pygame.sprite.collide_mask)
                                if colliding == baseball and mouse_x_velocity == abs(mouse_x_velocity):
                                        if baseball.cloneid not in hit:
                                                velocity_magnitude = math.sqrt(mouse_x_velocity**2 + mouse_y_velocity**2)
                                                print(f"magnitude of hit: {velocity_magnitude}")        
                                                if velocity_magnitude > 100:
                                                        
                                                        pygame.mixer.Sound.play(ball_sound)
                                                        restitution = 0.005
                                                        hit_velocity_x = ball_velocity_x * mouse_x_velocity * restitution 
                                                        
                                                        if ball_velocity_y == 0:
                                                                hit_velocity_y = mouse_y_velocity * restitution 
                                                        else:
                                                                hit_velocity_y = mouse_y_velocity * ball_velocity_y * restitution 
                                                        
                                                        if hit_velocity_x == 0:
                                                                hit_velocity_x = -1
                                                        
                                                        velocity_dict[baseball.cloneid] = (-hit_velocity_x, hit_velocity_y)
                                                        if baseball.cloneid not in hit:
                                                                hit.append(baseball.cloneid) #signal this baseball has been hit
                                                        print(f"ball velocity = {velocity_dict[baseball.cloneid]} mouse velocity = {mouse_x_velocity, mouse_y_velocity}")
                                
                                colliding_glove = pygame.sprite.spritecollideany(baseball_glove_static, on_screen_clones, pygame.sprite.collide_mask)
                                if colliding_glove == baseball and baseball.cloneid in hit:
                                        score_gradient = 0.1
                                        score_velocity_x, score_velocity_y = velocity_dict[baseball.cloneid]
                                        score_magnitude = math.sqrt(score_velocity_x**2 + score_velocity_y**2)
                                        if score_magnitude < 1:
                                                score_magnitude = 1
                                        score += round(score_magnitude * score_gradient)
                                        
                                        baseball_glove_anim.set_position(baseball_glove_static.position)
                                        baseball_glove_static.kill()
                                        pygame.mixer.Sound.play(glove_sound)
                                        caught = True
                                        spawn = True
                                        
                                        baseball.kill()
                                
                                if baseball.rect not in screen.get_rect() and baseball.position_x < (screen_width - baseball.width) and baseball.cloneid not in hit: 
                                        if baseball.cloneid not in off_screen:
                                                off_screen.append(baseball.cloneid)
                                                missed -= 1
                                                pygame.mixer.Sound.play(life_lost_sound)
                                
                                #moves each clone by their respective velocity within velocity dict
                                baseball.move(velocity_dict[baseball.cloneid], False)
                        
                        
                        anim_interval = 1
                        
                        
                        if caught == True:
                                
                                current_time_anim += clock.get_time()
                        
                                if (current_time_anim - previous_time_anim) > (anim_interval * 1000):
                                        baseball_glove_anim.kill()
                                        previous_time_anim = current_time_anim
                                        caught = False
                                else:
                                        baseball_glove_anim.update_frame(static=True, frame=2)
                                
                        
                        if spawn == True:
                                print ("SPAWNED GLOVE")
                                previous_glove_pos_y = baseball_glove_static.position[1]
                                while abs(previous_glove_pos_y - baseball_glove_static.position_y) < 20:
                                        baseball_glove_static.set_position((220, random.randrange(15, 225)))
                                spawn = False
                        
                        if baseball_glove_anim not in on_screen_sprites:
                                baseball_glove_static.update_frame()
                                
                        
                        on_screen_clones.draw(screen)
                        
                        
                        back_button.set_position((10, 10))
                        back_button.update_frame()
                        
                        if missed <= 0:
                                pygame.mixer.Sound.play(game_over_sound)
                                clear_screen()
                                baseball_glove_anim.kill()
                                baseball_glove_static.kill()
                                minigames_bat.kill()
                                cursors.add(cursor)
                                switch_screen_to("score")
                        

        # SCORE SCREEN ###############################################################
        
        elif current_screen == "score":
                #layout for each element on screen
                current_plant.resize((40, 40))
                current_plant.set_position((screen_center[0], screen_center[1] - 80), True)
                current_plant.update_frame()
                plant_name.set_position((screen_center[0], screen_center[1] - 40), True)
                plant_name.update_frame()
                score_screen_text.update_frame()
                score_text.resize((80, 80))
                score_text.set_position((screen_center[0], screen_center[1] + 40), True)
                score_text.update_frame()
                home_button.set_position((screen_center[0], screen_center[1] + 95), True)
                home_button.update_frame()
                        
        #####################################################################################
        
        #SETTINGS ###########################################################################
        
        elif current_screen == "settings":
                
                print(f"music:{music}")
                
                if music_on.toggled == True and music_off.toggled == False:
                        music = False
                        music_on.kill()
                        music_off.update_frame()
                        
                elif music_off.toggled == True and music_on.toggled == False:
                        music = True
                        music_off.kill()
                        music_on.update_frame()
                
                
                if light_mode.toggled == True and dark_mode.toggled == False: #if light mode is currently toggled
                        screen_mode = "light"
                        light_mode.kill()
                        dark_mode.update_frame()
                        
                elif dark_mode.toggled == True and light_mode.toggled == False: #if dark mode is currently toggled
                        screen_mode = "dark"
                        dark_mode.kill()
                        light_mode.update_frame()
                        
                back_button.set_position((10, 230))
                back_button.update_frame()
        else:
                back_button.update_frame() #every screen other than the main will have a back button              
        
        
        ####################################################################################
        
        for anim in on_screen_animations: #all animations scheduled to be playing (added to the on_screen_animations Rendergroup) will play
                if anim.playing == True:
                        anim.update_frame()
                else:
                        anim.kill()
                        if anim.name == "quit_anim":
                                pygame.quit()
                                sys.exit()
                
        #RENDERING GROUPS ###################################################
        
        if debug_mode == True:
                i = 0
                for sprite in on_screen_ui:
                        pygame.draw.rect(screen, (i, i+100, i), sprite.rect) #each ui element collider is shown in green
                        i+= 30
                for sprite in on_screen_sprites:
                         pygame.draw.rect(screen, (i+100, i, i), sprite.rect) #each sprite element collider is shown in red
                for sprite in on_screen_clones:
                        pygame.draw.rect(screen, (i, i, i+100), sprite.rect) #each ui element collider is shown in blue
                for sprite in on_screen_animations:
                        pygame.draw.rect(screen, (i+100, i+100, i), sprite.rect)
                for sprite in on_screen_text:
                        if sprite.name != "debug_text" and sprite.name != "fps_counter":
                                pygame.draw.rect(screen, (i, i+100, i+100), sprite.rect)
        
        on_screen_clones.draw(screen)
        on_screen_sprites.draw(screen) #draws all objects in the on_screen_sprites group
        on_screen_ui.draw(screen)
        on_screen_animations.draw(screen)
        on_screen_text.draw(screen)
        if show_cursor == True:
                cursors.draw(screen)
                
        pygame.display.flip() #update display (required to see changes made on the screen)
        
        #FRAME UPDATE #####################################################
        
        delta = clock.tick(game_fps) / 1000
                
        #DEBUG STUFF ########################################################
        
        if debug_mode == True:
                debug_text.update_frame()
                fps = round(clock.get_fps(), 1)
                fps_counter.set_text(f"FPS:{fps}")
                fps_counter.update_frame() 
                
                #fps counter for testing reasons that only updates if the fps changes
        
pygame.quit()
