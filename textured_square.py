# https://gist.github.com/davepape/6773405

import sys, time, math, os, random
from pyglet.gl import *

window = pyglet.window.Window()
keyboard = pyglet.window.key.KeyStateHandler()
window.push_handlers(keyboard)


class TexturedSquare:
    def __init__(self, width, height, xpos, ypos, texturefile):
        self.xpos = xpos
        self.ypos = ypos
        self.angle = 0
        self.size = 1
        self.texture = pyglet.image.load(texturefile).get_texture()
        x = width / 2.0
        y = height / 2.0
        self.vlist = pyglet.graphics.vertex_list(4, ('v2f', [-x, -y, x, -y, -x, y, x, y]),
                                                 ('t2f', [0, 0, 1, 0, 0, 1, 1, 1]))

    def draw(self):
        glPushMatrix()
        glTranslatef(self.xpos, self.ypos, 0)
        glRotatef(self.angle, 0, 0, 1)
        glScalef(self.size, self.size, self.size)
        glColor3f(1, 1, 1)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        self.vlist.draw(GL_TRIANGLE_STRIP)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()


@window.event
def on_draw():
    glClearColor(0, 0.3, 0.5, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    square1.draw()


def update(dummy):
    global square1
    if keyboard[pyglet.window.key.A]:
        square1.xpos -= 5
    if keyboard[pyglet.window.key.D]:
        square1.xpos += 5
    if keyboard[pyglet.window.key.W]:
        square1.ypos += 5
    if keyboard[pyglet.window.key.S]:
        square1.ypos -= 5
    if keyboard[pyglet.window.key.UP]:
        square1.size *= 1.1
    if keyboard[pyglet.window.key.DOWN]:
        square1.size /= 1.1
    if keyboard[pyglet.window.key.LEFT]:
        square1.angle += 5
    if keyboard[pyglet.window.key.RIGHT]:
        square1.angle -= 5


square1 = TexturedSquare(120, 120, 300, 200, "dirt.png")

pyglet.clock.schedule_interval(update, 1 / 60.0)
pyglet.app.run()