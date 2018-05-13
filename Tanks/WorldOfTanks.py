# -*- coding: utf-8 -*-
from pygame import transform
from pygame.sprite import Sprite
from time import time
from pygame.locals import *
import pygame,random,os,fileinput,time
pygame.init()
pygame.mixer.init()

smallfont = pygame.font.Font((os.path.join("Resources","prstart.ttf")),25)
medfont = pygame.font.Font((os.path.join("Resources","prstart.ttf")),50)
largefont = pygame.font.Font((os.path.join("Resources","prstart.ttf")),80)


display_width=800
display_height=600
SCREEN_SIZE = [display_width,display_height]
BLACK = (0,0,0)
YELLOW = (155,155,0)
GREEN = (0,155,0)
RED = (155,0,0)
WHITE = (255,255,255)
LIGHT_GREEN = (0,255,0)
LIGHT_YELLOW = (255,255,0)
LIGHT_RED = (255,0,0)

LAST_LEVEL = 3
SPRITE_PLAYER1 = os.path.join("Resources","player1.png")
SPRITE_PLAYER2 = os.path.join("Resources","player2.png")
SPRITE_ENEMY = os.path.join("Resources","enemy.png")
SPRITE_EXPLOSION1 = os.path.join("Resources","explosion1.png")
SPRITE_EXPLOSION2 = os.path.join("Resources","explosion2.png")
SPRITE_BLOCK = os.path.join("Resources","block.png")
SPRITE_BLOCKS = os.path.join("Resources","blocks.png")
SPRITE_BULLET = os.path.join("Resources","bullet.png")

SOUND_SHOT = os.path.join("Resources","fire.ogg")
SOUND_EXPLOSION = os.path.join("Resources","explosion.wav")
SOUND_GAMESTART = os.path.join("Resources","gamestart.ogg")
SOUND_GAMEOVER = os.path.join("Resources","gameover.ogg")
SOUND_INTRO = os.path.join("Resources","music_wake_68_glytch_funk_remix.wav")
SOUND_GAME = os.path.join("Resources","music_broke_for_free_caught_in_the_beat_remix.wav")

FONT = os.path.join("Resources","prstart.ttf")

ENEMIES = 3
KILL_GOAL = 10

EXPLOSION2 = (
(0, 0, 20, 20),
(20, 0, 20, 20),
(40, 0, 20, 20),
(60, 0, 20, 20),
(80, 0, 20, 20),
(100, 0, 20, 20),
(120, 0, 20, 20),
)

EXPLOSION1 = (
(0, 0, 62, 62),
(62, 0, 62, 62),
(124, 0, 62, 62),
(186, 0, 62, 62),
(0, 62, 62, 62),
(62, 62, 62, 62),
(124, 62, 62, 62),
(186, 62, 62, 62),
(0, 124, 62, 62),
(62, 124, 62, 62),
(124, 124, 62, 62),
(186, 124, 62, 62),
(0, 186, 62, 62),
(62, 186, 62, 62),
(124, 186, 62, 62),
(186, 186, 62, 62),
)

class Direction:
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class Tank(Sprite):
    def __init__(self,screen, img_filename,speed,pos):
        Sprite.__init__(self)
        self.screen = screen
        self.speed = speed
        self.image = pygame.image.load(img_filename)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.bullets = pygame.sprite.Group()
        self.bullet_time = 0
        self.direction = Direction.UP
        self.alive=True
        
    def shot(self,speed):
        ##oddanie strzału
        pos = []
        if self.direction == Direction.UP:
            pos.append(self.rect.centerx)
            pos.append(self.rect.centery-self.rect.height/2)
        
        elif self.direction == Direction.RIGHT:
            pos.append(self.rect.centerx + self.rect.width/2)
            pos.append(self.rect.centery)
        elif self.direction == Direction.DOWN:
            pos.append(self.rect.centerx)
            pos.append(self.rect.centery + self.rect.height/2)
        else:
            pos.append(self.rect.centerx - self.rect.width/2)
            pos.append(self.rect.centery)
        self.bullets.add(Bullet(self.screen,speed,pos,self.direction))
            
    def collision_detect(self,sprite):
        return pygame.sprite.collide_rect(self,sprite)
    
    def rotate(self,direct):
        """ Obracanie tanka wedlug wzoru:
            0 - 0 stopni
            1 - 90 stopni
            2 - 180 stopni
            3 - 270 stopni
        """
        if self.direction != direct:
            self.image = transform.rotate(self.image,(self.direction-direct)*90)
            self.direction = direct
