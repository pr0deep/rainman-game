import pygame,numpy as np,random,sys,os

#PATHs

SPRITE_PATH = r"C:\Users\prade\OneDrive\Documents\OldProjects\game\assets\sprites"
SOUNDS_PATH = r"C:\Users\prade\OneDrive\Documents\OldProjects\game\assets\sounds"
FONT_PATH = r"C:\Users\prade\OneDrive\Documents\OldProjects\game\assets\fonts"

#creating files
so_menuclick = os.path.join(SOUNDS_PATH,"menu_click.ogg")
so_dash = os.path.join(SOUNDS_PATH,"dash.ogg")
so_j1 = os.path.join(SOUNDS_PATH,"j1.ogg")
so_j2 = os.path.join(SOUNDS_PATH,"j2.ogg")
so_gameover = os.path.join(SOUNDS_PATH,"game_over.ogg")
so_nani = os.path.join(SOUNDS_PATH,"nani.ogg")
so_thunder = os.path.join(SOUNDS_PATH,"thunder.ogg")
so_menu = os.path.join(SOUNDS_PATH,"menu.ogg")
so_life = os.path.join(SOUNDS_PATH,"life.ogg")
so_bgm = os.path.join(SOUNDS_PATH,"bgm.ogg")
io_animeg = os.path.join(SPRITE_PATH,"anime_girl1.png")
io_dash = os.path.join(SPRITE_PATH,"dash.png")
io_heart = os.path.join(SPRITE_PATH,"heart.png")
io_icon = os.path.join(SPRITE_PATH,"icon.png")
io_lefta = os.path.join(SPRITE_PATH,"left_arrow.png")
io_righta = os.path.join(SPRITE_PATH,"right_arrow.png")
io_player = os.path.join(SPRITE_PATH,"player.png")
io_sun = os.path.join(SPRITE_PATH,"sun.png")
fo_gamefont = os.path.join(FONT_PATH,"game_font.otf")
#initialising module
pygame.init()

#initialising variables
GAME_HEIGHT = 900
GAME_WIDTH = 900
SIZE = (GAME_WIDTH,GAME_HEIGHT)
BG_COLOR = (255,255,255)
BLACK_PARTICLE_COUNT = 4
GAME_PARTICLE_COUNT = 10
BLACK_PARTICLE_SIZE = 9
COLOR_PARTICLE_SIZE = 9
COLORS = [(0,78,189),(255,179,0),(234,0,52),(130,0,72),(255,130,42)]
myfont = pygame.font.Font(fo_gamefont,30) 
POINTS = 0
RAIN_COLOR = (0,0,0)
DIFFICULTY = 1
PARAMS = [{"degen":-10,"gain":+30,"mult":1},{"degen":-20,"gain":20,"mult":2},{"degen":-50,"gain":5,"mult":3}]

clock = pygame.time.Clock()

#creating screen
screen = pygame.display.set_mode(SIZE)


#bgm
bgm  = pygame.mixer.Sound(so_bgm)
pygame.mixer.music.set_volume(0.1)
bgm.play()

menu_click  = pygame.mixer.Sound(so_menuclick)
j1  = pygame.mixer.Sound(so_j1)
j2  = pygame.mixer.Sound(so_j2)
j1.set_volume(0.1);j2.set_volume(0.1)
thunder_sound  = pygame.mixer.Sound(so_thunder)
dash_sound  = pygame.mixer.Sound(so_dash);dash_sound.set_volume(0.1)
life_sound  = pygame.mixer.Sound(so_life);life_sound.set_volume(0.3)
game_over_sound  = pygame.mixer.Sound(so_gameover);game_over_sound.set_volume(0.3)
retry_sound  = pygame.mixer.Sound(so_nani);retry_sound.set_volume(0.3)


#setup screen
pygame.display.set_caption("Rainman")
pygame.display.set_icon(pygame.image.load(io_icon))


#player model
player_texture = pygame.image.load(io_player)

#creating floor
floor_surface = pygame.Surface((GAME_WIDTH,player_texture.get_height()+25))
floor_surface.fill((0,0,0))

#loading dash image
dash_image = pygame.image.load(io_dash)

