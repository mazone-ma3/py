
x = 10
y = 50

from pyxel import *

init(128,128)
load("my_resource.pyxres")

while True:
	if btn(KEY_SPACE):
		play(0,0)

	cls(6)
	text(10,60,"HELLO",5)

	if btn(KEY_RIGHT):
		x+=1
	if btn(KEY_LEFT):
		x-=1
	if btn(KEY_UP):
		y-=1
	if btn(KEY_DOWN):
		y+=1

	blt(x,y,   0,   0,0,  8,8,   0)

	flip()