class PlayerTank(Tank):
    INIT_COORDS = [20.0,580.0]
    def __init__(self,screen,img_filename,speed,shot_sound):
        Tank.__init__(self,screen,img_filename,speed,PlayerTank.INIT_COORDS)
        self.shot_sound = shot_sound
        self.area = screen.get_rect()
        
    def update(self,time_passed,move,enemy,Map):
        """ Ruszanie spritem"""
        self.rect.centerx += move[0]*self.speed
        self.rect.centery += move[1]*self.speed
        """ Kolizja z przeciwnikiem"""
        if pygame.sprite.spritecollideany(self,enemy):
            self.rect.centerx -= move[0]*self.speed
            self.rect.centery -= move[1]*self.speed
        """ Kolizja z mapa """
        if Map.isCollideWithMap(self.rect):
            self.rect.centerx -= move[0]*self.speed
            self.rect.centery -= move[1]*self.speed
        """Poza ekranem"""
        if self.rect.left < 0 or self.rect.right > self.area.right:
            self.rect.centerx -= move[0]*self.speed
        if self.rect.top < 0 or self.rect.bottom > self.area.bottom:
            self.rect.centery -= move[1]*self.speed
        """obracanie tanka"""
        if move[0] > 0:
            self.rotate(Direction.RIGHT)
        elif move[0]<0:
            self.rotate(Direction.LEFT)
        elif move[1]>0:
            self.rotate(Direction.DOWN)
        elif move[1]<0:
            self.rotate(Direction.UP)
        """Naboje - update"""
        self.bullet_time -=time_passed
        self.bullets.update()
        self.bullets.draw(self.screen)
        
    def shot(self):
        if self.bullet_time > 0:
            return
        else:
            self.bullet_time = 200
        self.shot_sound.play()
        Tank.shot(self,self.speed+10)
    
class EnemyTank(Tank):
    def __init__(self,screen,img_filename,speed,pos):
        Tank.__init__(self,screen,img_filename,speed,pos)
        self.area = screen.get_rect()
        self.distance = 0
    def update(self,time_passed,tanks,Map):
        if self.distance <=0:
            self.distance = random.randrange(200)
            self.rotate(random.randrange(4))
        else:
            self.distance -= self.speed
        
        move = [0,0]
        if self.direction == Direction.UP:
           move[1] -= 1
        elif self.direction == Direction.RIGHT:
            move[0] += 1
        elif self.direction == Direction.DOWN:
            move[1] += 1
        else:
            move[0] -= 1
        """wykonaj ruch:"""
        self.rect.centerx += self.speed * move[0]
        self.rect.centery += self.speed * move[1]
        """kolizja z innymi tankami"""
        tanks.remove(self)
        if pygame.sprite.spritecollideany(self,tanks):
            self.rect.centerx -=move[0]*self.speed
            self.rect.centery -=move[1]*self.speed
            self.distance = 0
        tanks.add(self)
        """kolizja z mapa"""
        if Map.isCollideWithMap(self.rect):
            self.rect.centerx -=move[0]*self.speed
            self.rect.centery -=move[1]*self.speed
            self.distance = 0
        """poza ekranem"""
        if self.rect.left < 0 or self.rect.right >= self.area.right:
            self.rect.centerx -= move[0]*self.speed
            self.distance = 0
        if self.rect.top <0 or self.rect.bottom >= self.area.bottom:
            self.rect.centery -=move[1]*self.speed
            self.distance = 0
        """Naboje - update"""
        self.bullet_time -= time_passed
        self.bullets.update()
        self.bullets.draw(self.screen)
        """strzal"""
        self.shot()
    def shot(self):
        if self.bullet_time >0:
            return
        else:
            self.bullet_time = random.randrange(200,2000)
        Tank.shot(self,self.speed+1)