player_loc = (GAME_WIDTH/2,GAME_HEIGHT-floor_surface.get_height()-player_texture.get_height())

sun = pygame.image.load(io_sun)
arrow_l = pygame.image.load(io_lefta)
arrow_r = pygame.image.load(io_righta) 

ag_game_over = pygame.image.load(io_animeg) 
ag_game_over = pygame.transform.scale(ag_game_over,(200,333)) 
#model for player


def display_bonus():
    global PARAMS,DIFFICULTY
    return myfont.render(str(PARAMS[DIFFICULTY-1]["gain"]), False, (0, 0, 0))

def display_neg():
    global PARAMS,DIFFICULTY
    return myfont.render(str(PARAMS[DIFFICULTY-1]["degen"]), False, (0, 0, 0))



heart_image = pygame.image.load(io_heart)

class Hearts:
    def __init__(self,l,heart_image):
        self.texture = heart_image
        self.cur_lives = l
        self.cur_hpos = []
        self.initial_pos = (20,85)
        self.cur_hpos.append(self.initial_pos)
        for i in range(l-1):
            self.cur_hpos.append((self.initial_pos[0]+(i+1)*self.texture.get_width()+6,self.initial_pos[1]))
    
    def kill(self):
        life_sound.play()
        self.cur_lives -=1

heart = Hearts(3,heart_image)


class Player():
    def __init__(self,texture,location):
        self.speed_x= 0;self.speed_y=0;self.gravity = 1
        self.texture = texture
        self.x = location[0]
        self.y = location[1]
        self.jump_state = False;self.double_jump_state = False
        self.rect = pygame.Rect(self.x,self.y,self.texture.get_width(),self.texture.get_height())
        self.lives = 3
        self.health = 100
        self.dash_stat = False
        self.dash_speed = 15
    
    def update(self):
        new_pos = self.calculate_pos()
        self.x = new_pos[0]
        self.y = new_pos[1]
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self,screen_obj):
        screen_obj.blit(self.texture,(self.x,self.y))

    def calculate_pos(self):
        #bound rule
        if((self.speed_x+self.x+self.texture.get_width() >= GAME_WIDTH or self.speed_x+self.x<=0)):
            self.speed_x = 0
        if(self.speed_y+self.y+self.texture.get_height()>GAME_HEIGHT-floor_surface.get_height() or self.speed_y+self.y<=0):
            if not self.jump_state:
                self.speed_y = 0
            else:
                if self.double_jump_state:
                    self.double_jump_state = False
                    self.jump_state = False
                    self.speed_y = 0
                else:
                    self.jump_state = False
                    self.speed_y = 0
        if(self.jump_state):
            self.speed_y+=1

        if(self.dash_stat):
            if(not (self.dash_speed*np.sign(self.speed_x)+self.x+self.texture.get_width() >= GAME_WIDTH or self.dash_speed*np.sign(self.speed_x)+self.x<=0)):
                self.speed_x += self.dash_speed*np.sign(self.speed_x)
                self.dash_stat = False
            
            

        return self.speed_x+self.x,self.speed_y+self.y

    def jump(self):
        if self.jump_state:
            if self.double_jump_state:
                return
            else:
                self.speed_y -= 30
                j2.play()
                self.double_jump_state = True
        else:
            j1.play()
            self.jump_state = True
            self.speed_y = -20

    def dash(self):
        if self.dash_stat:
            return
        dash_sound.play()
        self.dash_stat = True
        

    def deduce(self):
        global POINTS,PARAMS,DIFFICULTY
        POINTS-=5*PARAMS[DIFFICULTY-1]["mult"]
        if POINTS<0:
            POINTS = 0
        self.health += PARAMS[DIFFICULTY-1]["degen"]
        if self.health<0:
            self.lives-=1
            if self.lives==0:
                print("Game Over")
                game_over_sound.play()
                heart.cur_lives = 3
                gameover()
               
            else:
                heart.kill()
            self.health = 100
        screen.blit(display_neg(),(self.rect.x,self.rect.y-50))
        
    def heal(self):
        global POINTS,PARAMS,DIFFICULTY
        POINTS+=10*PARAMS[DIFFICULTY-1]["mult"]
        if self.health<90:
            self.health += PARAMS[DIFFICULTY-1]["gain"]
        else:
            self.health = 100
        screen.blit(display_bonus(),(self.rect.x,self.rect.y-50))

    def reset(self):
        self.lives = 3
        self.health = 100



                

