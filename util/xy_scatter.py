#
# xy_scatter.py -- XY scatter plot in a Ginga viewer
#
import numpy as np

from ginga import cmap, imap


def p2r(r, t):
    t_rad = np.radians(t)
    x = r * np.cos(t_rad)
    y = r * np.sin(t_rad)
    return (x, y)


class XYScatterPlot:

    def __init__(self, logger):
        super().__init__()

        self.logger = logger
        # nominal size of plot window in px
        self._wd = 300
        self._ht = 300
        # concentric circles at each of radii
        self.radii = [0.125 * i for i in range(1, 12)]
        self.styles = ['cross', 'plus', 'circle', 'square', 'diamond',
                       'hexagon', 'downtriangle', 'uptriangle']
        # default style of point
        self.style = 'circle'
        # default radius of point
        self.r = 0.0125
        # store this many points max
        self.num_pts = 1000

    def build_gui(self, container):

        from ginga.gw import Widgets, Viewers

        zi = Viewers.CanvasView(logger=self.logger)
        zi.set_desired_size(self._wd, self._ht)
        zi.enable_autozoom('off')
        zi.set_zoom_algorithm('rate')
        zi.set_zoomrate(1.61)
        zi.ui_set_active(True)
        zi.show_mode_indicator(True, corner='ur')

        zi.set_bg(0.95, 0.95, 0.95)
        zi.set_fg(0.25, 0.25, 0.75)
        self.viewer = zi

        t_ = zi.get_settings()
        t_.set(sanity_check_scale=False)

        p_canvas = zi.get_canvas()
        self.dc = p_canvas.get_draw_classes()
        self.canvas = self.dc.DrawingCanvas()
        p_canvas.add(self.canvas)
        self.labels_canvas = self.dc.DrawingCanvas()
        p_canvas.add(self.labels_canvas)
        self.initialize_plot()

        bd = zi.get_bindings()
        bd.enable_all(True)

        iw = Viewers.GingaViewerWidget(zi)

        container.set_margins(2, 2, 2, 2)
        container.set_spacing(4)

        container.add_widget(iw, stretch=1)

    def initialize_plot(self):
        self.canvas.delete_object_by_tag('plotlines')

        self.pts_obj = self.dc.CompoundObject()
        self.canvas.add(self.pts_obj, tag='points')

        # plot circles
        objs = []
        for r in self.radii:
            objs.append(self.dc.Circle(0, 0, r, color='darkgreen'))

        # plot lines
        lim = self.radii[-1]
        objs.append(self.dc.Line(0, -lim, 0, lim, color='darkgreen'))
        objs.append(self.dc.Line(-lim, 0, lim, 0, color='darkgreen'))

        o = self.dc.CompoundObject(*objs)
        self.canvas.add(o, tag='plotlines')

        t = 45
        objs = []
        for r in self.radii:
            x, y = p2r(r, t)
            objs.append(self.dc.Text(x, y, "{}".format(r), color='orangered',
                                     fontscale=False, fontsize=10))

        o = self.dc.CompoundObject(*objs)
        self.labels_canvas.add(o, tag='labels')

        self.state_lbl = self.dc.Text(20, 30, text="", color='black',
                                      font='Ariel', fontsize=18,
                                      coord='window')
        self.labels_canvas.add(self.state_lbl, tag='state_lbl')

        self.viewer.set_limits([(-lim, -lim), (lim, lim)])
        self.viewer.set_pan(0, 0)
        self.viewer.zoom_to(14)

    def clear_plot(self):
        self.pts_obj.delete_all_objects()
        self.viewer.redraw(whence=3)

    def add_point(self, pt, color='black', alpha=1.0):
        # eject an old point if we've hit the max number of points
        if len(self.pts_obj.objects) >= self.num_pts:
            self.pts_obj.objects.pop(0)

        # add a point to the set of plotted points
        x, y = pt
        p = self.dc.Point(x, y, radius=self.r, style=self.style,
                          color=color, fillcolor=color,
                          fill=True, fillalpha=alpha)
        self.pts_obj.add_object(p)
        return p

    def refresh_plot(self):
        self.viewer.redraw(whence=3)

    def plot_points(self, pts):
        for i, pt in enumerate(pts):
            self.add_point(pt)
        self.refresh_plot()

    def plot_point(self, pt):
        self.add_point(pt)
        self.refresh_plot()

    def set_num_pts(self, num_pts):
        self.num_pts = num_pts
        self.pts_obj.objects[:] = self.pts_obj.objects[:num_pts]
        self.refresh_plot()

    def set_style(self, style):
        self.style = style
        for p in self.pts_obj.objects:
            p.style = style
        self.refresh_plot()

    def set_title_msg(self, text, color='black'):
        self.state_lbl.text = text
        self.state_lbl.color = color
        self.viewer.redraw(whence=3)


