import random
import time
import threading
import pygame
import sys


evQueue = [] 
evActive = {'right': False, 'down': False, 'left': False, 'up': False}
savedGreenTime = 0
currentGreen = 0 
currentYellow = 0
noOfSignals = 4
timeElapsed = 0

defaultGreen = {0: 90, 1: 10, 2: 10, 3: 10}
defaultYellow = 5
gap = 40 

signals = []
speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.5, 'ambulance': 1.8}

x = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}
stopLines = {'right': 590, 'down': 330, 'left': 810, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 820, 'up': 545}

redLinePos = {'up': 680, 'down': 120, 'left': 1000, 'right': 400}
roadStart, roadEnd = 580, 820 

vehicles = {'right': {0:[], 1:[], 2:[]}, 'down': {0:[], 1:[], 2:[]}, 'left': {0:[], 1:[], 2:[]}, 'up': {0:[], 1:[], 2:[]}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}
directionToIndex = {'right': 0, 'down': 1, 'left': 2, 'up': 3}

signalCoods = [(530,230),(810,230),(810,570),(530,570)]
signalTimerCoods = [(530,210),(810,210),(810,550),(530,550)]

pygame.init()
simulation = pygame.sprite.Group()
ambulance_group = pygame.sprite.Group() 
font = pygame.font.Font(None, 35)

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        try:
            self.image = pygame.image.load(f"images/{direction}/{vehicleClass}.png")
        except:
            self.image = pygame.Surface((45, 25)); self.image.fill((100, 100, 100))
        self.stop = defaultStop[direction]
        vehicles[direction][lane].append(self)
        simulation.add(self)

    def check_collision(self):
        if isinstance(self, Ambulance): return False
        lane_list = vehicles[self.direction][self.lane]
        idx = lane_list.index(self)
        if idx > 0:
            lead = lane_list[idx-1]
            if self.direction == 'up' and self.y - self.speed < lead.y + lead.image.get_rect().height + gap: return True
            if self.direction == 'down' and self.y + self.image.get_rect().height + self.speed > lead.y - gap: return True
            if self.direction == 'right' and self.x + self.image.get_rect().width + self.speed > lead.x - gap: return True
            if self.direction == 'left' and self.x - self.speed < lead.x + lead.image.get_rect().width + gap: return True
        return False

    def move(self):
        if self.check_collision(): return
        target_idx = directionToIndex[self.direction]
        if self.direction == 'up':
            if self.crossed == 0 and (currentGreen != target_idx or currentYellow == 1) and (self.y <= self.stop + 5 and self.y >= self.stop): return
            self.y -= self.speed
            if self.y < stopLines['up']: self.crossed = 1
        elif self.direction == 'right':
            if self.crossed == 0 and (currentGreen != target_idx or currentYellow == 1) and (self.x + self.image.get_rect().width >= self.stop - 5 and self.x + self.image.get_rect().width <= self.stop): return
            self.x += self.speed
            if self.x > stopLines['right']: self.crossed = 1
        elif self.direction == 'down':
            if self.crossed == 0 and (currentGreen != target_idx or currentYellow == 1) and (self.y + self.image.get_rect().height >= self.stop - 5 and self.y + self.image.get_rect().height <= self.stop): return
            self.y += self.speed
            if self.y > stopLines['down']: self.crossed = 1
        elif self.direction == 'left':
            if self.crossed == 0 and (currentGreen != target_idx or currentYellow == 1) and (self.x >= self.stop - 5 and self.x <= self.stop): return
            self.x -= self.speed
            if self.x < stopLines['left']: self.crossed = 1