hero = Player(player_texture,player_loc)

class Particle:
    def __init__(self):
        self.x = np.random.randint(0,GAME_WIDTH)
        self.y = np.random.randint(0,GAME_HEIGHT/2)
        self.vx = np.random.randint(-1,1)
        self.vy = np.random.randint(1,5)
        self.rect = pygame.rect.Rect(self.x,self.y,BLACK_PARTICLE_SIZE,BLACK_PARTICLE_SIZE)


    def update(self):
        if(self.x+self.vx > GAME_WIDTH or self.vx+self.x <0 or self.y+self.vy>GAME_HEIGHT):
            self.rebirth()
        else:
            self.x = self.x + self.vx
            self.y = self.y + self.vy
            self.rect.x = self.x
            self.rect.y = self.y
        self.isColliding(hero)

    def update_menu(self):
        if(self.x+self.vx*0.25 > GAME_WIDTH or self.vx+self.x <0 or self.y+self.vy*0.25>GAME_HEIGHT):
            self.rebirth()
        else:
            self.x = self.x + self.vx*0.25
            self.y = self.y + self.vy*0.25
            self.rect.x = self.x
            self.rect.y = self.y

    def rebirth(self):
        self.x = np.random.randint(0,GAME_WIDTH)
        self.y = 0
        self.rect.x = self.x
        self.rect.y = self.y
        self.vx = np.random.randint(-2,2)
        self.vy = np.random.randint(1*5/3,3*5/3)
    
    def isColliding(self,player):
        if(self.rect.colliderect(player.rect)):
            player.deduce()
            self.rebirth()
            
    def impulse(self):
        self.vx = -1*self.vx
        self.x += self.vx
        self.rect.x = self.x



class Particles():
    def __init__(self,particle_count):
        self.count = particle_count
        self.particles = []
        for i in range(self.count):
            self.particles.append(Particle())


    def particle_coll(self,other_particle_group):
        for i in range(self.count):
            for j in range(i+1,self.count):
                if(self.particles[i].rect.colliderect(self.particles[j].rect)):
                    self.particles[i].impulse()
                    self.particles[j].impulse()
                for k in range(other_particle_group.count):
                    if self.particles[i].rect.colliderect(other_particle_group.particles[k].rect):
                        self.particles[i].impulse()
                        other_particle_group.particles[k].impulse()
                    

    def update(self):
        for i in range(self.count):
            self.particles[i].update()

    def menu_update(self):
        for i in range(self.count):
            self.particles[i].update_menu()

class GameParticle(Particle):
    def __init__(self):
        super().__init__()
        self.color = random.choice(COLORS)

    def isColliding(self,player):
        if(self.rect.colliderect(player.rect)):
            player.heal()
            self.rebirth()
            

class GameParticles(Particles):
    def __init__(self,particle_count):
        self.count = particle_count
        self.particles = []
        for i in range(self.count):
            self.particles.append(GameParticle())


    def update(self):
        for i in range(self.count):
            self.particles[i].update()

    def menu_update(self):
        for i in range(self.count):
            self.particles[i].update_menu()

class RainParticlesInLine:
    def __init__(self,m,c,n):
        self.particles = []
        t= np.random.randint(0,2)
        self.m = m;self.c = c
        self.particles.append([t,m*t+c])
        self.step = np.random.randint(1,7);self.offset = 10;self.particle_count = n

        for i in range(n-1):
            self.particles.append( [self.particles[i][0]+self.offset+np.random.randint(0,6),t*(self.particles[i][0]+self.offset+np.random.randint(0,6))+self.c] )
    def update(self):
        for i in range(self.particle_count):
            self.particles[i][0] += self.step*np.random.randint(1,10)
            self.particles[i][1] = self.m*self.particles[i][0] +self.c
            if(self.particles[i][0]>GAME_WIDTH or self.particles[i][0]<0 or self.particles[i][1]>GAME_HEIGHT):
                self.particles[i][0] = np.random.randint(0,10)
                self.particles[i][1] = self.m*self.particles[i][0]+self.c
                continue
            
 

