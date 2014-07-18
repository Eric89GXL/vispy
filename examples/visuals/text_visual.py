# -*- coding: utf-8 -*-


from vispy import app, gloo
from vispy.scene.visuals import Text


class Canvas(app.Canvas):
    def __init__(self, **kwarg):
        app.Canvas.__init__(self, close_keys='escape', title='Glyphs', **kwarg)
        self._backend._vispy_warmup()
        self.text = Text('Hello world!', bold=True)

    def on_draw(self, event):
        gloo.clear(color=(1., 1., 1., 1.))
        self.text.draw()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)


c = Canvas(show=True)
c.app.run()
