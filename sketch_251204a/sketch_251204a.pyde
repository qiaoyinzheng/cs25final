import random
import time

RES_WIDTH = 1280
RES_HEIGHT = 720

class Ship:
    
    def __init__(self, in_x, in_y, in_friction):
        
        self.x = in_x
        self.y = in_y
        self.angle = -90
        self.diameter = 20
        
        self.velocity_x = 0
        self.velocity_y = 0
        
        self.key_handler = {LEFT:False, RIGHT:False, UP:False}
        
        self.friction = in_friction
        
    def update(self):
        
        #rtation
        if self.key_handler[LEFT]:
            self.angle -= 4.0
        if self.key_handler[RIGHT]:
            self.angle += 4.0
            
        #thrust & inertia    
        if self.key_handler[UP]:
            
            # read https://www.kodeco.com/2736-trigonometry-for-game-programming-part-1-2
            # actually interesting take
            
            self.velocity_x += cos(radians(self.angle)) * 0.2    # eg. facing right ~ 0 degrees ~ cos is 1, indicating +1 movement towards X....
            self.velocity_y += sin(radians(self.angle)) * 0.2            
        
        # movement, + modifier of friction
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y
        
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        if(self.x > RES_WIDTH+50):
            
            self.x = -10
            
        if(self.x < -50):
            
            self.x = RES_WIDTH+10
            
        if(self.y > RES_HEIGHT+50):
            
            self.y = -10
        
        if(self.y < -50):
            
            self.y = RES_HEIGHT+10

    def display(self):
        
        self.update()
        fill(0,0,255)
        ellipse(self.x, self.y, self.diameter, self.diameter)
        
class Bullet:
    
    def __init__(self, in_x, in_y, in_angle):
        
        self.x = in_x
        self.y = in_y
        
        self.vx = cos(radians(in_angle)) * 10     # same logic
        self.vy = sin(radians(in_angle)) * 10
        
        self.alive = True
        
    def display(self):
        
        self.x += self.vx
        self.y += self.vy
        
        fill(255,0,0)
        ellipse(self.x, self.y, 5, 5)
        
        if(self.x < 0 or self.x > RES_WIDTH or
            self.y < 0 or
                self.y > RES_HEIGHT):
            
            self.alive = False

class Asteroid:
    
    def __init__(self, in_x = None, in_y = None, size_type = 'RANDOM'):
        
        if(size_type == 'RANDOM'):
           
            select = random.randint(1, 3)
            if(select == 1): 
                self.type = 'SMALL'
            
            elif(select == 2): 
                self.type = 'MEDIUM'
            
            else: 
                self.type = 'LARGE'
        else:
            
            self.type = size_type

        if(self.type == 'SMALL'):
            self.diameter = 40
            self.score_val = 10
            
        elif(self.type == 'MEDIUM'):
            self.diameter = 60
            self.score_val = 20
            
        else: 
            self.diameter = 80
            self.score_val = 30

        if(in_x is not None and in_y is not None):
            
            self.x = in_x
            self.y = in_y
            self.vx = random.randint(-4, 4)
            self.vy = random.randint(-4, 4)
            
        else:
            side = random.randint(0, 1)
            if(side == 0):
                self.x = -50
                self.vx = random.randint(1, 3)
                self.vy = random.randint(1, 3)
            else:
                self.x = RES_WIDTH + 50
                self.vx = random.randint(-3, -1)
                self.vy = random.randint(-3, -1)
            self.y = random.randint(0, RES_HEIGHT)

        self.x_deviance = 0
        self.y_deviance = 0
        self.alive = True
        
        self.x_deviance_direction = random.randint(1,2)
        self.y_deviance_direction = random.randint(1,2)
        
    def display(self):
        
        if(self.x > RES_WIDTH+100): 
            self.x = -50
        
        if(self.x < -100): 
            self.x = RES_WIDTH+50
        
        if(self.y > RES_HEIGHT+100): 
            self.y = -50
        
        if(self.y < -100): 
            self.y = RES_HEIGHT+50
        
        if(self.x_deviance_direction == 1):
            self.x_deviance += random.randint(1,50) / 75
        
        else:
            self.x_deviance -= random.randint(1,50) / 75
            
        if(self.y_deviance_direction == 1):
            self.y_deviance += random.randint(1,50) / 75
        
        else:
            self.y_deviance -= random.randint(1,50) / 75
        
        self.x = self.x + self.vx + self.x_deviance
        self.y = self.y + self.vy + self.y_deviance
        
        fill(255)
        ellipse(self.x, self.y, self.diameter, self.diameter)
        