class Bullet(Sprite):
    def __init__(self,screen,speed,pos,direction):
        Sprite.__init__(self)
        self.screen = screen
        self.area = screen.get_rect()
        self.speed = speed
        
        self.direction = direction
        self.image = pygame.image.load(SPRITE_BULLET)
        
        self.rect = self.image.get_rect()
        self.rect.center = pos
        
    def update(self):
        
        if self.direction == 0:
            self.rect.centery -= self.speed
        elif self.direction == 1:
            self.rect.centerx += self.speed
        elif self.direction == 2:
            self.rect.centery += self.speed
        else:
            self.rect.centerx -= self.speed
    
        if self.rect.centerx <0 or self.rect.centerx > self.area.right or self.rect.centery<0 or self.rect.centery > self.area.bottom:
            self.kill();

class Explosion(Sprite):
    
    def __init__ (self,image,screen,rect,sound,tiles = EXPLOSION2, fps=10):
        Sprite.__init__(self)
        self.screen = screen
        self.frame = 0
        self.delay = 1000/fps
        self.time = 0
        self.tiles = tiles
        self.image = pygame.image.load(image)
        self.area = pygame.Rect(self.tiles[self.frame])
        self.rect = pygame.Rect(rect)
        sound.play()
        
    def update (self,time_passed):
        if (time_passed + self.time > self.delay):
            self.frame +=1
            if self.frame >= len(self.tiles):
                self.kill()
            else:
                self.area = pygame.rect.Rect(self.tiles[self.frame])
                self.time=0
        else:
            self.time +=time_passed
        
class Level():
    def __init__(self,level=1):
        self.level = level 
        self.map = Map(SPRITE_BLOCKS)
        self.map.loadMap(os.path.join("Maps",str(level) + ".map"))
        

class Map():
    (BLOCK_EMPTY, BLOCK_BRICK, BLOCK_STEEL, BLOCK_WATER, BLOCK_GRASS, BLOCK_FROZE) = range(6)
    DESTRUCTABLE = [BLOCK_BRICK]
    BULLET_STOPPER = (BLOCK_BRICK,BLOCK_STEEL)
    WALL = (BLOCK_BRICK, BLOCK_STEEL, BLOCK_WATER)
    BLOCK_SIZE = 20
    
    def __init__(self,blocks_filename):
        blocks = pygame.image.load(blocks_filename)
        block_images = [
            blocks.subsurface(0,0,Map.BLOCK_SIZE,Map.BLOCK_SIZE),
            blocks.subsurface(0,Map.BLOCK_SIZE,Map.BLOCK_SIZE,Map.BLOCK_SIZE),
            blocks.subsurface(Map.BLOCK_SIZE,Map.BLOCK_SIZE,Map.BLOCK_SIZE,Map.BLOCK_SIZE),
            blocks.subsurface(2*Map.BLOCK_SIZE,0,Map.BLOCK_SIZE,Map.BLOCK_SIZE),
            blocks.subsurface(3*Map.BLOCK_SIZE,0,Map.BLOCK_SIZE,Map.BLOCK_SIZE)
            ]
        self.block_brick = block_images[0]
        self.block_steel = block_images[1]
        self.block_grass = block_images[2]
        self.block_water = block_images[3]
        self.block_water1 = block_images[4]
    
    def loadMap(self,filename):
        self.map = []
        x,y=0,0
        for line in fileinput.input(filename):
            for current in line:
                if current == "#":
                    self.map.append((Map.BLOCK_BRICK,pygame.Rect(x,y,Map.BLOCK_SIZE,Map.BLOCK_SIZE)))
                elif current == "@":
                    self.map.append((Map.BLOCK_STEEL,pygame.Rect(x,y,Map.BLOCK_SIZE,Map.BLOCK_SIZE)))
                elif current == "%":
                    self.map.append((Map.BLOCK_GRASS,pygame.Rect(x,y,Map.BLOCK_SIZE,Map.BLOCK_SIZE)))
                elif current == "$":
                    self.map.append((Map.BLOCK_WATER,pygame.Rect(x,y,Map.BLOCK_SIZE,Map.BLOCK_SIZE)))
                x += Map.BLOCK_SIZE
            x = 0
            y += Map.BLOCK_SIZE
        self.updateRects()
    def drawMap(self,screen):
        
        for block in self.map:
            if block[0] == Map.BLOCK_BRICK:
                screen.blit(self.block_brick,block[1].topleft)
            elif block[0] == Map.BLOCK_STEEL:
                screen.blit(self.block_steel,block[1].topleft)
            elif block[0] == Map.BLOCK_GRASS:
                screen.blit(self.block_grass,block[1].topleft)
            elif block[0] == Map.BLOCK_WATER:
                if random.randrange(1):
                    screen.blit(self.block_water,block[1].topleft)
                else:
                    screen.blit(self.block_water1,block[1].topleft)
                    
    def isCollideWithMap(self,rect):
        for block in self.map:
            if block[0] in Map.WALL:
                if block[1].colliderect(rect):
                    return True
        return False
    def isBulletCollideWithMap(self,rect):
        index = rect.collidelist(self.block_rects)
        if index == -1:
            return False
        else:
            if self.map[index][0] in Map.DESTRUCTABLE:
                self.map.pop(index)
                self.block_rects.pop(index)
                return True
            elif self.map[index][0] in Map.BULLET_STOPPER:
                return True
            return False
    def updateRects(self):
        self.block_rects = []
        for block in self.map:
            if block[0] in (self.BLOCK_BRICK,self.BLOCK_STEEL,self.BLOCK_WATER,self.BLOCK_GRASS):
                self.block_rects.append(block[1])