class Rain:
    def __init__(self,n,l):
        self.particles = []
        self.slope = 1;self.l=l;self.n = n
        c = -800
        for i in range(l):
            self.particles.append(RainParticlesInLine(self.slope,c,n))
            c+=30
    
    def update(self):
        for i in range(self.l):
            self.particles[i].update()

particle_group = Particles(BLACK_PARTICLE_COUNT)
game_particle_group = GameParticles(GAME_PARTICLE_COUNT)

rain_group = Rain(10,60)
def score(points):
    return myfont.render('Score : '+str(points), False, (0, 0, 0))

dash_text = pygame.font.Font(fo_gamefont,30).render("Enter",False,(0,0,0))

thunder_event = pygame.USEREVENT+1
pygame.time.set_timer(thunder_event,35000)
bg_reset = pygame.USEREVENT+2
pygame.time.set_timer(bg_reset,1500)

class Slider:
    def __init__(self,maxval,x,y):
        self.max_val = maxval
        self.x = x;self.y = y
        self.rect = pygame.Rect(self.x,self.y,200,20)
        self.cur_val = 10;self.multiplier = self.rect.width/100
        self.circle_x = self.rect.x+self.rect.width;self.circle_y = self.rect.y+10
        self.circle_r = 15;self.circle_color = (0,0,0)
    
    def update(self,mp):
        mpx = mp[0]
        mpy = mp[1]
        if mpx<self.rect.x:
            self.circle_x = self.rect.x
        elif mpx>self.rect.x+self.rect.width:
            self.circle_x =self.rect.x+self.rect.width
        else:
            self.circle_x = mpx
        self.cur_val = self.multiplier*(self.circle_x-self.rect.x)
        for i in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(i).set_volume(self.cur_val/100)

class HMenu:
    def __init__(self,l,r) :
        self.left = l;self.right = r
        self.font = pygame.font.Font(fo_gamefont,40)
        self.texts = ['Easy','Medium','Hard']
        self.cur_diff = 0
        self.text = self.font.render(self.texts[0], False, (0, 0, 0))
    

    def update(self,a):
        global DIFFICULTY
        if a>0:
            self.cur_diff = (self.cur_diff+1)%3
            DIFFICULTY = self.cur_diff+1
            self.text = self.font.render(self.texts[self.cur_diff], False, (0, 0, 0))
        elif a<0:
            self.cur_diff = (3+self.cur_diff-1)%3
            DIFFICULTY = self.cur_diff+1
            self.text = self.font.render(self.texts[self.cur_diff], False, (0, 0, 0))
        else:
            return


def game():
    global POINTS,RAIN_COLOR
    #run condition
    run = True

    #game loop
    while run:
        global BG_COLOR
        clock.tick(120)
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("### Game Quit by User!!!")
                run = False
                sys.exit()

            #char move events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    hero.speed_x = -5
                if event.key == pygame.K_RIGHT:
                    hero.speed_x = 5

                if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    hero.jump()

                if event.key == pygame.K_ESCAPE:
                    run = False
                    main_menu()
                
                if event.key == pygame.K_RETURN:
                    hero.dash()
            

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    if hero.speed_x >0:
                        hero.speed_x = 0
                if event.key == pygame.K_LEFT:
                    if hero.speed_x <0:
                        hero.speed_x = 0
                
                
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_SPACE:
                    hero.speed_y = 0
            
            if event.type == thunder_event:
                thunder_sound.play()
                screen.fill((0,0,0))
                BG_COLOR = (0,0,0)
                RAIN_COLOR = (255,255,255)
                floor_surface.fill((255,255,255))
            
            if event.type == bg_reset:
                BG_COLOR = (255,255,255)
                RAIN_COLOR = (0,0,0)
                floor_surface.fill((0,0,0))
                POINTS+=1
            

        
        #rain 
        rain_group.update()

        for r in rain_group.particles:
            for k in r.particles:
                pygame.draw.line(screen,RAIN_COLOR,(k[0],k[1]),(k[0]+r.step,r.m*(r.step+k[0])+r.c),2)

        #sun
        screen.blit(sun,(GAME_WIDTH-sun.get_width()-5,5))
        #shower particles
        
        particle_group.update()

        particle_group.particle_coll(game_particle_group)


        for p in particle_group.particles:
            pygame.draw.circle(screen,(0,0,0),(p.x,p.y),BLACK_PARTICLE_SIZE)


        #game particles

        game_particle_group.update()

        game_particle_group.particle_coll(particle_group)

        for p in game_particle_group.particles:
            pygame.draw.circle(screen,p.color,(p.x,p.y),COLOR_PARTICLE_SIZE)


        #update player
        hero.update()
        
        hero.draw(screen)
        screen.blit(floor_surface,(0,GAME_HEIGHT-floor_surface.get_height()))

        screen.blit(score(POINTS),(20,50))

        for h in range(heart.cur_lives):
            screen.blit(heart_image,heart.cur_hpos[h])
        
        #dash icon
        screen.blit(dash_image,(20,400))
        screen.blit(dash_text,(20,400+dash_image.get_height()+10))

        pygame.display.update()

