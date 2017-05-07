import os

import pyglet
from pyglet.gl import gl
from pyglet.gl import glu

# colors
black = (0, 0, 0, 1)
dark_gray = (.75, .75, .75, 1)


class OBJModel:
    """
    Represents an OBJ model.
    """

    def __init__(self, (x, y, z)=(0, 0, 0), color=dark_gray, path=None):
        self.vertices = []
        self.quad_indices = []
        self.triangle_indices = []

        # translation and rotation values
        self.x, self.y, self.z = x, y, z
        self.rx = self.ry = self.rz = 0

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

    def draw(self):
        gl.glLoadIdentity()

        # sets the position
        gl.glTranslatef(self.x, self.y, self.z)

        # sets the rotation
        gl.glRotatef(self.rx, 1, 0, 0)
        gl.glRotatef(self.ry, 0, 1, 0)
        gl.glRotatef(self.rz, 0, 0, 1)

        # sets the color
        gl.glColor4f(*self.color)

        # draws the quads
        pyglet.graphics.draw_indexed(len(self.vertices) / 3, gl.GL_QUADS, self.quad_indices, ('v3f', self.vertices))

        # draws the triangles
        pyglet.graphics.draw_indexed(len(self.vertices) / 3, gl.GL_TRIANGLES, self.triangle_indices,
                                     ('v3f', self.vertices))


class Window(pyglet.window.Window):
    def __init__(self, width, height, caption, resizable=False):
        pyglet.window.Window.__init__(self, width=width, height=height, caption=caption, resizable=resizable)

        # sets the background color
        gl.glClearColor(*black)

        # pre-loaded models
        self.model_names = ['box.obj', 'uv_sphere.obj', 'monkey.obj']
        self.models = []
        for name in self.model_names:
            self.models.append(OBJModel((0, 0, -3.5), color=dark_gray, path=os.path.join('obj', name)))

        # current model
        self.model_index = 0
        self.current_model = self.models[self.model_index]

        @self.event
        def on_resize(width, height):
            # sets the viewport
            gl.glViewport(0, 0, width, height)

            # sets the projection
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            glu.gluPerspective(60.0, width / float(height), 0.1, 100.0)

            # sets the model view
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            return pyglet.event.EVENT_HANDLED

        @self.event
        def on_draw():
            # clears the screen with the background color
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            # sets wire-frame mode
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

            # draws the current model
            self.current_model.draw()

        @self.event
        def on_key_press(symbol, modifiers):
            # press the LEFT or RIGHT key to change the current model
            if symbol == pyglet.window.key.RIGHT:
                # next model
                self.model_index = (self.model_index + 1) % len(self.model_names)
                self.current_model = self.models[self.model_index]

            elif symbol == pyglet.window.key.LEFT:
                # previous model
                self.model_index = (self.model_index - 1) % len(self.model_names)
                self.current_model = self.models[self.model_index]

        @self.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            # scroll the MOUSE WHEEL to zoom
            self.current_model.z -= scroll_y / 10.0

        @self.event
        def on_mouse_drag(x, y, dx, dy, button, modifiers):
            # press the LEFT MOUSE BUTTON to rotate
            if button == pyglet.window.mouse.LEFT:
                self.current_model.ry += dx / 5.0
                self.current_model.rx -= dy / 5.0

            # press the LEFT and RIGHT MOUSE BUTTONS simultaneously to pan
            if button == pyglet.window.mouse.LEFT | pyglet.window.mouse.RIGHT:
                self.current_model.x += dx / 100.0
                self.current_model.y += dy / 100.0


# creates the window and sets its properties
window = Window(width=400, height=400, caption='OBJ Viewer', resizable=True)

# starts the application
pyglet.app.run()