class Game():
    def __init__(self,stage=1):
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("World of Tanks")
    	
        #grupy
        self.tanks = pygame.sprite.Group()
        self.player = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.killed = pygame.sprite.Group()
        
        self.shot_sound = pygame.mixer.Sound(SOUND_SHOT)
        self.explosion_sound = pygame.mixer.Sound(SOUND_EXPLOSION)
        self.startgame_sound = pygame.mixer.Sound(SOUND_GAMESTART)
        self.gameover_sound = pygame.mixer.Sound(SOUND_GAMEOVER)
        self.intro_sound = pygame.mixer.music.load(SOUND_INTRO)
        
        self.stage = stage
        self.level = Level(stage)
        self.killed_count = 0
        
        self.player_Sprite = PlayerTank(self.screen,SPRITE_PLAYER1,2.0,self.shot_sound)
        self.player_Sprite.add(self.tanks,self.player)
    def text_objects(self,text,color,size):
        if size == "small":
        	textSurface = smallfont.render(text,True,color)
        elif size == "medium":
        	textSurface = medfont.render(text,True,color)
        elif size == "large":
        	textSurface = largefont.render(text,True,color)
        return textSurface, textSurface.get_rect()
    def text_to_button(self,msg,color,buttonx,buttony,buttonwidth,buttonheight,size="small"):
        self.textSurf,self.textRect = self.text_objects(msg,color,size)
        self.textRect.center = ((buttonx+(buttonwidth/2)),buttony+(buttonheight/2))
        self.screen.blit(self.textSurf,self.textRect)
            
    def message_to_screen(self,msg,color,y_display=0,size="small"):
        self.textSurf, self.textRect = self.text_objects(msg,color,size)
        self.textRect.center = (display_width/2), (display_height/2)+y_display
        self.screen.blit(self.textSurf,self.textRect)
    def button(self,text,x,y,width,height,size,inactive_color,active_color,action=None):
        cur = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x+width > cur[0] > x and y+height > cur[1] > y:
            pygame.draw.rect(self.screen,active_color,(x,y,width,height))
            if click[0]==1 and action != None:
                if action == "quit":
                    pygame.quit()
                    quit()
                if action == "play":
                    Game().game()
        else:
            pygame.draw.rect(self.screen,inactive_color,(x,y,width,height))
        self.text_to_button(text,BLACK,x,y,width,height,size)
    def game_intro(self):
        pygame.mixer.music.play(-1)
        intro = True
        while intro:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            keyPresses = pygame.key.get_pressed()
            if keyPresses[K_ESCAPE]:
                    pygame.quit()
                    quit()
            self.screen.fill(BLACK)
            self.message_to_screen("WORLD", YELLOW, -100, "large")
            self.message_to_screen("OF", YELLOW, 0, "large")
            self.message_to_screen("TANKS", YELLOW, 100, "large")
            self.button("Play",150,500,100,50,"small",GREEN,LIGHT_GREEN,"play")
            self.button("Quit",550,500,100,50,"small",RED,LIGHT_RED,"quit")
            pygame.display.update()
            self.clock.tick(50)
    def won(self):
        self.startgame_sound.play()
        game_over = True
        time.sleep(3.5)
        pygame.mixer.music.play(-1)
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            keyPresses = pygame.key.get_pressed()
            if keyPresses[K_ESCAPE]:
                    pygame.quit()
                    quit()    
            self.screen.fill(BLACK)
            self.message_to_screen("You", YELLOW, -100, "large")
            self.message_to_screen("Won!", YELLOW, 0, "large")
            self.button("Play",150,500,100,50,"small",GREEN,LIGHT_GREEN,"play")
            self.button("Quit",550,500,100,50,"small",RED,LIGHT_RED,"quit")
            pygame.display.update()
            self.clock.tick(50)
    def game_over(self):
        time.sleep(1)
        game_over = True
        pygame.mixer.music.play(-1)
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            keyPresses = pygame.key.get_pressed()
            if keyPresses[K_ESCAPE]:
                    pygame.quit()
                    quit()    
            self.screen.fill(BLACK)
            self.message_to_screen("Game", YELLOW, -100, "large")
            self.message_to_screen("Over", YELLOW, 0, "large")
            self.button("Play",150,500,100,50,"small",GREEN,LIGHT_GREEN,"play")
            self.button("Quit",550,500,100,50,"small",RED,LIGHT_RED,"quit")
            pygame.display.update()
            self.clock.tick(50)
    def game(self):
        gameExit = False
        gameOver = False
        gameNext = False
        self.startgame_sound.play()
        while not gameExit:
            if gameNext is True:
                if self.stage == LAST_LEVEL:
                    Game().won()
                else:
                    Game(self.stage+1).game()
            if gameOver is True:
                   self.game_over()
            if not self.player:
                gameOver=True
            time_passed = self.clock.tick(50)
            self.screen.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameExit = True
            keyPresses = pygame.key.get_pressed()
            if self.player:
                if keyPresses[K_SPACE]:
                    self.player_Sprite.shot()
                if keyPresses[K_UP]:
                    self.player_Sprite.update(time_passed,(0,-1),self.enemies,self.level.map)
                elif keyPresses[K_DOWN]:
                    self.player_Sprite.update(time_passed,(0,1),self.enemies,self.level.map)
                elif keyPresses[K_LEFT]:
                    self.player_Sprite.update(time_passed,(-1,0),self.enemies,self.level.map)
                elif keyPresses[K_RIGHT]:
                    self.player_Sprite.update(time_passed,(1,0),self.enemies,self.level.map)
                elif keyPresses[K_ESCAPE]:
                    gameExit = True
                else:
                    self.player_Sprite.update(time_passed,(0,0),self.enemies,self.level.map)
            for die in pygame.sprite.groupcollide(self.enemies,self.player_Sprite.bullets,False,True):
               self.killed.add(Explosion(SPRITE_EXPLOSION2,self.screen,die.rect,self.explosion_sound))
               die.kill()
               self.killed_count +=1
                
            for enemy in self.enemies.sprites():
                if pygame.sprite.groupcollide(self.player,enemy.bullets,False,True):
                    self.killed.add(Explosion(SPRITE_EXPLOSION2,self.screen,self.player_Sprite,self.explosion_sound))
                    self.player_Sprite.kill()
                    self.gameover_sound.play()
                    
                    
            for bullet in self.player_Sprite.bullets:
                if self.level.map.isBulletCollideWithMap(bullet.rect):
                    bullet.kill()
            for enemy in self.enemies:
                for bullet in enemy.bullets:
                    if self.level.map.isBulletCollideWithMap(bullet.rect):
                        bullet.kill()
            
            if len(self.enemies) < ENEMIES and self.killed_count <= KILL_GOAL - ENEMIES:
                i=0
                while i<ENEMIES-len(self.enemies):
                    enemy = (EnemyTank(self.screen,SPRITE_ENEMY,2.0,[20+random.randrange(SCREEN_SIZE[0]-50),20]))
                    if not pygame.sprite.spritecollideany(enemy,self.tanks) and not self.level.map.isCollideWithMap(enemy.rect):
                        enemy.add(self.tanks,self.enemies)
                        i+=1
            self.enemies.update(time_passed,self.tanks,self.level.map)
            self.killed.update(time_passed)  
            self.tanks.draw(self.screen)
            self.level.map.drawMap(self.screen)
            
            for ex in self.killed:
                self.screen.blit(ex.image,ex.rect,ex.area)		
            if self.killed_count == KILL_GOAL:
                gameNext=True
            pygame.display.update()
           
        pygame.quit()
        quit()   
     
                
Game().game_intro()
