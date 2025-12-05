add_library('sound')
from processing.sound import SoundFile
import random

# ---------------------------------
# GLOBAL RESOLUTION
# ---------------------------------
RES_WIDTH = 1280
RES_HEIGHT = 720

# ---------------------------------
# GLOBAL ASSETS
# ---------------------------------
main_bg = None
tutorial_bg = None 
bg_wave1_2 = None
bg_wave3_4 = None
bg_wave5_7 = None
bg_wave7_10 = None

# Ship Sprites
ship_sheet1 = None
ship_sprite2 = None
ship_sprite3 = None
ship_sprite4 = None
SHIP_FRAME_W = 250
SHIP_FRAME_H = 277

# Bullet Sprites
bullet_sheet = None
BULLET_FRAME_W = 140
BULLET_FRAME_H = 150

# Asteroid Sprites
big_aster_img = None
mid_aster_img = None
small_aster_img = None

# Shop Items
boost_img = None
heart_img = None
coin_img = None
pixel_font = None

# Sounds
bgm = None
bullet_sound = None
thrust_sound = None
ship_crash_sound = None
upgrade_sound = None

game = None 

# ---------------------------------
# SHIP CLASS
# ---------------------------------
class Ship:
    
    def __init__(self, in_x, in_y, in_friction, sprite_sheet=None):
        self.x = in_x
        self.y = in_y
        self.angle = -90
        self.diameter = 20
        
        self.velocity_x = 0
        self.velocity_y = 0
        
        self.key_handler = {LEFT:False, RIGHT:False, UP:False}
        self.friction = in_friction
        
        self.thrust_power = 0.1

        self.frame_index = 0
        self.anim_counter = 0
        self.thrust_playing = False
        
        self.sprite_sheet = sprite_sheet if sprite_sheet is not None else ship_sheet1
        
    def update(self):
        if self.key_handler[LEFT]:
            self.angle -= 4.0
        if self.key_handler[RIGHT]:
            self.angle += 4.0
            
        if self.key_handler[UP]:
            angle_rad = radians(self.angle)
            self.velocity_x += cos(angle_rad) * self.thrust_power
            self.velocity_y += sin(angle_rad) * self.thrust_power            

            max_frame_index = 3
            try:
                current_health = game.waves[game.wave].health
            except:
                current_health = 3

            if current_health >= 3:
                max_frame_index = 3
            elif current_health == 2:
                max_frame_index = 2
            elif current_health <= 1:
                max_frame_index = 1

            self.anim_counter += 1
            if self.anim_counter % 5 == 0:
                self.frame_index += 1
                if self.frame_index > max_frame_index:
                    self.frame_index = 0

            if thrust_sound is not None and not self.thrust_playing:
                thrust_sound.loop()
                self.thrust_playing = True

        else:
            self.frame_index = 0
            self.anim_counter = 0
            if thrust_sound is not None and self.thrust_playing:
                thrust_sound.stop()
                self.thrust_playing = False
        
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y
        
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        if(self.x > width + 50): self.x = -50
        if(self.x < -50): self.x = width + 50
        if(self.y > height + 50): self.y = -50
        if(self.y < -50): self.y = height + 50

    def display(self):
        self.update()

        if self.sprite_sheet is None:
            fill(0,0,255)
            ellipse(self.x, self.y, self.diameter, self.diameter)
            return

        sx1 = self.frame_index * SHIP_FRAME_W
        sy1 = 0
        sx2 = sx1 + SHIP_FRAME_W
        sy2 = SHIP_FRAME_H

        scale_factor = 0.4
        dw = SHIP_FRAME_W * scale_factor
        dh = SHIP_FRAME_H * scale_factor

        pushMatrix()
        translate(self.x, self.y)
        rotate(radians(self.angle + 90))
        imageMode(CENTER)
        image(self.sprite_sheet, 0, 0, dw, dh, sx1, sy1, sx2, sy2)
        popMatrix()

# ---------------------------------
# SHIP SUBCLASSES
# ---------------------------------
class CopperShip(Ship):
    def __init__(self, in_x, in_y, in_friction):
        super(CopperShip, self).__init__(in_x, in_y, in_friction, ship_sprite2)

class SilverShip(Ship):
    def __init__(self, in_x, in_y, in_friction):
        super(SilverShip, self).__init__(in_x, in_y, in_friction, ship_sprite3)

