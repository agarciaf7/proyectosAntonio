# JuegoVida. Ver nota JuegoVida en Evernote
import pgzrun
import copy
import time

WIDTH = 600
HEIGHT = 600
LADO = 20 # Lado de cada celda en px
NUM_FILAS = int(HEIGHT / LADO)
NUM_COLUMNAS = int(WIDTH / LADO)
RED = 200, 0, 0
DELAY = 10 #delay de reproducción del bucle en segundos

ciclos = 0 #cuenta el número de generaciones que pasan

# Inicializo matriz https://www.snakify.org/es/lessons/two_dimensional_lists_arrays/
a = [[False] * NUM_COLUMNAS for i in range(NUM_FILAS)]

def devolverCoordenadasCeldasAlrededor(x, y):
    return [[x-1, y-1], [x, y-1], [x+1, y-1], [x-1, y], [x+1, y], [x-1, y+1], [x, y+1], [x+1, y+1]]

def verVidaEnCelda(x, y, matriz):
    """Nos devuelve si la celda x,y está viva o no mirando las de alrededor"""
    retorno = False
    celdasVivasAlrededor = 0
    coordenadasCeldasAlrededor = devolverCoordenadasCeldasAlrededor(x, y)
    print('Analizo x='+str(x) + 'y=' + str(y) + ' que esta ' + str(matriz[x][y]))
    for c in coordenadasCeldasAlrededor:
        print ('Analizamos alrededor='+ str(c))
        try:
            print('Alrededor x='+str(c[0]) + 'y=' + str(c[1]))
            if (int(c[0]) > 0) and (int(c[1]) > 0) and (matriz[int(c[0])][int(c[1])]):
                celdasVivasAlrededor+=1
                print('viva')
            else:
#                pass
                print('muerta')
        except IndexError:
            pass
#            print('IndexError en x=' + str(c[0]) + 'y=' + str(c[1]))
    
    if not matriz[x][y] and celdasVivasAlrededor == 3: # Una célula muerta con exactamente 3 células vecinas vivas "nace"
        retorno = True # Nace la célula
    elif matriz[x][y] and 2 <= celdasVivasAlrededor <= 3: # Una célula viva con 2 o 3 células vecinas vivas sigue viva, en otro caso muere
        retorno = True # Continúa viva la célula
    else:
        retorno = False # En otro caso muere
    print('celdasVivasAlrededor='+str(celdasVivasAlrededor)+ ' retorno=' + str(retorno))    
    return retorno

def verVidaEnTodasLasCeldas():
    print('En verVidaEnTodasLasCeldas')
    oldMatriz=copy.deepcopy(a)

#    for x in range(NUM_COLUMNAS):
#        for y in range(NUM_FILAS):
    for x in range(5):
        for y in range(5):            
            a[x][y] = verVidaEnCelda(x, y, oldMatriz)
#            print('x=' + str(x) + ' y=' + str(y) +' old/a='+str(oldMatriz[x][y]) + '/' + str(a[x][y]))
#        print()    

def draw(): # Pygame Zero draw function
    print('En draw')
    screen.fill((0, 0, 0))
    
    #PINTO EL TABLERO COMPLETO (las coordenadas son columna, fila)
    for x in range(NUM_COLUMNAS):
        for y in range(NUM_FILAS):
            dibujaCelda(x, y, LADO, RED)

 
    
def update(): # Pygame Zero update function
#    print('Pulsa Enter')
#    foo = input() # Esperamos a que teclee cualquier cosa
    global ciclos
    print('En update')
    ciclos +=1
    checkKeys()
    if ciclos > 1:
        verVidaEnTodasLasCeldas()
        time.sleep(DELAY)    

def checkKeys():
    pass
#    global player
#    if keyboard.left:
#        if player.x > 40: player.x -= 5
#    if keyboard.right:
#        if player.x < 760: player.x += 5

def dibujaCelda(x, y, lado, color):
    if a[x][y]:
        screen.draw.filled_rect(Rect((x*lado, y*lado), (lado, lado)), color)
        
        
def inicializacion1():
    # Para pruebas inicializo diagonal a unos
    for i in range(NUM_FILAS): 
        a[i][i] = True
    a[1][2]=True
    a[2][1]=True
    
def inicializacion2():
    # Para pruebas inicializo diagonal con el patrón glider (planeador)
    a[0][1]=True
    a[1][2]=True
    a[2][2]=True
    a[0][3]=True
    a[1][3]=True


##################################################################################
        
inicializacion2()       

##################################################################################
pgzrun.go()