class Ambulance(Vehicle):
    def __init__(self, direction):
        self.triggered = False 
        super().__init__(1, 'ambulance', direction)
        self.image = pygame.image.load(f"images/{direction}/ev.png")
        ambulance_group.add(self)

    def move(self):
        global evQueue, savedGreenTime, currentGreen
        if not self.triggered:
            if (self.direction == 'up' and self.y < redLinePos['up']) or \
               (self.direction == 'left' and self.x < redLinePos['left']):
                if not evQueue: savedGreenTime = signals[0].green
                evQueue.append(self.direction)
                self.triggered = True

        target_idx = directionToIndex[self.direction]
        if evQueue and evQueue[0] == self.direction:
            if currentGreen != target_idx:
                if self.direction == 'up' and self.y <= self.stop + 5 and self.y >= self.stop: return
                if self.direction == 'left' and self.x >= self.stop - 5 and self.x <= self.stop: return
        else:
            if self.direction == 'up' and self.y <= self.stop + 5 and self.y >= self.stop: return
            if self.direction == 'left' and self.x >= self.stop - 5 and self.x <= self.stop: return

        if self.check_collision(): return
        if self.direction == 'up': self.y -= self.speed
        elif self.direction == 'left': self.x -= self.speed

       
        cleared = (self.direction == 'up' and self.y < stopLines['up'] - 180) or \
                  (self.direction == 'left' and self.x < stopLines['left'] - 180)
        
        if cleared and evQueue and evQueue[0] == self.direction:
            evQueue.pop(0) 
        
        if self.y < -100 or self.x < -100: self.kill()

def initialize():
    signals.append(TrafficSignal(0, defaultYellow, 90))
    for i in range(1, 4): signals.append(TrafficSignal(150, defaultYellow, 10))
    
    def controller():
        global currentGreen, currentYellow, evQueue, savedGreenTime
        while True:
            if evQueue:
                
                currentYellow = 1; time.sleep(5); currentYellow = 0
                while evQueue:
                    currentGreen = directionToIndex[evQueue[0]]
                    active_ev = evQueue[0]

                    while evQueue and evQueue[0] == active_ev: time.sleep(0.1)
                    
                    
                    if evQueue:
                        currentYellow = 1; time.sleep(5); currentYellow = 0
                
                
                currentYellow = 1; time.sleep(2); currentYellow = 0
                currentGreen = 0; signals[0].green = savedGreenTime
            else:
                while signals[currentGreen].green > 0 and not evQueue:
                    time.sleep(1); signals[currentGreen].green -= 1
                if not evQueue:
                    currentYellow = 1; time.sleep(defaultYellow); currentYellow = 0
                    currentGreen = (currentGreen + 1) % noOfSignals
                    signals[currentGreen].green = defaultGreen[currentGreen]
    threading.Thread(target=controller, daemon=True).start()

def spawn_logic():
    global timeElapsed, evActive
    while True:
        if timeElapsed == 10 and not evActive['up']:
            Ambulance('up'); evActive['up'] = True
        if timeElapsed == 13 and not evActive['left']:
            Ambulance('left'); evActive['left'] = True
        Vehicle(random.randint(0, 2), vehicleTypes[random.randint(0, 3)], directionNumbers[random.randint(0, 3)])
        time.sleep(1.2)

initialize()
threading.Thread(target=spawn_logic, daemon=True).start()
threading.Thread(target=lambda: (exec("global timeElapsed\nwhile True:\n time.sleep(1)\n timeElapsed += 1")), daemon=True).start()

screen = pygame.display.set_mode((1400, 800))
bg = pygame.image.load('images/intersection.png')
signal_imgs = [pygame.image.load('images/signals/red.png'), pygame.image.load('images/signals/yellow.png'), pygame.image.load('images/signals/green.png')]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
    screen.blit(bg, (0,0))
    pygame.draw.line(screen, (255, 0, 0), (roadStart, redLinePos['up']), (roadEnd, redLinePos['up']), 5)
    pygame.draw.line(screen, (255, 0, 0), (redLinePos['left'], 330), (redLinePos['left'], 500), 5)
    for i in range(noOfSignals):
        # UI logic for Yellow Transitions
        if currentYellow == 1:
            if evQueue and (i == directionToIndex[evQueue[0]] or (i == 0 and not evQueue)): img = signal_imgs[1]
            elif i == currentGreen: img = signal_imgs[1]
            else: img = signal_imgs[0]
            t = "5"
        elif i == currentGreen:
            img = signal_imgs[2]; t = signals[i].green if not evQueue else "---"
        else: img = signal_imgs[0]; t = "---"
        screen.blit(img, signalCoods[i]); screen.blit(font.render(str(t), True, (255, 255, 255)), signalTimerCoods[i])
    for v in simulation:
        if v not in ambulance_group: v.move(); screen.blit(v.image, (v.x, v.y))
    for a in ambulance_group: a.move(); screen.blit(a.image, (a.x, a.y))
    pygame.display.update()