class CrystalShip(Ship):
    def __init__(self, in_x, in_y, in_friction):
        super(CrystalShip, self).__init__(in_x, in_y, in_friction, ship_sprite4)
        self.thrust_power = 0.2

# ---------------------------------
# BULLET CLASS
# ---------------------------------
class Bullet:
    
    def __init__(self, in_x, in_y, in_angle):
        self.x = in_x
        self.y = in_y
        self.angle = in_angle
        self.vx = cos(radians(in_angle)) * 10
        self.vy = sin(radians(in_angle)) * 10
        self.alive = True
        
        # Animation Properties
        self.frame_index = 0
        self.anim_counter = 0
        
    def display(self):
        self.x += self.vx
        self.y += self.vy
        
        # Animate Bullet
        self.anim_counter += 1
        if self.anim_counter % 5 == 0:
            self.frame_index = (self.frame_index + 1) % 4
        
        # Draw Bullet
        if bullet_sheet is not None:
            pushMatrix()
            translate(self.x, self.y)
            rotate(radians(self.angle + 90)) # Rotate to match travel direction
            
            scale_factor = 0.15 # Scale down significantly (140px -> ~21px)
            dw = BULLET_FRAME_W * scale_factor
            dh = BULLET_FRAME_H * scale_factor
            
            sx = self.frame_index * BULLET_FRAME_W
            sy = 0
            
            imageMode(CENTER)
            image(bullet_sheet, 0, 0, dw, dh, sx, sy, sx + BULLET_FRAME_W, sy + BULLET_FRAME_H)
            popMatrix()
        else:
            # Fallback
            fill(255, 0, 0)
            ellipse(self.x, self.y, 8, 8)
        
        if(self.x < 0 or self.x > width or self.y < 0 or self.y > height):
            self.alive = False

# ---------------------------------
# ASTEROID CLASS
# ---------------------------------
class Asteroid:
    
    def __init__(self, in_x = None, in_y = None, size_type = 'RANDOM'):
        
        if(size_type == 'RANDOM'):
            select = random.randint(1, 3)
            if(select == 1): self.type = 'SMALL'
            elif(select == 2): self.type = 'MEDIUM'
            else: self.type = 'LARGE'
        else:
            self.type = size_type

        if(self.type == 'SMALL'):
            self.diameter = 40
            self.score_val = 30
        elif(self.type == 'MEDIUM'):
            self.diameter = 60
            self.score_val = 20
        else: 
            self.diameter = 80
            self.score_val = 10

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

        self.alive = True
        
    def display(self):
        if(self.x > width + 100): self.x = -50
        if(self.x < -100): self.x = width + 50
        if(self.y > height + 100): self.y = -50
        if(self.y < -100): self.y = height + 50
        
        self.x = self.x + self.vx
        self.y = self.y + self.vy
        
        # Draw Asteroid Sprite
        img_to_draw = None
        if self.type == 'LARGE':
            img_to_draw = big_aster_img
        elif self.type == 'MEDIUM':
            img_to_draw = mid_aster_img
        elif self.type == 'SMALL':
            img_to_draw = small_aster_img
            
        if img_to_draw is not None:
            imageMode(CENTER)
            image(img_to_draw, self.x, self.y)
        else:
            # Fallback
            fill(255)
            ellipse(self.x, self.y, self.diameter, self.diameter)
        