#menufont = pygame.font.SysFont('Comic Sans MS', 100)
menufont = pygame.font.Font(fo_gamefont,120)
#startfont = pygame.font.SysFont('Comic Sans MS', 50)
startfont = pygame.font.Font(fo_gamefont,50)



def main_menu():
    run = True 
    highlight_color = random.choice(COLORS)

    while run:
        clock.tick(60)
        screen.fill(BG_COLOR)
         #rain 
        rain_group.update()

        for r in rain_group.particles:
            for k in r.particles:
                pygame.draw.line(screen,(0,0,0),(k[0],k[1]),(k[0]+r.step,r.m*(r.step+k[0])+r.c),2)

        menu_text =  menufont.render('Rain Man', False, (0, 0, 0))

        start_text =  startfont.render('Play', False, (0, 0, 0))

        options_text =  startfont.render('Options', False, (0, 0, 0))

        exit_text =  startfont.render('Exit', False, (0, 0, 0))

        cursor = pygame.mouse.get_pos()
        if pygame.Rect(400,500,start_text.get_width(),start_text.get_height()).collidepoint(cursor) :
            start_text =  startfont.render('Play', False, highlight_color)

        if pygame.Rect(400,700,exit_text.get_width(),exit_text.get_height()).collidepoint(cursor) :
            exit_text =  startfont.render('Exit', False, highlight_color)

        if pygame.Rect(375,600,options_text.get_width(),options_text.get_height()).collidepoint(cursor) :
            options_text =  startfont.render('Options', False, highlight_color)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(400,500,start_text.get_width(),start_text.get_height()).collidepoint(cursor) :
                    run = False
                    menu_click.play()
                    game()
                if pygame.Rect(400,700,exit_text.get_width(),exit_text.get_height()).collidepoint(cursor) :
                    run = False
                    menu_click.play()
                    sys.exit()
                if pygame.Rect(375,600,options_text.get_width(),options_text.get_height()).collidepoint(cursor) :
                    run = False
                    menu_click.play()
                    options_menu()

        #copy code
        #shower particles
        
        particle_group.menu_update()
        particle_group.particle_coll(game_particle_group)
        for p in particle_group.particles:
            pygame.draw.circle(screen,(0,0,0),(p.x,p.y),BLACK_PARTICLE_SIZE)

        #game particles

        game_particle_group.menu_update()
        game_particle_group.particle_coll(particle_group)
        for p in game_particle_group.particles:
            pygame.draw.circle(screen,p.color,(p.x,p.y),COLOR_PARTICLE_SIZE)


        screen.blit(menu_text,(260,200))

        screen.blit(start_text,(400,500))

        screen.blit(options_text,(375,600))

        screen.blit(exit_text,(400,700))



    

        pygame.display.update()


diff_text =  startfont.render('Difficulty :', False, (0, 0, 0))

audio_text =  startfont.render('Music  : ', False, (0, 0, 0))


audio_slider = Slider(100,450,605)
slider_click_status = False

diff_menu = HMenu(arrow_l,arrow_r)

