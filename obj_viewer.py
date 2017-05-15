# http://www.poketcode.com/pyglet_demos.html
"""
Added:
    - world container of models
    - multiple models in scene
    - independent movement of different models
    - solid wireframes
    - depth check on object drawing order
    - independent movement of scene and models - in progress
    - groundplane & sky
    - height lines
    - texture on ground plane
"""


import os
import copy
import random
import math
import pyglet
from pyglet.gl import gl
from pyglet.gl import glu

# TODO: Camera view all objects in scene
# TODO: Camera adjust view to fit both objects (while locked to one)
# TODO: add model + texture
# TODO: add direction vector to model
# TODO: prevent camera to go below ground plane

# constants
UPDATE_RATE = 100  # Hz

# colors
black = (0, 0, 0, 1)
dark_gray = (.75, .75, .75, 1)
white = (1, 1, 1, 1)
ground = (0.26, 0.47, 0.13, 1)
ground_line = (0, 0, 0, 1)
sky = (0.5, 0.7, 1, 1)

class World:
    """
    Collection of OBJ models within the larger simulation.
    """

    def __init__(self, coords, models=None, background_color=sky):

        # sets the background color
        gl.glClearColor(*background_color)

        [self.x, self.y, self.z] = coords
        self.rx = self.ry = self.rz = 0

        self.cx, self.cy, self.cz = 0, 0, 0

        if models is None:
            self.models = []
        else:
            if type(models) is list:
                self.models = models
            else:
                self.models = list(models)
        self.tex = pyglet.image.load('grass_top.png').get_texture()

    def draw(self):
        # clears the screen with the background color
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        gl.glLoadIdentity()

        # # sets the position
        gl.glTranslatef(self.x, self.y, self.z)

        # sets the rotation
        gl.glRotatef(self.rx, 1, 0, 0)
        gl.glRotatef(self.ry, 0, 1, 0)
        gl.glRotatef(self.rz, 0, 0, 1)

        self.draw_ground_plane()

        for model in self.models:
            self._model_render(model)

    def draw_ground_line(self,model):
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        gl.glColor4f(*ground_line)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v3f', (model.x - self.cx, model.y - self.cy, model.z - self.cz,  model.x - self.cx, -self.cy, model.z - self.cz)))

    def draw_ground_plane(self):
        size = 100

        gl.glPushMatrix()
        gl.glColor3f(1, 1, 1) # no textures drawn without this for some reason
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex.id)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST) # you need two
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST) # I don't know why!

        pos = ('v3f', (-size, -self.cy, -size, size, -self.cy, -size, size, -self.cy, size, -size, -self.cy, size))
        tex_coords = ('t2f', (0, 0, 1, 0, 1, 1, 0, 1))
        vlist = pyglet.graphics.vertex_list(4, pos, tex_coords)
        vlist.draw(gl.GL_QUADS)

        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glPopMatrix()

    def _model_render(self,model):

        # sets fill mode
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

        # draws the current model
        self._model_draw(model)

        # sets wire-frame mode
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

        # draws the current model
        temp_color = model.color
        model.color = white
        self._model_draw(model)
        model.color = temp_color

    def _model_draw(self, model):
        # gl.glLoadIdentity()
        gl.glPushMatrix()

        # sets the color
        gl.glColor4f(*model.color)

        # sets the position
        gl.glTranslatef(model.x - self.cx, model.y - self.cy, model.z - self.cz)

        # sets the rotation
        gl.glRotatef(model.rx, 1, 0, 0)
        gl.glRotatef(model.ry, 0, 1, 0)
        gl.glRotatef(model.rz, 0, 0, 1)

        # sets the scale
        gl.glScalef(model.scale, model.scale, model.scale)

        # draws the quads
        pyglet.graphics.draw_indexed(len(model.vertices) // 3, gl.GL_QUADS, model.quad_indices,
                                     ('v3f', model.vertices))

        # draws the triangles
        pyglet.graphics.draw_indexed(len(model.vertices) // 3, gl.GL_TRIANGLES, model.triangle_indices,
                                     ('v3f', model.vertices))

        gl.glPopMatrix()
        self.draw_ground_line(model)

    def update(self, dt):
        count = 0
        for model in self.models:
            count += 1
            if count == 1:
                model.rx += 10 / UPDATE_RATE
            elif count == 2:
                model.ry += 10 / UPDATE_RATE
            else:
                model.rz += 10 / UPDATE_RATE
                model.y -= 0.1 / UPDATE_RATE
        # print(dt)


