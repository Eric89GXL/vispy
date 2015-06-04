
import numpy as np

from .visual import Visual
from .line import LineVisual
from .text import TextVisual


class AxisVisual(Visual):
    """Axis visual

    Parameters
    ----------
    extents : array
        Co-ordinates of start and end of the axis.
    domain : tuple
        The data values at the beginning and end of the axis, used for tick
        labels. i.e. (5, 10) means the axis starts at 5 and ends at 10. Default
        is (0, 1).
    scale_type : str
        The type of scale. For now only 'linear' is supported.
    axis_color : tuple
        RGBA values for the axis colour. Default is black.
    tick_color : tuple
        RGBA values for the tick colours. The colour for the major and minor
        ticks is currently fixed to be the same. Default is a dark grey.
    **kwargs : dict
        Keyword arguments to pass to `Visual`.
    """
    def __init__(self, extents, domain=(0., 1.),
                 scale_type="linear", axis_color=(1, 1, 1),
                 tick_color=(0.7, 0.7, 0.7), **kwargs):
        Visual.__init__(self, **kwargs)
        if scale_type != 'linear':
            raise NotImplementedError('only linear scaling is currently '
                                      'supported')
        # XXX TODO: All kinds of input validation, property support, etc.
        self.axis_color = axis_color
        self.tick_color = tick_color
        self.scale_type = scale_type
        self.extents = np.array(extents, float)
        self.domain = domain

        self.minor_tick_length = 5
        self.major_tick_length = 10

        self._text = None
        self._line = None
        self._ticks = None

    @property
    def _vec(self):
        return self.extents[1] - self.extents[0]

    def draw(self, transforms):

        # Initialize two LineVisuals - one for the axis line, one for ticks
        if self._text is None:
            major_tick_fractions, minor_tick_fractions, tick_labels = \
                self._get_tick_frac_labels()

            tick_pos, tick_label_pos = self._get_tick_positions(
                major_tick_fractions, minor_tick_fractions)

            self._line = LineVisual(pos=self.extents, color=self.axis_color,
                                    method='gl', width=3.0)
            self._ticks = LineVisual(pos=tick_pos, color=self.tick_color,
                                     method='gl', width=2.0,
                                     connect='segments')
            self._text = TextVisual(list(tick_labels), pos=tick_label_pos,
                                    font_size=8, color='w')

        self._line.draw(transforms)
        self._ticks.draw(transforms)
        self._text.draw(transforms)

    def _get_tick_direction(self):
        """Determines the tick direction if not specified."""
        v = self._vec

        if abs(v[0]) >= abs(v[1]):  # rightward axis, rotate ticks clockwise
            v = np.dot(np.array([[0, -1], [1, 0]]), v)
        else:  # upwards axis, rotate ticks counter-clockwise
            v = np.dot(np.array([[0, 1], [-1, 0]]), v)

        # now return a unit vector
        return v / np.linalg.norm(v)

    def _get_tick_positions(self, major_tick_fractions, minor_tick_fractions):
        tick_direction = self._get_tick_direction()

        minor_vector = tick_direction * self.minor_tick_length
        major_vector = tick_direction * self.major_tick_length

        major_origins, major_endpoints = self._tile_ticks(
            major_tick_fractions, major_vector)

        minor_origins, minor_endpoints = self._tile_ticks(
            minor_tick_fractions, minor_vector)

        tick_label_pos = ((major_origins + tick_direction *
                          (self.major_tick_length + 20)))

        num_major = len(major_tick_fractions)
        num_minor = len(minor_tick_fractions)

        c = np.empty([(num_major + num_minor) * 2, 2])

        c[0:(num_major-1)*2+1:2] = major_origins
        c[1:(num_major-1)*2+2:2] = major_endpoints
        c[(num_major-1)*2+2::2] = minor_origins
        c[(num_major-1)*2+3::2] = minor_endpoints

        return c, tick_label_pos

    def _tile_ticks(self, frac, tickvec):
        """Tiles tick marks along the axis."""
        origins = np.tile(self._vec, (len(frac), 1))
        origins = self.extents[0].T + (origins.T*frac).T
        endpoints = tickvec + origins
        return origins, endpoints

    def _get_tick_frac_labels(self):
        # This conditional is currently unnecessary since we only support
        # linear, but eventually we will support others so we leave it in
        if (self.scale_type == 'linear'):

            major_num = 11  # maximum number of major ticks
            minor_num = 4   # maximum number of minor ticks per major division

            major, majstep = np.linspace(0, 1, num=major_num, retstep=True)

            labels = [str(x) for x in np.interp(major, [0, 1], self.domain)]

            # Naive minor tick labels. TODO: make these nice numbers only
            # - and faster! Potentially could draw in linspace across the whole
            # axis and render them before the major ticks, so the overlap
            # gets hidden. Might be messy. Benchmark trade-off of extra GL
            # versus extra NumPy.
            minor = []
            for i in np.nditer(major[:-1]):
                minor.extend(np.linspace(i, (i + majstep),
                             (minor_num + 2))[1:-1])
        # elif (self.scale_type == 'logarithmic'):
        #     return NotImplementedError
        # elif (self.scale_type == 'power'):
        #     return NotImplementedError
        return major, minor, labels