# ---------------------------------
# SHOP CLASS
# ---------------------------------
class Shop:
    def __init__(self):
        self.products = [
            {"id": 1, "name": "Extra Heart", "price": 1000, "stock": 3, "max_stock": 3, "img": "heart"},
            {"id": 2, "name": "Speed Boost", "price": 2000, "stock": 1, "max_stock": 1, "img": "boost"},
            {"id": 3, "name": "Copper Ship", "price": 3000, "stock": 1, "max_stock": 1, "img": "copper"},
            {"id": 4, "name": "Silver Ship", "price": 4000, "stock": 1, "max_stock": 1, "img": "silver"},
            {"id": 5, "name": "Crystal Ship", "price": 5000, "stock": 1, "max_stock": 1, "img": "crystal"}
        ]
        self.buttons = [] 
        self.feedback_message = ""
        self.feedback_timer = 0

    def display(self):
        fill(0, 0, 0, 240)
        rectMode(CORNER)
        rect(0, 0, RES_WIDTH, RES_HEIGHT)
        
        textAlign(CENTER, TOP)
        fill(255)
        textSize(24)
        text("Press 'E' to EXIT", RES_WIDTH/2, 60)
        
        if millis() - self.feedback_timer < 2000:
            fill(255, 50, 50) 
            textSize(24)
            text(self.feedback_message, RES_WIDTH/2, 100)
        
        num_products = len(self.products)
        col_width = RES_WIDTH / num_products
        y_start = 300
        
        self.buttons = [] 
        
        for i in range(num_products):
            p = self.products[i]
            x_center = i * col_width + (col_width / 2)
            
            img_to_draw = None
            if p["img"] == "heart": img_to_draw = heart_img
            elif p["img"] == "boost": img_to_draw = boost_img
            elif p["img"] == "copper": img_to_draw = ship_sprite2
            elif p["img"] == "silver": img_to_draw = ship_sprite3
            elif p["img"] == "crystal": img_to_draw = ship_sprite4
            
            imageMode(CENTER)
            if img_to_draw is not None:
                if p["img"] == "heart": w, h = 80, 80
                elif p["img"] == "boost": w, h = 90, 90
                else: w, h = 80, 80 
                
                if p["img"] in ["copper", "silver", "crystal"]:
                    sx = 3 * SHIP_FRAME_W 
                    sy = 0
                    sw = SHIP_FRAME_W
                    sh = SHIP_FRAME_H
                    image(img_to_draw, x_center, y_start, w, h, sx, sy, sx + sw, sy + sh)
                else:
                    image(img_to_draw, x_center, y_start, w, h)
            else:
                fill(100)
                rect(x_center - 30, y_start - 30, 60, 60)
            
            price_y = y_start + 80
            coin_size = 24
            textSize(20)
            price_str = str(p["price"])
            price_w = textWidth(price_str)
            total_w = coin_size + 5 + price_w
            
            start_x_price = x_center - (total_w / 2)
            
            imageMode(CORNER)
            if coin_img:
                image(coin_img, start_x_price, price_y, coin_size, coin_size)
            fill(255, 255, 0)
            textAlign(LEFT, TOP)
            text(price_str, start_x_price + coin_size + 5, price_y + 4)
            
            stock_y = price_y + 40
            fill(255)
            textAlign(CENTER, TOP)
            textSize(15) 
            text(str(p["stock"]) + "/" + str(p["max_stock"]) + " in stock", x_center, stock_y)
            
            btn_y = stock_y + 40
            btn_w = 140
            btn_h = 40
            
            can_buy = game.score >= p["price"] and p["stock"] > 0
            
            if can_buy:
                fill(0, 200, 0)
            else:
                fill(100)
            
            rectMode(CENTER)
            rect(x_center, btn_y + btn_h/2, btn_w, btn_h)
            
            fill(255)
            textAlign(CENTER, CENTER)
            textSize(15) 
            if p["stock"] == 0:
                text("Sold Out", x_center, btn_y + btn_h/2)
            else:
                text("Upgrade", x_center, btn_y + btn_h/2)
            
            self.buttons.append({
                "rect": (x_center - btn_w/2, btn_y, btn_w, btn_h),
                "product_idx": i
            })

    def handle_click(self, mx, my):
        for btn in self.buttons:
            bx, by, bw, bh = btn["rect"]
            if bx <= mx <= bx + bw and by <= my <= by + bh:
                self.purchase(btn["product_idx"])

    def purchase(self, idx):
        p = self.products[idx]
        
        if p["stock"] <= 0: return
        
        if game.score < p["price"]: 
            self.feedback_message = "Insufficient Fund! Keep Going!"
            self.feedback_timer = millis()
            return
        
        game.score -= p["price"]
        p["stock"] -= 1
        
        current_wave = game.waves[game.wave]
        ship = current_wave.ship
        
        if p["id"] == 1: 
            current_wave.health += 1
        elif p["id"] == 2: 
            ship.thrust_power *= 2
        elif p["id"] == 3: 
            self.replace_ship(current_wave, CopperShip)
        elif p["id"] == 4: 
            self.replace_ship(current_wave, SilverShip)
        elif p["id"] == 5: 
            self.replace_ship(current_wave, CrystalShip)
            
        if upgrade_sound:
            upgrade_sound.play()
            
    def replace_ship(self, wave, NewShipClass):
        old_ship = wave.ship
        new_ship = NewShipClass(old_ship.x, old_ship.y, old_ship.friction)
        new_ship.angle = old_ship.angle
        new_ship.velocity_x = old_ship.velocity_x
        new_ship.velocity_y = old_ship.velocity_y
        new_ship.key_handler = old_ship.key_handler
        wave.ship = new_ship