class Game:
    
    def __init__(self):
        
        self.waves = []
        
        for i in range(11):
            
            self.waves.append(Wave(i))
        
        self.wave = 1
        self.coins = 0
        self.score = 0
        
        self.last_shot_time = 0
    
    def display(self):
        
        self.waves[self.wave].display()
        if(self.waves[self.wave].ending_detection() == True):
            
            self.waves[self.wave] = Wave(self.wave)
            if(self.wave+1 > 10):
                
                self.wave = 1
                # Game win display
                fill(255)
                textSize(24)
                textAlign(RIGHT, TOP)
                text("You have progressed through all 10 waves"+str(self.health), RES_WIDTH / 2 -80, 110)
                
            else: 
                self.wave+=1
        
        # Score display
        fill(255)
        textSize(24)
        textAlign(RIGHT, TOP)
        text("Score: "+str(self.score), RES_WIDTH - 20, 20)
        
        # Wave number display
        fill(255)
        textSize(24)
        textAlign(RIGHT, TOP)
        text("Wave: "+str(self.wave), RES_WIDTH - 20, 80)
        
    def append_bullets(self):
        
        if(time.time() - self.last_shot_time >= 0.1):
        
            self.waves[self.wave].bullets.append(Bullet(self.waves[self.wave].ship.x, self.waves[self.wave].ship.y, self.waves[self.wave].ship.angle))
            self.last_shot_time = time.time()
        
    def directional_signal(self, in_direction,in_option):
        
        self.waves[self.wave].ship.key_handler[in_direction] = in_option
        
class Wave:

    def __init__(self, in_wave_number):    

        self.bullets = []
        self.asteroids = []
        self.wave_number = in_wave_number
        
        self.asteroids_num = self.wave_number*3
        
        self.ship = Ship(40, 20,0.98)     # creation of SHIP object
        self.gamestate = 'Game'       # 'Game' or 'Stop' states
        self.last_spawntime = 0
        self.health = 5
        
    def display(self):    

        if(time.time() - self.last_spawntime > 3 and self.asteroids_num > 0):

            self.asteroids.append(Asteroid())
            self.asteroids_num = self.asteroids_num-1
            
            self.last_spawntime = time.time()
            
        self.ship.display()
        
        # now detect inter-asteroids collisions

        for i in range(len(self.asteroids)):
            for j in range(i + 1, len(self.asteroids)):
                a1 = self.asteroids[i]
                a2 = self.asteroids[j]
                
                min_distance = (a1.diameter / 2) + (a2.diameter / 2)
                
                if(dist(a1.x, a1.y, a2.x, a2.y) < min_distance):
                    
                    # swap x velocity of the 2
                    temp_vx = a1.vx
                    a1.vx = a2.vx
                    a2.vx = temp_vx
                    
                    # swap y velocity of the 2
                    temp_vy = a1.vy
                    a1.vy = a2.vy
                    a2.vy = temp_vy
                
                    a1.x += a1.vx * 6
                    a1.y += a1.vy * 6
                    a2.x += a2.vx * 6
                    a2.y += a2.vy * 6       
       
        # detect asteroid - ship collisions
        for i in range(len(self.asteroids)):
            for j in range(i + 1, len(self.asteroids)):
                a1 = self.asteroids[i]
                a2 = self.ship
                
                min_distance = (a1.diameter / 2) + (a2.diameter / 2)
                
                if(dist(a1.x, a1.y, a2.x, a2.y) < min_distance):
                    
                    # swap x velocity of the 2
                    self.health = self.health -1
                    
                    a1.alive = False
                    self.asteroids.remove(a1)

        #list to contain individual bullets
        for bullet in self.bullets[:]:
            bullet.display()
            if(bullet.alive == False): 
                
                self.bullets.remove(bullet)
            
        for asteroid in self.asteroids[:]:
            
            asteroid.display()
                    
            # collision detection, similar to Mario case
            for bullet in self.bullets:
                if(dist(asteroid.x, asteroid.y, bullet.x, bullet.y) < asteroid.diameter / 2 +5):
                    asteroid.alive = False
                    bullet.alive = False
                    game.score += asteroid.score_val
                    
                    if(asteroid.type == 'LARGE'):
                       
                        self.asteroids.append(Asteroid(asteroid.x-20, asteroid.y-20, 'MEDIUM'))
                        self.asteroids.append(Asteroid(asteroid.x+20, asteroid.y+20, 'MEDIUM'))
                    
                    elif(asteroid.type == 'MEDIUM'):
                    
                        self.asteroids.append(Asteroid(asteroid.x-20, asteroid.y-20, 'SMALL'))
                        self.asteroids.append(Asteroid(asteroid.x+20, asteroid.y+20, 'SMALL'))
                    
            if(asteroid.alive == False): 
               
               self.asteroids.remove(asteroid)
        
        print("total amount:",len(self.asteroids))         # *TESTING, REMOVE BEFORE SUBMISSION
        
        # Health display
        fill(255)
        textSize(24)
        textAlign(RIGHT, TOP)
        text("Health: "+str(self.health), RES_WIDTH - 20, 50)
        
    def ending_detection(self):
        
        if(len(self.asteroids) == 0):
            
            return True
    
game = Game()

def setup():
    
    size(RES_WIDTH, RES_HEIGHT)
    noStroke()

def draw():
    
    background(20)
    game.display()

def keyPressed():
    
    if key == ' ':
        game.append_bullets()
    
    if keyCode == LEFT:
        game.directional_signal(LEFT,True)
    if keyCode == RIGHT:
        game.directional_signal(RIGHT,True)
    if keyCode == UP:
        game.directional_signal(UP,True)

def keyReleased():
    
    if keyCode == LEFT:
        game.directional_signal(LEFT, False)
    if keyCode == RIGHT:
        game.directional_signal(RIGHT, False)
    if keyCode == UP:
        game.directional_signal(UP, False)