class OBJModel:
    """
    Represents an OBJ model.
    """

    def __init__(self, coords=(0, 0, 0), scale = 1, color=dark_gray, path=None):
        self.vertices = []
        self.quad_indices = []
        self.triangle_indices = []

        # translation and rotation values
        [self.x, self.y, self.z] = coords
        self.rx = self.ry = self.rz = 0
        self.scale = scale

        # color of the model
        self.color = color

        # if path is provided
        if path:
            self.load(path)

    def clear(self):
        self.vertices = self.vertices[:]
        self.quad_indices = self.quad_indices[:]
        self.triangle_indices = self.triangle_indices[:]

    def load(self, path):
        self.clear()

        with open(path) as obj_file:
            for line in obj_file.readlines():
                # reads the file line by line
                data = line.split()

                # every line that begins with a 'v' is a vertex
                if data[0] == 'v':
                    # loads the vertices
                    x, y, z = data[1:4]
                    self.vertices.extend((float(x), float(y), float(z)))

                # every line that begins with an 'f' is a face
                elif data[0] == 'f':
                    # loads the faces
                    for f in data[1:]:
                        if len(data) == 5:
                            # quads
                            # Note: in obj files the first index is 1, so we must subtract one for each
                            # retrieved value
                            vi_1, vi_2, vi_3, vi_4 = data[1:5]
                            self.quad_indices.extend((int(vi_1) - 1, int(vi_2) - 1, int(vi_3) - 1, int(vi_4) - 1))

                        elif len(data) == 4:
                            # triangles
                            # Note: in obj files the first index is 1, so we must subtract one for each
                            # retrieved value
                            vi_1, vi_2, vi_3 = data[1:4]
                            self.triangle_indices.extend((int(vi_1) - 1, int(vi_2) - 1, int(vi_3) - 1))


class Window(pyglet.window.Window):
    """
    Takes care of all the viewing functionality
    """

    def __init__(self, *args, ** kwargs):
        super().__init__(*args, **kwargs)

        # pre-loaded models
        self.model_names = ['box.obj', 'uv_sphere.obj', 'monkey.obj']
        self.models = []

        for name in self.model_names:
            self.models.append(OBJModel((0, 0, 0), color=dark_gray, path=os.path.join('obj', name)))

        # # current model
        self.model_index = 0
        # self.current_model = self.models[self.model_index]

        sphere1 = copy.deepcopy(self.models[0])
        sphere2 = copy.deepcopy(self.models[0])
        sphere3 = copy.deepcopy(self.models[0])

        sphere1.x, sphere1.y, sphere1.z = [-1, 2, -3.5]
        sphere1.color = (1, 0, 0, 1)
        sphere1.scale = 0.5
        sphere2.x, sphere2.y, sphere2.z = [1, 2, -3.5]
        sphere2.color = (0, 0, 1, 1)

        sphere3.x, sphere3.y, sphere3.z = [2, 4, 2]
        sphere3.color = (1, 1, 0, 1)
        sphere3.scale = 0.1

        self.world = World([0, 0, -5])
        self.world.models.append(sphere1)
        self.world.models.append(sphere2)
        self.world.models.append(sphere3)

        @self.event
        def on_resize(width, height):
            # sets the viewport
            gl.glViewport(0, 0, width, height)

            # sets the projection
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            # gluPerspective(vfov, aspect, near_clipping, far_clipping)
            glu.gluPerspective(90.0, width / height, 0.1, 10000.0)

            # sets the model view
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glLoadIdentity()

            return pyglet.event.EVENT_HANDLED

        @self.event
        def on_draw():
            self.world.draw()

        @self.event
        def on_key_press(symbol, modifiers):
            # press the LEFT or RIGHT key to change the current model
            if symbol == pyglet.window.key.RIGHT:
                # next model
                self.model_index = (self.model_index + 1) % len(self.world.models)

            elif symbol == pyglet.window.key.LEFT:
                # previous model
                self.model_index = (self.model_index - 1) % len(self.world.models)

            elif symbol == pyglet.window.key.ESCAPE:
                # exit
                self.close()

        @self.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            # scroll the MOUSE WHEEL to zoom
            self.world.z += scroll_y / 1.0

        @self.event
        def on_mouse_drag(x, y, dx, dy, button, modifiers):
            # press the LEFT MOUSE BUTTON to rotate
            if button == pyglet.window.mouse.LEFT:
                self.world.ry += dx / 5.0
                self.world.rx -= dy / 5.0

            # press the LEFT and RIGHT MOUSE BUTTONS simultaneously to pan
            if button == pyglet.window.mouse.LEFT | pyglet.window.mouse.RIGHT:
                self.world.x += dx / 100.0
                self.world.y += dy / 100.0

        @self.event
        def update(dt):
            self.world.update(dt)
            self.world.cx = self.world.models[self.model_index].x
            self.world.cy = self.world.models[self.model_index].y
            self.world.cz = self.world.models[self.model_index].z

        pyglet.clock.schedule_interval(update, 1/UPDATE_RATE)




config = pyglet.gl.Config(sample_buffers=1, samples=4)

# creates the window and sets its properties
window = Window(config=config, width=400, height=400, caption='OBJ Viewer', resizable=True)


# starts the application
pyglet.app.run()