class Game:
    
    def __init__(self):
        self.game_state = 'INTRO'
        self.waves = []
        self.enter = False
        self.last_shot_time = 0
        self.shop = Shop() 
        self.reset_game()
        self.key_states = {LEFT:False, RIGHT:False, UP:False, ' ':False, 'e':False, 'p':False, 'u':False}
        self.tutorial_thrust_playing = False
        
        # Intro Menu Buttons
        self.btn_bg = (RES_WIDTH/2 - 110, RES_HEIGHT/2 + 160, 220, 50)
        self.btn_tutorial = (RES_WIDTH/2 - 100, RES_HEIGHT/2 + 235, 200, 46)
        
        for i in range(11):
            self.waves.append(Wave(i))
        
    def reset_game(self): 
        self.wave = 1
        self.score = 0
        for p in self.shop.products:
            p["stock"] = p["max_stock"]
            
    def display_intro(self):
        if main_bg is not None:
            imageMode(CORNER)
            image(main_bg, 0, 0)
        else:
            background(20)
        
        textAlign(CENTER, CENTER)
        fill(255)
        textSize(60) 
        text("ASTEROIDS", RES_WIDTH / 2, RES_HEIGHT / 3.5)
        
        textSize(24)
        text("Press 'ENTER' to START", RES_WIDTH / 2, RES_HEIGHT / 2)
        
        bx, by, bw, bh = self.btn_bg
        if bx < mouseX < bx+bw and by < mouseY < by+bh:
            fill(100, 100, 255)
        else:
            fill(50, 50, 200)
        rectMode(CORNER)
        rect(bx, by, bw, bh, 10)
        fill(255)
        textSize(20)
        text("Background", bx + bw/2, by + bh/2 - 3)
        
        tx, ty, tw, th = self.btn_tutorial
        if tx < mouseX < tx+tw and ty < mouseY < ty+th:
            fill(100, 255, 100)
        else:
            fill(50, 200, 50)
        rect(tx, ty, tw, th, 10)
        fill(255)
        text("Tutorial", tx + tw/2, ty + th/2 - 3)
        
        textSize(12) 
        fill(150)
        textAlign(RIGHT, BOTTOM)
        text("Presented by John & Joy", RES_WIDTH - 20, RES_HEIGHT - 20)
        
        if(self.enter):
            self.waves[1] = Wave(1)
            self.game_state = 'PLAYING'

    def display_background_page(self):
        if main_bg is not None:
            imageMode(CORNER)
            image(main_bg, 0, 0)
        else:
            background(20)
            
        textAlign(CENTER, TOP)
        fill(255)
        textSize(24)
        text("Press 'E' to EXIT", RES_WIDTH / 2, 60)
            
        rectMode(CENTER)
        fill(0, 0, 0, 200)
        rect(RES_WIDTH/2, RES_HEIGHT/2, RES_WIDTH - 170, RES_HEIGHT - 170)
        
        story = ("You once traveled the stars with Lyra, mapping constellations and dreaming of crossing the galaxy together. "
                 "Then a cosmic rupture tore through your route, scattering 10 waves of unstable asteroids across her last known position. "
                 "Her signal faded, leaving only a faint heartbeat-like echo in the dark.\n\n"
                 "You cannot lose her.\n\n"
                 "To reach her, you must fly through all 10 waves of drifting asteroids, each faster and more crowded than the last. "
                 "Every asteroid you clear brings you one step closer to her pulse in the void.\n\n"
                 "You launch with one vow in your heart:\n"
                 "\"I’ll find you among the stars.\"")
        
        fill(255)
        textSize(20)
        textAlign(CENTER, CENTER)
        text(story, RES_WIDTH/2, RES_HEIGHT/2, RES_WIDTH - 250, RES_HEIGHT - 250)

    def display_tutorial_page(self):
        if tutorial_bg is not None:
            imageMode(CORNER)
            image(tutorial_bg, 0, 0)
        else:
            background(0)
            fill(255)
            textAlign(CENTER)
            text("Tutorial BG Missing", RES_WIDTH/2, RES_HEIGHT/2)
            
        textAlign(CENTER, TOP)
        fill(255)
        textSize(24)
        text("Press 'E' to EXIT", RES_WIDTH / 2, 150)
        
        textAlign(CENTER, CENTER)
        text("Press on to TRY", RES_WIDTH * 0.75, RES_HEIGHT * 0.5)

        fill(255, 255, 255, 51) 
        rectMode(CORNER)
        
        if self.key_states[LEFT]:
            rect(120, 326, 267-120, 601-326)
            
        if self.key_states[UP]:
            rect(286, 326, 471-286, 473-326)
            if thrust_sound is not None and not self.tutorial_thrust_playing:
                thrust_sound.loop()
                self.tutorial_thrust_playing = True
        else:
            if self.tutorial_thrust_playing:
                if thrust_sound is not None: thrust_sound.stop()
                self.tutorial_thrust_playing = False
            
        if self.key_states[' ']:
            rect(286, 497, 471-286, 601-497)
            
        if self.key_states[RIGHT]:
            rect(493, 326, 640-493, 601-326)
            
        if self.key_states['e']:
            rect(808, 239, 1079-808, 345-239)
            
        if self.key_states['p']:
            rect(784, 368, 1109-784, 473-368)
            
        if self.key_states['u']:
            rect(757, 497, 1144-757, 601-497)

    def display(self):
        
        # ------------------------------------------
        # INTRO STATE
        # ------------------------------------------
        if(self.game_state == 'INTRO'):
            self.display_intro()
            
        # ------------------------------------------
        # BACKGROUND STORY STATE
        # ------------------------------------------
        elif(self.game_state == 'BACKGROUND'):
            self.display_background_page()

        # ------------------------------------------
        # TUTORIAL STATE
        # ------------------------------------------
        elif(self.game_state == 'TUTORIAL'):
            self.display_tutorial_page()
            
        # ------------------------------------------
        # PLAYING STATE
        # ------------------------------------------
        elif(self.game_state == 'PLAYING'):

            imageMode(CORNER)
            if self.wave <= 2 and bg_wave1_2 is not None:
                image(bg_wave1_2, 0, 0)
            elif self.wave <= 4 and bg_wave3_4 is not None:
                image(bg_wave3_4, 0, 0)
            elif self.wave <= 7 and bg_wave5_7 is not None:
                image(bg_wave5_7, 0, 0)
            elif bg_wave7_10 is not None:
                image(bg_wave7_10, 0, 0)
            else:
                background(20)

            self.waves[self.wave].display()
            
            if(self.waves[self.wave].health <= 0):
                self.game_state = 'GAMEOVER'
                return 
            
            if(self.waves[self.wave].ending_detection() == True):
                current_health = self.waves[self.wave].health
                if(self.wave >= 10):
                    self.game_state = 'WIN'
                    return
                else: 
                    self.wave += 1
                    self.waves[self.wave] = Wave(self.wave)
                    self.waves[self.wave].health = current_health
            
            fill(255)
            textSize(25)
            textAlign(LEFT, TOP)
            
            margin_left = 65
            margin_top = 60
            row_height = 50 
            icon_size = 40  
            
            text("Wave " + str(self.wave), margin_left, margin_top)
            
            coin_y = margin_top + row_height - 8
            if coin_img is not None:
                imageMode(CORNER)
                image(coin_img, margin_left, coin_y, icon_size, icon_size)
                text(str(self.score), margin_left + icon_size + 10, coin_y + 8)
            else:
                text("Score: " + str(self.score), margin_left, coin_y)
            
            heart_y = coin_y + row_height
            if heart_img is not None:
                hearts_to_draw = self.waves[self.wave].health
                for i in range(hearts_to_draw):
                    x_pos = margin_left + (i * (icon_size + 10))
                    image(heart_img, x_pos, heart_y, icon_size, icon_size)

            textAlign(RIGHT, TOP)
            
            current_wave_obj = self.waves[self.wave]
            elapsed_sec = (millis() - current_wave_obj.start_time) / 1000.0
            remaining_time = current_wave_obj.duration - elapsed_sec
            if remaining_time < 0: remaining_time = 0
            
            text("Time: " + str(int(remaining_time)), RES_WIDTH - margin_left, margin_top)
            
            textSize(20)
            text("Press 'U' to UPGRADE", RES_WIDTH - margin_left, margin_top + 40)
            text("Press 'P' to PAUSE", RES_WIDTH - margin_left, margin_top + 70)

        # ------------------------------------------
        # SHOP STATE (Paused)
        # ------------------------------------------
        elif(self.game_state == 'SHOP'):
            imageMode(CORNER)
            if self.wave <= 2 and bg_wave1_2: image(bg_wave1_2, 0, 0)
            elif self.wave <= 4 and bg_wave3_4: image(bg_wave3_4, 0, 0)
            elif self.wave <= 7 and bg_wave5_7: image(bg_wave5_7, 0, 0)
            elif bg_wave7_10: image(bg_wave7_10, 0, 0)
            
            self.shop.display()

        # ------------------------------------------
        # PAUSED STATE
        # ------------------------------------------
        elif(self.game_state == 'PAUSED'):
            imageMode(CORNER)
            if self.wave <= 2 and bg_wave1_2: image(bg_wave1_2, 0, 0)
            elif self.wave <= 4 and bg_wave3_4: image(bg_wave3_4, 0, 0)
            elif self.wave <= 7 and bg_wave5_7: image(bg_wave5_7, 0, 0)
            elif bg_wave7_10: image(bg_wave7_10, 0, 0)
            
            fill(0, 0, 0, 150)
            rectMode(CORNER)
            rect(0, 0, RES_WIDTH, RES_HEIGHT)
            
            textAlign(CENTER, CENTER)
            fill(255)
            textSize(50)
            text("PAUSED", RES_WIDTH/2, RES_HEIGHT/2 - 20)
            textSize(24)
            text("Press 'P' to RESUME", RES_WIDTH/2, RES_HEIGHT/2 + 40)

        # ------------------------------------------
        # GAMEOVER STATE
        # ------------------------------------------
        elif(self.game_state == "GAMEOVER"):
            background(0)
            textAlign(CENTER, TOP)
            fill(255)
            textSize(24)
            text("GAME OVER", RES_WIDTH / 2, RES_HEIGHT / 2 - 50)
            text("Final Coins: " + str(self.score), RES_WIDTH / 2, RES_HEIGHT / 2)
            text("Press 'ENTER' to RESTART", RES_WIDTH / 2, RES_HEIGHT / 2 + 50)
            
            if self.enter:
                 self.reset_game()
                 self.waves[1] = Wave(1) 
                 self.game_state = 'PLAYING'
        
        # ------------------------------------------
        # WIN STATE
        # ------------------------------------------
        elif(self.game_state == "WIN"):
            background(0)
            textAlign(CENTER, TOP)
            fill(255)
            textSize(32)
            text("Congrats", RES_WIDTH / 2, RES_HEIGHT / 2 - 50)
            textSize(24)
            text("Final Coins: " + str(self.score), RES_WIDTH / 2, RES_HEIGHT / 2)
            text("Press 'ENTER' to RESTART", RES_WIDTH / 2, RES_HEIGHT / 2 + 50)
            
            if self.enter:
                 self.reset_game()
                 self.waves[1] = Wave(1) 
                 self.game_state = 'PLAYING'
        
    def append_bullets(self):
        if (millis() - self.last_shot_time >= 150):
            ship_obj = self.waves[self.wave].ship
            angle_rad = radians(ship_obj.angle)
            nose_offset = 40
            start_x = ship_obj.x + cos(angle_rad) * nose_offset
            start_y = ship_obj.y + sin(angle_rad) * nose_offset
            self.waves[self.wave].bullets.append(Bullet(start_x, start_y, ship_obj.angle))
            self.last_shot_time = millis()
            if bullet_sound is not None:
                bullet_sound.play()
        
    def directional_signal(self, in_direction,in_option):
        self.waves[self.wave].ship.key_handler[in_direction] = in_option
        
    def ENTER_signal(self, in_option):
        if(in_option):
            self.enter = True
        else:
            self.enter = False
            
    def toggle_shop(self):
        if self.game_state == 'PLAYING':
            self.game_state = 'SHOP'
        elif self.game_state == 'SHOP':
            self.game_state = 'PLAYING'
            
    def toggle_pause(self):
        if self.game_state == 'PLAYING':
            self.game_state = 'PAUSED'
        elif self.game_state == 'PAUSED':
            self.game_state = 'PLAYING'
    
    def handle_click_intro(self, mx, my):
        # Background Button
        bx, by, bw, bh = self.btn_bg
        if bx < mx < bx+bw and by < my < by+bh:
            self.game_state = 'BACKGROUND'
            return

        # Tutorial Button
        tx, ty, tw, th = self.btn_tutorial
        if tx < mx < tx+tw and ty < my < ty+th:
            self.game_state = 'TUTORIAL'
            return

