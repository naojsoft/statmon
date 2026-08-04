#
# TelescopePlugin.py -- Telescope status schematic for StatMon
#
# T. Inagaki (original composite widgets)
# E. Jeschke (reorg)
#
# This is a rewrite of the original plugin that composed ~20 small
# matplotlib/Label sub-widgets (see TelescopeParts.py).  The whole
# schematic is now drawn on a *single* ginga canvas using canvas
# primitives (Text, Box, Rectangle, Circle, dashed Line, filled
# Polygon).  Objects are built once and, on each status update, we
# mutate them in place and redraw with ``whence=3`` (a graphics-only
# partial redraw) so updates are smooth and flicker-free.
#
import math

import numpy as np

import PlBase
from error import ERROR

from ginga.gw import Viewers
from ginga.canvas.CanvasObject import get_canvas_types

# virtual drawing area (data coordinates); the schematic is scaled to
# fit the pane while preserving this aspect ratio.  Authoring is done in
# a top-down pixel space (matching the reference image) and converted to
# ginga's y-up data space with yflip().
W, H = 560.0, 560.0
CX = W / 2.0    # horizontal center of the vertical instrument column


def yflip(py):
    """Convert a top-down pixel Y to ginga's y-up data Y."""
    return H - py


def arc_pts(cx, cy, radius, a0, a1, n=28):
    """Sample points along an arc from a0..a1 degrees (math convention:
    0 = +x/east, CCW positive), returned in y-up data coordinates.
    """
    angs = np.radians(np.linspace(a0, a1, n))
    return [(cx + radius * math.cos(a), cy + radius * math.sin(a))
            for a in angs]


def annulus_sector(cx, cy, r_in, r_out, a0, a1, n=28):
    """Filled annulus-sector polygon points (outer arc + inner arc back)."""
    outer = arc_pts(cx, cy, r_out, a0, a1, n)
    inner = arc_pts(cx, cy, r_in, a1, a0, n)
    return outer + inner


def dome_cap(cx, cy, rx, ry, n=28):
    """Lower-half ellipse (flat top, bulging down) used for mirror covers."""
    angs = np.radians(np.linspace(0.0, 180.0, n))
    return [(cx + rx * math.cos(a), cy - ry * math.sin(a)) for a in angs]