def options_menu():
    run = True
    global slider_click_status
    highlight_color = random.choice(COLORS)


    while run:
        screen.fill(BG_COLOR)
        clock.tick(120)
        #rain 
        rain_group.update()

        for r in rain_group.particles:
            for k in r.particles:
                pygame.draw.line(screen,(0,0,0),(k[0],k[1]),(k[0]+r.step,r.m*(r.step+k[0])+r.c),2)


        back_text =  startfont.render('Back', False, (0, 0, 0))
        cursor = pygame.mouse.get_pos()

        if pygame.Rect(400,700,back_text.get_width(),back_text.get_height()).collidepoint(cursor) :
            back_text =  startfont.render('Back', False, highlight_color)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                cursor = pygame.mouse.get_pos()
                if pygame.Rect(400,700,back_text.get_width(),back_text.get_height()).collidepoint(cursor) :
                    run = False
                    menu_click.play()
                    main_menu()
                if pygame.Rect(audio_slider.circle_x-audio_slider.circle_r,audio_slider.circle_y-audio_slider.circle_r,2*audio_slider.circle_r,2*audio_slider.circle_r).collidepoint(cursor):
                    slider_click_status = True
                if pygame.Rect(625,500,diff_menu.right.get_width(),diff_menu.right.get_height()).collidepoint(cursor):
                    menu_click.play()
                    diff_menu.update(1)
                if pygame.Rect(450,500,diff_menu.left.get_width(),diff_menu.left.get_height()).collidepoint(cursor):
                    menu_click.play()
                    diff_menu.update(-1)
            if event.type == pygame.MOUSEMOTION:
                if slider_click_status:
                    audio_slider.update(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                slider_click_status = False
        
        




        screen.blit(diff_text,(200,500))

        screen.blit(audio_text,(200,600))

        screen.blit(back_text,(400,700))
        pygame.draw.rect(screen,highlight_color,(audio_slider.rect.x,audio_slider.rect.y,audio_slider.circle_x-audio_slider.rect.x,audio_slider.rect.height))
        pygame.draw.rect(screen,audio_slider.circle_color,audio_slider.rect,3)

        pygame.draw.circle(screen,audio_slider.circle_color,(audio_slider.circle_x,audio_slider.circle_y),audio_slider.circle_r)
 
        screen.blit(diff_menu.left,(450,500))
        screen.blit(diff_menu.text,(510,500))
        screen.blit(diff_menu.right,(625,500))


        pygame.display.update()

over_text =  menufont.render('Game Over!', False, (0, 0, 0))


def gameover():
    run = True
    global POINTS
    POINTS = 0
    highlight_color = random.choice(COLORS)


    while run:
        clock.tick(120)

        screen.fill(BG_COLOR)

         #rain 
        rain_group.update()

        for r in rain_group.particles:
            for k in r.particles:
                pygame.draw.line(screen,(0,0,0),(k[0],k[1]),(k[0]+r.step,r.m*(r.step+k[0])+r.c),2)

        retry_text =  startfont.render('Retry', False, (0, 0, 0))
        exit_text =  startfont.render('Exit', False, (0, 0, 0))

        cursor = pygame.mouse.get_pos()
        if pygame.Rect(400,500,retry_text.get_width(),retry_text.get_height()).collidepoint(cursor):
            retry_text = startfont.render('Retry', False, highlight_color)
        if pygame.Rect(400,600,exit_text.get_width(),exit_text.get_height()).collidepoint(cursor) :
            exit_text =  startfont.render('Exit', False, highlight_color)
    



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                cursor = pygame.mouse.get_pos()
                if pygame.Rect(400,500,retry_text.get_width(),retry_text.get_height()).collidepoint(cursor) :
                    run = False
                    retry_sound.play()
                    hero.reset()
                    game()
                if pygame.Rect(400,600,exit_text.get_width(),exit_text.get_height()).collidepoint(cursor) :
                    run = False
                    sys.exit()


        screen.blit(ag_game_over,(0,GAME_HEIGHT-ag_game_over.get_height())) 

        screen.blit(over_text,(260,300))

        screen.blit(retry_text,(390,500))

        screen.blit(exit_text,(400,600))


        pygame.display.update()

main_menu()

#game()