class Wave:

    def __init__(self, in_wave_number):      
        self.bullets = []
        self.asteroids = []
        self.wave_number = in_wave_number
        self.asteroids_num = self.wave_number * 3
        
        self.duration = 30 + (in_wave_number - 1) * 5
        self.start_time = millis() 

        self.ship = Ship(RES_WIDTH/2, RES_HEIGHT/2, 0.98) 
        self.last_spawntime = 0
        self.health = 3
        
    def display(self):      
        if(millis() - self.last_spawntime > 3000 and self.asteroids_num > 0):
            self.asteroids.append(Asteroid())
            self.asteroids_num = self.asteroids_num - 1
            self.last_spawntime = millis()
            
        self.ship.display()
        
        for bullet in self.bullets[:]:
            bullet.display()
            if(bullet.alive == False): 
                self.bullets.remove(bullet)
        
        for asteroid in self.asteroids[:]:
            asteroid.display()
            
            min_dist_ship = (asteroid.diameter / 2) + (self.ship.diameter / 2)
            if dist(asteroid.x, asteroid.y, self.ship.x, self.ship.y) < min_dist_ship:
                self.health -= 1
                asteroid.alive = False
                if ship_crash_sound is not None:
                    ship_crash_sound.play()

            for bullet in self.bullets:
                if(bullet.alive and dist(asteroid.x, asteroid.y, bullet.x, bullet.y) < asteroid.diameter / 2 + 5):
                    asteroid.alive = False
                    bullet.alive = False
                    game.score += asteroid.score_val
                    
                    if(asteroid.type == 'LARGE'):
                        self.asteroids.append(Asteroid(asteroid.x-10, asteroid.y-10, 'MEDIUM'))
                        self.asteroids.append(Asteroid(asteroid.x+10, asteroid.y+10, 'MEDIUM'))
                    elif(asteroid.type == 'MEDIUM'):
                        self.asteroids.append(Asteroid(asteroid.x-10, asteroid.y-10, 'SMALL'))
                        self.asteroids.append(Asteroid(asteroid.x+10, asteroid.y+10, 'SMALL'))
            
            if(asteroid.alive == False): 
               self.asteroids.remove(asteroid)
        
    def ending_detection(self):
        elapsed_ms = millis() - self.start_time
        if elapsed_ms > self.duration * 1000:
            return True
        if(len(self.asteroids) == 0 and self.asteroids_num <= 0):
            return True
        return False
    