class TelescopeCanvas(object):
    """Builds and updates the telescope schematic on one ginga canvas."""

    def __init__(self, logger, obcp=None):
        self.logger = logger
        self.obcp = obcp
        self.focus_kind = None

        # --- color palette (matches the original parts) ---
        self.c_normal = 'darkgreen'     # nominal label text
        self.c_green = 'forestgreen'          # schematic geometry
        self.c_warn = 'orange'
        self.c_alarm = 'red'
        self.c_wind = 'blue'
        self.c_black = 'black'
        self.c_white = 'white'
        self.c_grey = 'grey'

        self.dc = get_canvas_types()

        self.viewer = Viewers.CanvasView(logger=logger, render='widget')
        self.viewer.set_background('white')
        self.viewer.set_foreground('black')
        self.viewer.set_desired_size(int(W), int(H))
        self.viewer.set_enter_focus(False)
        try:
            self.viewer.set_limits([(0, 0), (W, H)])
        except Exception:
            pass
        self.viewer.add_callback('configure', self._configure_cb)

        self.canvas = self.viewer.get_canvas()

        # references to dynamic objects, keyed by role
        self.o = {}
        # centered text objects (recentered by measuring rendered width)
        self._centered = []
        # bookkeeping for the top-screen rear bar (as in the original)
        self.rear1_pos = 4.0
        self.screen_len = 6.0
        self.ts_vmax = 30.0
        self.ts_xL, self.ts_xR = CX - 140.0, CX + 140.0

        self._build()

    # -- widget / fit -------------------------------------------------

    def get_widget(self):
        self.gw = Viewers.GingaViewerWidget(viewer=self.viewer)
        return self.gw

    def _configure_cb(self, viewer, width, height):
        if width < 2 or height < 2:
            return
        scale = min(width / W, height / H)
        try:
            # the compass center is the horizontal alignment point; it sits
            # at CX == W/2, so panning at the box center keeps it centered.
            viewer.scale_to(scale, scale)
            viewer.set_pan(W / 2.0, H / 2.0)
            self._recenter_all()
        except Exception as e:
            self.logger.error("error fitting telescope view: %s" % (e))

    # -- small canvas helpers -----------------------------------------

    def _add(self, obj):
        self.canvas.add(obj, redraw=False)
        return obj

    def _text(self, cx, py, text, color, fontsize, center=True, boxed=False):
        kw = {}
        if boxed:
            kw = dict(bordercolor=self.c_grey, borderlinewidth=1,
                      borderalpha=1.0, borderpadding=6)
        obj = self.dc.Text(cx, yflip(py), text=text, color=color,
                           fontsize=fontsize, fontscale=True,
                           fontsize_min=6.0, fontsize_max=28.0, **kw)
        obj._cx = cx if center else None
        self._add(obj)
        if center:
            self._centered.append(obj)
            self._recenter(obj)
        return obj

    def _recenter(self, obj):
        """Horizontally center a text object under its stored center x by
        measuring the actual rendered text width (proportional font)."""
        cx = getattr(obj, '_cx', None)
        if cx is None:
            return
        try:
            px_wd, _ = self.viewer.renderer.get_dimensions(obj)
            scale = self.viewer.get_scale_max()
            if scale > 0:
                obj.x = cx - (px_wd / scale) / 2.0
        except Exception:
            pass

    def _recenter_all(self):
        for obj in self._centered:
            self._recenter(obj)

    def _set_text(self, obj, text=None, color=None):
        if text is not None:
            obj.text = text
            if getattr(obj, '_cx', None) is not None:
                self._recenter(obj)
        if color is not None:
            obj.color = color
            obj.fillcolor = color

    def _set_visible(self, obj, tf):
        a = 1.0 if tf else 0.0
        obj.alpha = a
        if hasattr(obj, 'fillalpha'):
            obj.fillalpha = a

    # -- build all objects once ---------------------------------------

    def _build(self):
        dc = self.dc

        # ===== Dome shutter: black bar + white text (top) =====
        self.o['dome_bar'] = self._add(dc.Rectangle(
            0, yflip(28), W, yflip(0), color=self.c_black,
            fill=True, fillcolor=self.c_black))
        self.o['dome_txt'] = self._text(W / 2, 20, 'Dome Shutter',
                                        self.c_white, 13)

        # ===== Top screen: full-width axis + 3 stacked sliding bars + text =====
        # the axis line spans wide enough to meet the windscreen rail on the left
        self._add(dc.Line(95, yflip(72), CX + 150, yflip(72),
                          color=self.c_green, linewidth=1, alpha=0.7))
        # three segments stacked vertically (front lowest, rear1 highest),
        # each slides horizontally with its position
        for key, py in (('ts_front', 72), ('ts_rear2', 67), ('ts_rear1', 62)):
            self.o[key] = self._add(dc.Rectangle(
                200, yflip(py), 260, yflip(py - 5), color=self.c_green,
                fill=True, fillcolor=self.c_green, alpha=0.85))
        self.o['ts_txt'] = self._text(W / 2, 48, 'Top Screen', self.c_black, 13)

        # ===== Focus Z / M2 / Focus labels =====
        # boxes are drawn by the Text objects' own border (auto-sized to text);
        # placed below the top-screen area so they don't overlap it
        self.o['z_txt'] = self._text(CX, 110, 'Focus:', self.c_normal, 13,
                                    boxed=True)
        self.o['m2_txt'] = self._text(CX, 136, 'M2', self.c_normal, 14)
        self.o['focus_txt'] = self._text(CX, 170, 'Focus', self.c_normal, 17,
                                        boxed=True)

        # ===== AzEl compass =====
        cx, cy = CX, yflip(300)
        self.compass_c = (cx, cy)
        self.R = 115.0
        self.R_in = 58.0
        self.subaru_r = 26.0

        # elevation annulus sector (built first so rings draw over it)
        self.o['el_wedge'] = self._add(dc.Polygon(
            annulus_sector(cx, cy, self.R_in, self.R, 135.0, 180.0),
            color=self.c_green, fill=True, fillcolor=self.c_green,
            alpha=0.5, fillalpha=0.5, linewidth=0))
        # wind wedge (narrow isosceles triangle poking in from the outer ring)
        self.o['wind'] = self._add(dc.Polygon(
            [(cx, cy + self.R - 42), (cx - 11, cy + self.R),
             (cx + 11, cy + self.R)],
            color=self.c_wind, fill=True, fillcolor=self.c_wind,
            alpha=0.5, fillalpha=0.5, linewidth=0))
        # outer + inner circles
        self._add(dc.Circle(cx, cy, self.R, color=self.c_green, linewidth=2))
        self._add(dc.Circle(cx, cy, self.R_in, color=self.c_green,
                           linewidth=1))
        # spokes every 30 degrees (diameters through the center)
        for deg in range(0, 180, 30):
            a = math.radians(deg)
            dx, dy = self.R_in * math.cos(a), self.R_in * math.sin(a)
            self._add(dc.Line(cx - dx, cy - dy, cx + dx, cy + dy,
                             color=self.c_green, linewidth=1, alpha=0.3))
        # N/S/E/W just inside the outer ring, black and bold
        d = 0.82 * self.R
        for txt, (dx, dy) in (('N', (0, d)), ('S', (0, -d)),
                              ('E', (d, 0)), ('W', (-d, 0))):
            self._add(dc.Text(cx + dx - 6, cy + dy - 8, text=txt,
                             color=self.c_black, font='Sans Serif;normal;bold',
                             fontsize=16, fontscale=True, fontsize_max=26.0))
        # light path (dashed) from center
        self.o['az_light'] = self._add(dc.Line(
            cx, cy, cx, cy + self.R, color=self.c_green, linewidth=5,
            linestyle='dash', alpha=0.6))
        # subaru pointing marker: filled circle + direction triangle
        self.o['subaru_c'] = self._add(dc.Circle(
            cx, cy, self.subaru_r, color=self.c_wind, linewidth=2,
            fill=True, fillcolor=self.c_white))
        self.o['subaru_tri'] = self._add(dc.Polygon(
            self._subaru_tri_pts(0.0), color=self.c_wind, fill=True,
            fillcolor=self.c_wind, alpha=0.6, fillalpha=0.6, linewidth=0))

        # ===== Windscreen (left column) =====
        # single thin solid vertical rail, cut off just below the top screen
        self._add(dc.Line(105, yflip(84), 105, yflip(300),
                         color=self.c_green, linewidth=1, alpha=0.8))
        self.ws_base = yflip(300)
        self.o['ws_bar'] = self._add(dc.Rectangle(
            98, self.ws_base, 112, self.ws_base + 2, color=self.c_wind,
            fill=True, fillcolor=self.c_wind, alpha=0.7))
        # up to 3 message lines
        self.o['ws_msg'] = [self._text(60, 330 + i * 18, '', self.c_normal, 12)
                            for i in range(3)]

        # ===== M1 cover + cell cover =====
        self.o['m1'] = self._add(dc.Polygon(
            dome_cap(CX, yflip(476), 132, 30), color=self.c_grey,
            fill=True, fillcolor=self.c_black, alpha=0.75, fillalpha=0.75,
            linewidth=2))
        self.o['m1_txt'] = self._text(CX, 468, 'M1 Cover', self.c_black, 13)
        # pedestal sits lower, leaving a gap below the mirror's bulge
        self.o['cell'] = self._add(dc.Rectangle(
            CX - 68, yflip(536), CX + 68, yflip(514), color=self.c_grey,
            fill=True, fillcolor=self.c_black, alpha=0.75, fillalpha=0.75,
            linewidth=1))
        self.o['cell_txt'] = self._text(CX, 555, 'Cell Cover',
                                       self.c_black, 11)

        # ===== Right column (focus-dependent) =====
        rx = CX + 133.0    # sits clear of the outer ring (radius R = 115)
        rfs = 11        # right-column font size
        # shift the whole column down so it is roughly level with the
        # windscreen status messages on the left
        dry = 110
        self.o['insrot'] = self._text(rx, 185 + dry, '', self.c_normal, rfs,
                                     center=False)
        self.o['imgrot'] = [self._text(rx, 176 + dry + i * 15, '',
                                      self.c_normal, rfs, center=False)
                            for i in range(2)]
        self.o['adc'] = self._text(rx, 228 + dry, '', self.c_normal, rfs,
                                   center=False)
        self.o['m3'] = self._text(rx, 270 + dry, '', self.c_normal, rfs,
                                  center=False)
        self.o['tipchop'] = self._text(rx, 120 + dry, '', self.c_normal, 13,
                                       center=False)
        # waveplate: 3 stages
        self.o['wav'] = [self._text(rx, 214 + dry + i * 16, '', self.c_normal,
                                   rfs, center=False) for i in range(3)]
        # ao shutters: 2 labelled values
        self.o['ao'] = [self._text(rx, 282 + dry + i * 16, '', self.c_normal,
                                  rfs, center=False) for i in range(2)]

        # everything in the right column starts hidden until a focus is set
        for key in ('insrot', 'adc', 'm3', 'tipchop'):
            self._set_visible(self.o[key], False)
        for key in ('imgrot', 'wav', 'ao'):
            for obj in self.o[key]:
                self._set_visible(obj, False)

    def _subaru_tri_pts(self, az):
        """Triangle pointing in the telescope azimuth direction, with its
        base sitting on the outer edge of the blue center circle and the tip
        reaching out toward the inner ring (as in the original).

        NOTE: the exact az->screen mapping mirrors the original loosely and
        may need tuning against live telemetry.
        """
        cx, cy = self.compass_c
        a = math.radians(az)
        ux, uy = math.sin(a), math.cos(a)      # unit pointing vector
        r0 = self.subaru_r                     # base rides the center circle
        r1 = self.R_in - 4.0                   # tip stops just inside the ring
        ba = math.radians(42.0)                # half-angle subtended by base
        ca, sa = math.cos(ba), math.sin(ba)
        b1 = (cx + r0 * (ux * ca - uy * sa), cy + r0 * (ux * sa + uy * ca))
        b2 = (cx + r0 * (ux * ca + uy * sa), cy + r0 * (-ux * sa + uy * ca))
        tip = (cx + r1 * ux, cy + r1 * uy)
        return [tip, b1, b2]

    # ================================================================
    # update handlers (state -> object mutation).  Decode logic is kept
    # identical to the original TelescopeParts classes; only the output
    # side is changed to mutate canvas objects.
    # ================================================================

    def update_dome(self, dome):
        if dome in ERROR:
            text, bg, fg = 'Dome Shutter Undefined', self.c_alarm, self.c_white
        elif dome == "OPEN":
            text, bg, fg = 'Dome Shutter Open', self.c_white, self.c_normal
        elif dome == "CLOSED":
            text, bg, fg = 'Dome Shutter Closed', self.c_black, self.c_white
        elif not dome:
            text, bg, fg = 'Dome Shutter Partial', self.c_warn, self.c_white
        else:
            text, bg, fg = 'Dome Shutter Undefined', self.c_alarm, self.c_white
        self.o['dome_bar'].fillcolor = bg
        self._set_text(self.o['dome_txt'], text=text, color=fg)

    def update_topscreen(self, mode, front, rear):
        free, link = 0x10, 0x0C
        color = self.c_black
        if mode in ERROR:
            label = 'Top Screen Undefined'
            color = self.c_alarm
        elif mode & free:
            label = 'Top Screen Free'
        elif mode & link:
            label = 'Top Screen Link'
        else:
            label = 'Top Screen Mode Undef'
            color = self.c_alarm
        self._set_text(self.o['ts_txt'], text=label, color=color)

        try:
            if rear < self.rear1_pos:
                self.rear1_pos = rear
            elif (self.rear1_pos + self.screen_len) < rear:
                self.rear1_pos = rear - self.screen_len
            self._place_segments(front, self.rear1_pos, rear)
        except Exception as e:
            self.logger.error('error: top screen front=%s rear=%s. %s' % (
                front, rear, e))

    def _place_segments(self, front, rear1, rear2):
        """Position the three top-screen segments preserving their relative
        (stepped) offsets, but keeping the group overall centered above the
        azimuth circle (as if occluding it when closed)."""
        span = self.ts_xR - self.ts_xL
        length = (self.screen_len / self.ts_vmax) * span
        # relative left edges: larger position slides further left
        rel = {'ts_front': -(float(front) / self.ts_vmax) * span,
               'ts_rear1': -(float(rear1) / self.ts_vmax) * span,
               'ts_rear2': -(float(rear2) / self.ts_vmax) * span}
        lo = min(rel.values())
        hi = max(rel.values()) + length
        shift = CX - (lo + hi) / 2.0     # center the group on CX
        for key, x0 in rel.items():
            obj = self.o[key]
            obj.x1, obj.x2 = x0 + shift, x0 + shift + length

    def update_windscreen(self, drv, windscreen, cmd, pos, el):
        color = self.c_normal
        if windscreen == 0x02:
            msg = ['Windscreen', 'Free']
        elif windscreen == 0x01:
            msg = ['Windscreen', 'Link']
        else:
            msg = ['WindScreen', 'Mode Undef']
            color = self.c_alarm

        if pos in ERROR:
            color = self.c_alarm
            msg.append('No Pos Data')
        elif cmd in ERROR:
            color = self.c_alarm
            msg.append('No Cmd Data')
        elif not drv == 0x04 and pos <= 5.0:
            pass
        elif not drv == 0x04 and pos > 5.0:
            color = self.c_alarm
            msg.append('DrvOff/PosHigh')
        elif drv == 0x04 and windscreen == 0x02:
            color = self.c_alarm
            msg.append('DriveOn')
        elif drv == 0x04 and windscreen == 0x01 and math.fabs(cmd - pos) <= 1.0:
            pass
        elif drv == 0x04 and windscreen == 0x01 and (cmd - pos > 1.0):
            color = self.c_warn
            msg.append('Pos!=Cmd')
        elif drv == 0x04 and windscreen == 0x01:
            color = self.c_alarm
            msg.append('WS OBSTRUCT')

        for i, line in enumerate(self.o['ws_msg']):
            self._set_text(line, text=msg[i] if i < len(msg) else '',
                           color=color)

        bar = self.o['ws_bar']
        bar.color = color
        bar.fillcolor = color
        if pos not in ERROR:
            try:
                bar.y2 = self.ws_base + float(pos) * 8.0
            except Exception:
                pass

    def update_z(self, z):
        try:
            text = "Focus: %.4f mm" % z
            color = self.c_normal
        except Exception:
            text, color = "Focus: Undefined", self.c_alarm
        self._set_text(self.o['z_txt'], text=text, color=color)

    def update_m2(self, focus):
        color = self.c_normal
        if str(focus).upper() == "M2 UNDEFINED":
            color = self.c_alarm
        self._set_text(self.o['m2_txt'], text=focus, color=color)

    def update_focuslabel(self, focus, alarm):
        color = self.c_normal
        text = focus
        if str(text).upper() == "FOCUS UNDEFINED":
            color = self.c_alarm
        try:
            if alarm & 0x40:
                text, color = 'Focus Changing', self.c_alarm
            if alarm & 0x80:
                text, color = 'Focus Conflict', self.c_alarm
        except TypeError:
            text, color = 'Focus Undefined', self.c_alarm
        self._set_text(self.o['focus_txt'], text=text, color=color)

    def update_azel(self, az, el, winddir, windspeed, state):
        cx, cy = self.compass_c
        # elevation wedge
        color = self.c_green
        try:
            if state == "Pointing":
                pass
            elif el >= 89.5 or el <= 10.0:
                color = self.c_alarm
            elif el >= 89.0 or el <= 15.0:
                color = self.c_warn
            a0 = 180.0 - float(el)
            pts = annulus_sector(cx, cy, self.R_in, self.R, a0, 180.0)
            wedge = self.o['el_wedge']
            wedge.set_data_points(pts)
            wedge.color = color
            wedge.fillcolor = color
            # keep the fill semi-transparent (~0.5) rather than fully opaque
            wedge.alpha = wedge.fillalpha = (0.5 if el > 0.5 else 0.0)
        except Exception as e:
            self.logger.error('error: elevation. %s' % (e))

        # subaru azimuth marker
        try:
            self.o['subaru_tri'].set_data_points(self._subaru_tri_pts(float(az)))
        except Exception as e:
            self.logger.error('error: azimuth. %s' % (e))

        # light path along elevation
        try:
            y = math.tan(math.radians(float(el))) * self.R
            self.o['az_light'].y2 = cy + max(-self.R, min(self.R, y))
        except Exception:
            pass

        # wind direction/speed wedge
        self._update_wind(winddir, windspeed)

    def _update_wind(self, direction, speed):
        cx, cy = self.compass_c
        try:
            speed = float(speed)
            rot = 270.0
            ang = math.radians((float(direction) + rot) * -1.0)
            if speed < 7.0:
                color, alpha = self.c_wind, 0.5
            elif speed < 20.0:
                color, alpha = self.c_warn, 0.5
            else:
                color, alpha = self.c_alarm, 0.8
            # tip points inward from the outer ring by the (scaled) speed
            depth = min(self.R * 0.62, 40.0 + speed)
            tx = cx + (self.R - depth) * math.cos(ang)
            ty = cy + (self.R - depth) * math.sin(ang)
            perp = ang + math.pi / 2.0
            ox, oy = 11.0 * math.cos(perp), 11.0 * math.sin(perp)
            b1 = (cx + self.R * math.cos(ang) + ox,
                  cy + self.R * math.sin(ang) + oy)
            b2 = (cx + self.R * math.cos(ang) - ox,
                  cy + self.R * math.sin(ang) - oy)
            obj = self.o['wind']
            obj.set_data_points([(tx, ty), b1, b2])
            obj.color = color
            obj.fillcolor = color
            obj.alpha = obj.fillalpha = alpha
        except Exception as e:
            self.logger.error('error: wind. %s' % (e))

    def update_m1cover(self, m1cover, m1cover_onway):
        m1 = self.o['m1']
        try:
            if m1cover in ERROR:
                m1.fillcolor, text = self.c_alarm, 'M1 Cover Undef'
            elif m1cover_onway in ERROR:
                m1.fillcolor, text = self.c_alarm, 'M1 Cover OnWay Undef'
            elif m1cover_onway == 0x01:
                m1.fillcolor, text = self.c_warn, 'M1 Cover OnWay-Open'
            elif m1cover_onway == 0x02:
                m1.fillcolor, text = self.c_warn, 'M1 Cover OnWay-Closed'
            elif (m1cover & 0x5555555555555555555555) == 0x1111111111111111111111:
                m1.fillcolor, text = self.c_white, 'M1 Cover Open'
            elif (m1cover & 0x5555555555555555555555) == 0x4444444444444444444444:
                m1.fillcolor, text = self.c_black, 'M1 Cover Closed'
            else:
                m1.fillcolor, text = self.c_warn, 'M1 Cover Partial'
            self._set_text(self.o['m1_txt'], text=text)
        except Exception as e:
            self.logger.error('Error: M1 cover. %s' % (e))

    def update_cell(self, cell):
        obj = self.o['cell']
        if cell == 0x01:
            obj.fillcolor, text = self.c_white, 'Cell Cover Open'
        elif cell == 0x04:
            obj.fillcolor, text = self.c_black, 'Cell Cover Closed'
        elif cell == 0x00:
            obj.fillcolor, text = self.c_warn, 'Cell Cover OnWay'
        else:
            obj.fillcolor, text = self.c_alarm, 'Cell Cover Undef'
        self._set_text(self.o['cell_txt'], text=text)

    # --- right-column decoders (kept identical to the originals) ------

    def _insrot(self, insrot, mode, variant):
        if variant == 'pf':
            free_r, link_r, free_m, link_m = 0x02, 0x01, 0x20, 0x10
        else:  # cs
            free_r, link_r, free_m, link_m = 0x02, 0x01, 0x02, 0x01
        if insrot == free_r or mode == free_m:
            return 'InsRot Free', self.c_warn
        elif insrot == link_r and mode == link_m:
            return 'InsRot Link', self.c_normal
        return 'InsRot Undefined', self.c_alarm

    def _imgrot_base(self, imgrot, mode, focus):
        imgout = [0x10000000, 0x20000000, 0x00040000, 0x00100000, 0x00200000,
                  0x00000400, 0x00002000, 0x00004000, 0x00000008, 0x00000000]
        color = self.c_normal
        if focus in imgout:
            return 'ImgRot Out', color
        elif imgrot == 0x02 or mode == 0x02:
            return 'ImgRot Free', self.c_warn
        elif imgrot == 0x01 and mode == 0x01:
            return 'ImgRot Link', color
        elif imgrot == 0x01 and mode == 0x40:
            return 'ImgRot Zenith', color
        return 'ImgRot Undefined', self.c_alarm

    def _adc(self, on_off, mode, in_out, pf=False):
        if pf:
            mode_free, mode_link = 0x80, 0x40
        else:
            mode_free, mode_link = 0x08, 0x04
        adc_out, adc_in, adc_off, adc_on = 0x10, 0x08, 0x02, 0x01

        def _mode():
            if mode == mode_link:
                return 'ADC Link', self.c_normal
            elif mode == mode_free:
                return 'ADC Free', self.c_alarm
            return 'ADC Mode Undef', self.c_alarm

        def _power():
            if on_off == adc_off:
                return 'ADC Free', self.c_alarm
            elif on_off == adc_on:
                return _mode()
            return 'ADC On/Off Undef', self.c_alarm

        if in_out == adc_out:
            return 'ADC Out', self.c_normal
        elif in_out == adc_in:
            return _power()
        return 'ADC In/Out Undef', self.c_alarm

    def _m3(self, m3):
        if m3 == 0x09:
            return 'NS OPT M3 In', self.c_normal
        elif m3 == 0x06:
            return 'NS IR M3 In', self.c_normal
        elif m3 == 0x0a:
            return 'M3 Out', self.c_normal
        return 'M3 Conflict', self.c_alarm

    def _tipchop(self, mode, drive, data, state):
        color = self.c_normal
        if mode in ERROR or drive in ERROR or data in ERROR or state in ERROR:
            return '', color
        elif not drive & 0x01 and drive & 0x02:
            return '', color
        elif mode & 0x47 == 0x04:
            return '', color
        elif mode & 0x47 == 0x02:
            return 'Tip-Tilt', self.c_warn if not data & 0x01 else color
        elif mode & 0x47 == 0x01:
            warn = state & 0x02 or (not state & 0x05 == 0x05)
            return 'Chopping', self.c_warn if warn else color
        return 'Tip/Chop Undefined', self.c_alarm

    def _stage(self, stage, name):
        try:
            stage = float(stage)
            assert -0.0001 < stage < 0.0001
            return '%s Out' % name, self.c_normal
        except AssertionError:
            try:
                assert 54.9999 < stage < 55.00001
                return '%s In' % name, self.c_green
            except AssertionError:
                return '%s Undef' % name, self.c_alarm
        except Exception:
            return '%s Undef' % name, self.c_alarm

    def _shutter(self, val):
        if val == 'OPEN':
            return 'OPEN', self.c_alarm
        elif val == 'CLOSE':
            return 'CLOSE', self.c_normal
        return 'Undef', self.c_alarm

    # -- focus layout selection ---------------------------------------

    # obcp -> focus kind (same grouping the original used)
    FOCUS = {'HDS': 'nsopt', 'SPCAM': 'popt', 'HICIAO': 'nsir', 'IRCS': 'nsir',
             'CHARIS': 'nsir', 'IRD': 'nsir', 'FMOS': 'pir', 'HSC': 'popt',
             'K3D': 'nsir', 'MOIRCS': 'cs', 'SWIMS': 'csir', 'MIMIZUKU': 'csir',
             'FOCAS': 'csopt', 'COMICS': 'csir', 'SUKA': 'cs', 'PFS': 'popt',
             'VAMPIRES': 'nsir', 'SCEXAO': 'nsir', 'REACH': 'nsir',
             'NINJA': 'nsir'}

    # which right-column roles are visible per focus kind
    LAYOUT = {'popt': ['insrot', 'adc', 'm3'],
              'pir': ['insrot', 'm3'],
              'nsopt': ['imgrot', 'adc', 'm3'],
              'nsir': ['imgrot', 'wav', 'ao', 'm3'],
              'cs': ['insrot', 'm3'],
              'csir': ['tipchop', 'insrot', 'm3'],
              'csopt': ['insrot', 'adc', 'm3']}

    def set_focus(self, obcp):
        self.obcp = obcp
        self.focus_kind = self.FOCUS.get(obcp)
        roles = set(self.LAYOUT.get(self.focus_kind, []))
        for role in ('insrot', 'adc', 'm3', 'tipchop'):
            self._set_visible(self.o[role], role in roles)
        for role in ('imgrot', 'wav', 'ao'):
            for obj in self.o[role]:
                self._set_visible(obj, role in roles)
        self.canvas.update_canvas(whence=3)

    # -- top-level status update --------------------------------------

    def update_focus(self, **k):
        kind = self.focus_kind
        self._set_text(self.o['m3'], *self._m3(k.get('TSCV.M3Drive')))

        if kind == 'nsir':
            t, c = self._imgrot_base(k.get('TSCV.ImgRotRotation'),
                                     k.get('TSCV.ImgRotMode'),
                                     k.get('TSCV.FOCUSINFO'))
            line2 = ''
            if t == 'ImgRot Out':
                line2 = '(AO In)' if k.get('TSCV.FOCUSINFO') == 0 else '(AO Out)'
            self._set_text(self.o['imgrot'][0], t, c)
            self._set_text(self.o['imgrot'][1], line2, c)
            for i, (stg, nm) in enumerate((('WAV.STG1_PS', 'Polarizer'),
                                           ('WAV.STG2_PS', '1/2 WP'),
                                           ('WAV.STG3_PS', '1/4 WP'))):
                self._set_text(self.o['wav'][i], *self._stage(k.get(stg), nm))
            lw_t, lw_c = self._shutter(k.get('AON.LWFS.LASH'))
            hw_t, hw_c = self._shutter(k.get('AON.HWFS.LASH'))
            self._set_text(self.o['ao'][0], 'LWSH: %s' % lw_t, lw_c)
            self._set_text(self.o['ao'][1], 'HWSH: %s' % hw_t, hw_c)

        elif kind == 'nsopt':
            t, c = self._imgrot_nsopt(k)
            self._set_text(self.o['imgrot'][0], t.split('\n')[0], c)
            self._set_text(self.o['imgrot'][1],
                           t.split('\n')[1] if '\n' in t else '', c)
            self._set_text(self.o['adc'],
                           *self._adc(k.get('TSCV.ADCOnOff'),
                                      k.get('TSCV.ADCMode'),
                                      k.get('TSCV.ADCInOut')))

        elif kind == 'csir':
            self._set_text(self.o['tipchop'],
                           *self._tipchop(k.get('TSCV.TT_Mode'),
                                          k.get('TSCV.TT_Drive'),
                                          k.get('TSCV.TT_DataAvail'),
                                          k.get('TSCV.TT_ChopStat')))
            self._set_text(self.o['insrot'],
                           *self._insrot(k.get('TSCV.InsRotRotation'),
                                         k.get('TSCV.InsRotMode'), 'cs'))

        elif kind == 'csopt':
            self._set_text(self.o['insrot'],
                           *self._insrot(k.get('TSCV.InsRotRotation'),
                                         k.get('TSCV.InsRotMode'), 'cs'))
            self._set_text(self.o['adc'],
                           *self._adc(k.get('TSCV.ADCOnOff'),
                                      k.get('TSCV.ADCMode'),
                                      k.get('TSCV.ADCInOut')))

        elif kind == 'cs':
            self._set_text(self.o['insrot'],
                           *self._insrot(k.get('TSCV.InsRotRotation'),
                                         k.get('TSCV.InsRotMode'), 'cs'))

        elif kind == 'pir':
            self._set_text(self.o['insrot'],
                           *self._insrot(k.get('TSCV.INSROTROTATION_PF'),
                                         k.get('TSCV.INSROTMODE_PF'), 'pf'))

        elif kind == 'popt':
            self._set_text(self.o['insrot'],
                           *self._insrot(k.get('TSCV.INSROTROTATION_PF'),
                                         k.get('TSCV.INSROTMODE_PF'), 'pf'))
            self._set_text(self.o['adc'],
                           *self._adc(k.get('TSCV.ADCONOFF_PF'),
                                      k.get('TSCV.ADCMODE_PF'), 0x08, pf=True))

    def _imgrot_nsopt(self, k):
        imgrot = k.get('TSCV.ImgRotRotation')
        mode = k.get('TSCV.ImgRotMode')
        focus = k.get('TSCV.FOCUSINFO')
        itype = k.get('TSCV.ImgRotType')
        imrb = [0x40000000, 0x80000000, 0x00400000, 0x00800000, 0x00008000,
                0x00000001]
        imrr = [0x00010000, 0x00020000, 0x00000100, 0x00000200, 0x00000002,
                0x00000004]
        itypes = {0x12: imrb, 0x10: '(OnWay-Blue)', 0x0C: imrr,
                  0x04: '(OnWay-Red)', 0x14: '(none type)'}
        text, color = self._imgrot_base(imgrot, mode, focus)
        if text in ('ImgRot Free', 'ImgRot Link', 'ImgRot Zenith'):
            try:
                res = itypes[itype]
            except KeyError:
                text += '\n(type undef)'
                color = self.c_warn
            else:
                if isinstance(res, list):
                    if focus in imrb:
                        text += '\n(Blue)'
                    elif focus in imrr:
                        text += '\n(Red)'
                    else:
                        text += '\n(type undef)'
                        color = self.c_warn
                else:
                    text += '\n' + res
        return text, color

    def update_telescope(self, **k):
        try:
            self.update_dome(dome=k.get('STATL.DOMESHUTTER_POS'))
            self.update_topscreen(mode=k.get('TSCV.TopScreen'),
                                  front=k.get('TSCL.TSFPOS'),
                                  rear=k.get('TSCL.TSRPOS'))
            self.update_windscreen(drv=k.get('TSCV.WINDSDRV'),
                                   windscreen=k.get('TSCV.WindScreen'),
                                   cmd=k.get('TSCL.WINDSCMD'),
                                   pos=k.get('TSCL.WINDSPOS'),
                                   el=k.get('TSCS.EL'))
            self.update_z(z=k.get('TSCL.Z'))
            self.update_m2(focus=k.get('STATL.M2_DESCR'))
            self.update_focuslabel(focus=k.get('STATL.FOC_DESCR'),
                                   alarm=k.get('TSCV.FOCUSALARM'))
            self.update_azel(az=k.get('TSCS.AZ'), el=k.get('TSCS.EL'),
                             winddir=k.get('TSCL.WINDD'),
                             windspeed=k.get('TSCL.WINDS_O'),
                             state=k.get('STATL.TELDRIVE'))
            self.update_m1cover(m1cover=k.get('TSCV.M1Cover'),
                                m1cover_onway=k.get('TSCV.M1CoverOnway'))
            self.update_cell(cell=k.get('TSCV.CellCover'))
            if self.focus_kind is not None:
                self.update_focus(**k)
        except Exception as e:
            self.logger.error("error updating telescope plugin: %s" % (e),
                              exc_info=True)
        # one flicker-free, graphics-only redraw for the whole update
        self.canvas.update_canvas(whence=3)


