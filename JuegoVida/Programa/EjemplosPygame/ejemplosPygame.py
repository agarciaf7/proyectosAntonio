import pgzrun

WIDTH = 400
HEIGHT = 400
RED = 200, 0, 0
OTRO = 100, 0, 0
#BOX = Rect((20, 20), (100, 100))
BOX = Rect((80, 40), (20, 20))
BOX1 = Rect((80, 60), (20, 20))
#BOX1 = Rect((200, 300), (250, 350))


player = Actor("player", (400, 400)) # Load in the player Actor image

def draw(): # Pygame Zero draw function
#    screen.blit('background', (0, 0))
    screen.fill((128, 128, 128))
    player.draw()
#    screen.draw.text("X", (20, 20))
#    screen.draw.text("X", (100, 100))
#    screen.draw.textbox("X", ((20, 20),(100, 100)))
    screen.draw.rect(BOX, RED)
#    screen.draw.rect(BOX1, OTRO)
    screen.draw.filled_rect(BOX1, OTRO)
    
def update(): # Pygame Zero update function
    checkKeys()

def checkKeys():
    global player
    if keyboard.left:
        if player.x > 40: player.x -= 5
    if keyboard.right:
        if player.x < 760: player.x += 5

pgzrun.go()