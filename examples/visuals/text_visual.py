# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 30

from vispy import app, gloo
from vispy.scene.visuals import Text
from vispy.scene.transforms import STTransform


class Canvas(app.Canvas):
    def __init__(self, **kwarg):
        self.text = Text('Hello world!', bold=True)
        # We need to give a transform to our visual
        self.transform = STTransform((0.3, 0.4, 1.))
        self.text._program['transform'] = self.transform.shader_map()
        # Now we can create the canvas
        app.Canvas.__init__(self, close_keys='escape', title='Glyphs', **kwarg)
        self.scale = 200.

    def on_draw(self, event):
        gloo.clear(color=(1., 1., 1., 1.))
        self.text.draw()

    def on_mouse_wheel(self, event):
        """Use the mouse wheel to zoom."""
        self.scale *= 0.8 if event.delta[1] > 0 else 1.25
        self.scale = max(min(self.scale, 2000.), 10.)
        self.apply_zoom()

    def on_resize(self, event):
        self.apply_zoom()

    def apply_zoom(self):
        gloo.set_viewport(0, 0, *self.size)
        self.transform.scale = (self.scale / self.size[0],
                                self.scale / self.size[1], 1.)
        self.update()

c = Canvas(show=True)
c.app.run()