class TimedXYScatterPlot(XYScatterPlot):

    def __init__(self, logger):
        super().__init__(logger)

        self.t = None
        self.mn = 10
        self.range_t = self.mn * 60.0

        self.cmap = cmap.get_cmap('Purples_r')
        self.imap = imap.get_imap('ramp')

    def build_gui(self, container):
        from ginga.gw import ColorBar

        super().build_gui(container)

        rgbmap = self.viewer.get_rgbmap()
        self.cbar = ColorBar.ColorBar(self.logger, rgbmap=rgbmap,
                                      link=True)
        self.cbar.set_cmap(self.cmap)
        self.cbar.set_imap(self.imap)
        rgbmap.add_callback('changed', self.rgbmap_cb)
        # hack to set font size of this color bar
        self.cbar.cbar.fontsize = 8
        self.cbar.set_range(0.0, self.range_t)

        cbar_w = self.cbar.get_widget()
        cbar_w.resize(-1, 32)
        container.add_widget(cbar_w, stretch=0)

    def initialize_plot(self):
        super().initialize_plot()

        # create highlight object for newest points: an arrow pointing
        # from the last most recent point to the most recent and a dashed
        # circle around the most recent
        objs = []
        objs.append(self.dc.Circle(0, 0, self.r * 1.5, color='red',
                                   linestyle='dash', linewidth=2,
                                   alpha=0.0))
        objs.append(self.dc.Line(0, 0, 0, 0, color='blue',
                                 linestyle='solid', linewidth=1,
                                 arrow='end', alpha=0.0))
        self.hl_obj = self.dc.CompoundObject(*objs)
        self.labels_canvas.add(self.hl_obj, tag='hilite')

    def clear_plot(self):
        self.pts_obj.delete_all_objects()
        self.recolor_points()
        self.viewer.redraw(whence=3)

    def add_point(self, pt, t):
        # record latest new time stamp
        self.t = t

        p = super().add_point(pt, color='white', alpha=1.0)
        p.set_data(time_t=t)

    def recolor_points(self):
        ol = self.pts_obj.objects
        for p in ol:
            color = self.get_color(p.data.time_t)
            p.color = p.fillcolor = color

        # update transition highlight for latest point
        curr, arrow = self.hl_obj.objects
        if len(ol) > 1:
            arrow.x1, arrow.y1 = ol[-2].x, ol[-2].y
            arrow.x2, arrow.y2 = ol[-1].x, ol[-1].y
            arrow.alpha = 1.0
        else:
            arrow.alpha = 0.0

        if len(ol) > 0:
            curr.x, curr.y = ol[-1].x, ol[-1].y
            curr.alpha = 1.0
        else:
            curr.alpha = 0.0

    def refresh_plot(self):
        self.recolor_points()
        self.viewer.redraw(whence=3)

    def plot_points(self, pts, ts):
        for i, pt in enumerate(pts):
            self.add_point(pt, ts[i])
        self.refresh_plot()

    def plot_point(self, pt, t):
        self.add_point(pt, t)
        self.refresh_plot()

    def get_color(self, t):
        # calculate range of values
        pct = (self.t - t) / self.range_t

        # sanity check: clip to 8-bit color range
        idx = int(np.clip(pct * 255.0, 0, 255))

        # Apply colormap.
        rgbmap = self.cbar.get_rgbmap()
        (r, g, b) = rgbmap.get_rgbval(idx)
        r = float(r) / 255.0
        g = float(g) / 255.0
        b = float(b) / 255.0
        return (r, g, b)

    def rgbmap_cb(self, *args):
        self.refresh_plot()

    def set_range(self, range_t):
        self.range_t = range_t
        self.cbar.set_range(0.0, self.range_t)
        self.refresh_plot()