game = Game()

def setup():
    global main_bg, bg_wave1_2, bg_wave3_4, bg_wave5_7, bg_wave7_10
    global ship_sheet1, heart_img, coin_img, pixel_font
    global bgm, bullet_sound, thrust_sound, ship_crash_sound
    global boost_img, ship_sprite2, ship_sprite3, ship_sprite4, upgrade_sound
    global tutorial_bg
    global big_aster_img, mid_aster_img, small_aster_img, bullet_sheet

    size(RES_WIDTH, RES_HEIGHT)
    noStroke()

    try:
        main_bg = loadImage("assets/MainBG.png")
        if main_bg: main_bg.resize(RES_WIDTH, RES_HEIGHT)
        
        # Load Tutorial BG
        tutorial_bg = loadImage("assets/Tutorial.png")
        if tutorial_bg: tutorial_bg.resize(RES_WIDTH, RES_HEIGHT)
        
        bg_wave1_2 = loadImage("assets/Wave1-2BG.png")
        if bg_wave1_2: bg_wave1_2.resize(RES_WIDTH, RES_HEIGHT)
        
        bg_wave3_4 = loadImage("assets/Wave3-4BG.png")
        if bg_wave3_4: bg_wave3_4.resize(RES_WIDTH, RES_HEIGHT)
        
        bg_wave5_7 = loadImage("assets/Wave5-7BG.png")
        if bg_wave5_7: bg_wave5_7.resize(RES_WIDTH, RES_HEIGHT)
        
        bg_wave7_10 = loadImage("assets/Wave7-10BG.png")
        if bg_wave7_10: bg_wave7_10.resize(RES_WIDTH, RES_HEIGHT)

        ship_sheet1 = loadImage("assets/ShipSprite1.png")
        heart_img = loadImage("assets/Heart.png")
        coin_img = loadImage("assets/Coin.png")
        pixel_font = createFont("assets/PressStart2P-Regular.ttf", 24)
        textFont(pixel_font)
        
        boost_img = loadImage("assets/BoostPotion.png")
        ship_sprite2 = loadImage("assets/ShipSprite2.png")
        ship_sprite3 = loadImage("assets/ShipSprite3.png")
        ship_sprite4 = loadImage("assets/ShipSprite4.png")
        
        # Load Asteroids and Bullets
        big_aster_img = loadImage("assets/BigAster.png")
        if big_aster_img: big_aster_img.resize(80, 80)

        mid_aster_img = loadImage("assets/MidAster.png")
        if mid_aster_img: mid_aster_img.resize(60, 60)

        small_aster_img = loadImage("assets/SmallAster.png")
        if small_aster_img: small_aster_img.resize(40, 40)
        
        bullet_sheet = loadImage("assets/BulletSprite.png")
        
    except:
        print("Error loading images")

    try:
        bgm = SoundFile(this, "assets/BackgroundMusic.mp3")
        bgm.loop()
        bullet_sound = SoundFile(this, "assets/BulletHit.mp3")
        thrust_sound = SoundFile(this, "assets/Throttling.mp3")
        ship_crash_sound = SoundFile(this, "assets/ShipCrash.mp3")
        upgrade_sound = SoundFile(this, "assets/Upgrade.mp3")
    except Exception as e:
        print("Sound loading error:", e)

