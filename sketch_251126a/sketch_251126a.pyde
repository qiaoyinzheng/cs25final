import random

RES_WIDTH = 600
RES_HEIGHT = 600

class Ship:
    
    def __init__(self, in_x, in_y):
        
        self.x = in_x
        self.y = in_y
        self.angle = -90
        
        self.velocity_x = 0
        self.velocity_y = 0
        
        self.key_handler = {LEFT:False, RIGHT:False, UP:False}
        
    def update(self):
        
        #rtation
        if self.key_handler[LEFT]:
            self.angle -= 5
        if self.key_handler[RIGHT]:
            self.angle += 5
            
        #thrust & inertia    
        if self.key_handler[UP]:
            
            # read https://www.kodeco.com/2736-trigonometry-for-game-programming-part-1-2
            # actually interesting take
            
            self.velocity_x += cos(radians(self.angle)) * 0.2     # eg. facing right ~ 0 degrees ~ cos is 1, indicating +1 movement towards X....
            self.velocity_y += sin(radians(self.angle)) * 0.2            
        
        # movement, + modifier of friction
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y
        
        self.velocity_x *= 0.98
        self.velocity_y *= 0.98

    def display(self):
        
        self.update()
        fill(255)
        ellipse(self.x, self.y, 20, 20)
        
class Bullet:
    
    def __init__(self, in_x, in_y, in_angle):
        
        self.x = in_x
        self.y = in_y
        
        self.vx = cos(radians(in_angle)) * 7     # same logic
        self.vy = sin(radians(in_angle)) * 7
        
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
    
    def __init__(self):
        
        side = random.randint(0, 1)
        
        if(side == 0):
            self.x = 0
        else:
            self.x = RES_WIDTH
            
        self.y = random.randint(0, RES_HEIGHT)
        self.vx = random.randint(-3, 3)
        self.vy = random.randint(-3, 3)
    
        self.alive = True
        
    def display(self):
        
        self.x = self.x + self.vx
        self.y = self.y + self.vy
        fill(255)
        ellipse(self.x, self.y, 40, 40)

class Game:
    
    def __init__(self):
        
        self.ship = Ship(40, 20)
        self.bullets = []
        self.asteroids = []
        
    def display(self):
        
        spawning_chance = random.randint(0, 50)
        if spawning_chance == 0: 
            self.asteroids.append(Asteroid())
        
        self.ship.display()
        
        #list to contain individual bullets
        for bullet in self.bullets[:]:
            bullet.display()
            if(bullet.alive == False): 
                
                self.bullets.remove(bullet)
            
        for asteroid in self.asteroids[:]:
            
            asteroid.display()
            
            # collision detection, similar to Mario case
            for bullet in self.bullets:
                if(dist(asteroid.x, asteroid.y, bullet.x, bullet.y) < 25):
                    asteroid.alive = False
                    bullet.alive = False
                    
            if(asteroid.alive == False): 
               
               self.asteroids.remove(asteroid)

game = Game()

def setup():
    
    size(RES_WIDTH, RES_HEIGHT)
    noStroke()

def draw():
    
    background(20)
    game.display()

def keyPressed():
    
    if key == ' ':
        game.bullets.append(Bullet(game.ship.x, game.ship.y, game.ship.angle))
    
    if keyCode == LEFT:
        game.ship.key_handler[LEFT] = True
    if keyCode == RIGHT:
        game.ship.key_handler[RIGHT] = True
    if keyCode == UP:
        game.ship.key_handler[UP] = True

def keyReleased():
    
    if keyCode == LEFT:
        game.ship.key_handler[LEFT] = False
    if keyCode == RIGHT:
        game.ship.key_handler[RIGHT] = False
    if keyCode == UP:
        game.ship.key_handler[UP] = False
