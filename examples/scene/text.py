# -*- coding: utf-8 -*-


from vispy import app, gloo
from vispy.scene.visuals import Text


class Canvas(app.Canvas):
    def __init__(self, **kwarg):
        self.text = Text('AV', face='Arial', bold=True)
        app.Canvas.__init__(self, close_keys='escape', title='Glyphs', **kwarg)

    def on_draw(self, event):
        gloo.clear(color=(1., 1., 1., 1.))
        self.text.draw()
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)


c = Canvas(show=True)
c.app.run()