def draw():
    background(0)
    game.display()

def mousePressed():
    if game.game_state == 'SHOP':
        game.shop.handle_click(mouseX, mouseY)
    elif game.game_state == 'INTRO':
        game.handle_click_intro(mouseX, mouseY)

def keyPressed():
    # Update Key States for Tutorial
    if keyCode in [LEFT, RIGHT, UP]:
        game.key_states[keyCode] = True
    elif key in [' ', 'e', 'p', 'u']:
        game.key_states[key.lower()] = True
        
    if key == ' ': game.append_bullets()
    if key == ENTER: game.ENTER_signal(True)
    if keyCode == LEFT: game.directional_signal(LEFT,True)
    if keyCode == RIGHT: game.directional_signal(RIGHT,True)
    if keyCode == UP: game.directional_signal(UP,True)
    
    # Shop Controls
    if key == 'u' or key == 'U':
        if game.game_state == 'PLAYING':
            game.toggle_shop()
            
    if key == 'e' or key == 'E':
        if game.game_state == 'SHOP':
            game.toggle_shop()
        elif game.game_state in ['BACKGROUND', 'TUTORIAL']:
            # Stop tutorial sound if currently playing
            if game.tutorial_thrust_playing:
                if thrust_sound is not None: thrust_sound.stop()
                game.tutorial_thrust_playing = False
            game.game_state = 'INTRO'
            
    # Pause Controls
    if key == 'p' or key == 'P':
        game.toggle_pause()

def keyReleased():
    # Update Key States for Tutorial
    if keyCode in [LEFT, RIGHT, UP]:
        game.key_states[keyCode] = False
    elif key in [' ', 'e', 'p', 'u']:
        game.key_states[key.lower()] = False

    if key == ENTER: game.ENTER_signal(False)
    if keyCode == LEFT: game.directional_signal(LEFT, False)
    if keyCode == RIGHT: game.directional_signal(RIGHT, False)
    if keyCode == UP: game.directional_signal(UP, False)
