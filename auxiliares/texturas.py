import pyglet
from OpenGL import GL
import numpy as np
import trimesh as tm
import networkx as nx
import os
import sys
import math
from pathlib import Path
import utils.transformations as tr
import utils.shapes as shapes

from utils.drawables import DirectionalLight, Material, Texture
from utils.scene_graph import SceneGraph
from utils.helpers import OrbitCamera, mesh_from_file, Model

WIDTH = 640
HEIGHT = 640


# controler de siempre
class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        # Evita error cuando se redimensiona a 0
        self.set_minimum_size(240, 240)
        self.set_caption(title)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.program_state = {"total_time": 0.0, "camera": None}
        self.init()

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)

    def is_key_pressed(self, key):
        return self.key_handler[key]


if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Sobre Texturas", width=WIDTH,
                            height=HEIGHT, resizable=True)

    # Definimos una camara con su distancia, la medida de la pantalla y el tipo de camara
    controller.program_state["camera"] = OrbitCamera(
        4, WIDTH, HEIGHT, "perspective")

    with open(Path(os.path.dirname(__file__)) / "shaders/textured_mesh_lit.vert") as f:
        color_vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "shaders/textured_mesh_lit.frag") as f:
        color_fragment_source_code = f.read()

    pipeline = pyglet.graphics.shader.ShaderProgram(
        pyglet.graphics.shader.Shader(color_vertex_source_code, "vertex"),
        pyglet.graphics.shader.Shader(color_fragment_source_code, "fragment")
    )

    # Defino mi objeto

    cube = Model(shapes.Cube["position"], uv_data=shapes.Cube["uv"], normal_data=shapes.Cube["normal"],
                 index_data=shapes.Cube["indices"])
    cubeTex = Texture("assets/bricks.jpg")

    cube.init_gpu_data(pipeline)

    cat = mesh_from_file(
        Path(os.path.dirname(__file__)) / "assets/cat.obj")[0]["mesh"]

    # la textura del objeto
    catTex = Texture("assets/catTex.png")

    cat.init_gpu_data(pipeline)

    # Creo un grafo de escena
    graph = SceneGraph(controller)

    # Agrego todos los objetos al grafo
    graph.add_node("sun",
                   pipeline=pipeline,
                   light=DirectionalLight(diffuse=[0.4, 0.4, 0.4], specular=[
                                          0.4, 0.4, 0.4], ambient=[0.2, 0.2, 0.2]),
                   rotation=[-np.pi/4, 0, 0]
                   )

    graph.add_node("cat",
                   mesh=cat,
                   pipeline=pipeline,
                   material=Material(),
                   texture=catTex,
                   position=[-1, 0, 1],
                   rotation=[0, -np.pi/2, 0])

    graph.add_node("cube",
                   mesh=cube,
                   pipeline=pipeline,
                   material=Material(),
                   texture=cubeTex,
                   position=[1, 0, 0],
                   scale=[2, 2, 2]
                   )

    def update(dt):
        global direction
        global t

        controller.program_state["total_time"] += dt

        # variables del controller
        time = controller.program_state["total_time"]
        camera = controller.program_state["camera"]

        if controller.is_key_pressed(pyglet.window.key.A):
            camera.phi += dt

        if controller.is_key_pressed(pyglet.window.key.D):
            camera.phi -= dt

        if controller.is_key_pressed(pyglet.window.key.W):
            camera.theta += dt

        if controller.is_key_pressed(pyglet.window.key.S):
            camera.theta -= dt

        camera.update()

    @ controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

    # draw loop
    @ controller.event
    def on_draw():
        controller.clear()

        graph.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