class TelescopePlugin(PlBase.Plugin):
    """Telescope status schematic (single ginga canvas)."""

    aliases = ['STATL.DOMESHUTTER_POS', 'TSCV.TopScreen', 'TSCL.TSFPOS',
               'TSCL.TSRPOS', 'TSCV.WINDSDRV', 'TSCV.WindScreen',
               'TSCL.WINDSPOS', 'TSCL.WINDSCMD', 'TSCL.WINDD', 'TSCL.Z',
               'STATL.FOC_DESCR', 'STATL.M2_DESCR', 'TSCV.FOCUSALARM',
               'TSCS.AZ', 'STATL.TELDRIVE', 'TSCS.EL',
               'TSCV.M1Cover', 'TSCV.M1CoverOnway', 'TSCV.CellCover',
               'TSCV.ADCONOFF_PF', 'TSCV.ADCMODE_PF',
               'TSCV.ADCOnOff', 'TSCV.ADCMode', 'TSCV.ADCInOut',
               'TSCV.ImgRotRotation', 'TSCV.ImgRotMode', 'TSCV.ImgRotType',
               'TSCV.FOCUSINFO',
               'TSCV.INSROTROTATION_PF', 'TSCV.INSROTMODE_PF',
               'TSCV.InsRotRotation', 'TSCV.InsRotMode',
               'WAV.STG1_PS', 'WAV.STG2_PS', 'WAV.STG3_PS',
               'TSCV.TT_Mode', 'TSCV.TT_Drive', 'TSCV.TT_DataAvail',
               'TSCV.TT_ChopStat', 'TSCL.WINDS_O',
               'AON.LWFS.LASH', 'AON.HWFS.LASH', 'TSCV.M3Drive']

    def build_gui(self, container):
        self.root = container
        self.root.set_margins(0, 0, 0, 0)
        self.root.set_spacing(0)

        self.obcp = 'SUKA'
        try:
            self.telescope = TelescopeCanvas(self.logger, obcp=self.obcp)
            self.root.add_widget(self.telescope.get_widget(), stretch=1)
            self.telescope.set_focus(self.obcp)
        except Exception as e:
            self.logger.error("error building telescope layout: %s" % (e),
                              exc_info=True)

    def change_config(self, controller, d):
        obcp = d['inst']
        self.logger.debug('telescope change config ins=%s' % (obcp))
        if obcp.startswith('#'):
            self.logger.debug('obcp is not assigned. %s' % obcp)
            return
        try:
            self.telescope.set_focus(obcp)
        except Exception as e:
            self.logger.error("error configuring telescope layout: %s" % (e))

    def start(self):
        self.controller.register_select('telescope', self.update,
                                        TelescopePlugin.aliases)
        self.controller.add_callback('change-config', self.change_config)

    def update(self, statusDict):
        self.telescope.update_telescope(**statusDict)
