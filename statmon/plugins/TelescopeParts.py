#
# T. Inagaki
#
import math
import numpy as np

from matplotlib.figure import Figure
from matplotlib.figure import SubplotParams
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
from matplotlib.artist import Artist

from error import ERROR
from g2cam.status.common import STATNONE, STATERROR
from ginga.gw import Widgets

import PlBase
from CustomLabel import Label, ERROR
from CustomPlot import PlotWidget


class DomeShutter(Label):

    ''' state of the DomeShutter  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=10, width=500,
                         height=20, fg='white', bg='black',
                         weight='bold', logger=logger )

    def update_dome(self, dome):
        ''' dome=STATL.DOMESHUTTER_POS '''
        self.logger.debug('dome=%s' %(str(dome)))

        if dome in ERROR:
            self.logger.error(f'error: dome={dome}')
            text = 'Dome Shutter Undefined'
            bg = self.alarm
            fg = self.fg
        elif dome == "OPEN": # dome shutter open
            self.logger.debug(f'open dome={dome}')
            text = 'Dome Shutter Open'
            bg = self.fg
            fg = self.normal
        elif dome == "CLOSED": # dome shuuter close
            self.logger.debug('close dome={dome}')
            text = 'Dome Shutter Closed'
            bg = self.bg
            fg = self.fg
        elif not dome : # dome shutter  partial
            self.logger.debug('partial dome={dome}')
            text = 'Dome Shutter Partial'
            bg = self.warn
            fg = self.fg

        self.logger.debug(f'text={text}, fg={fg}, bg={bg}')

        self.set_color(fg=fg, bg=bg)
        self.set_text(text)


class Topscreen(PlotWidget):
    """ Topscreen """
    def __init__(self, parent=None, width=1, height=1,  logger=None):

        sub = SubplotParams(left=0, bottom=0, right=1,
                            top=1, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height), facecolor='white',
                          subplotpars=sub)
        super().__init__(self.fig)

        self.axes = self.fig.add_subplot(111)

        # y axis values. these are fixed values.
        self.y_axis = [-1.0, 0, 1]
        self.center_y = 0.0

        # width/hight of widget
        self.w = 500
        self.h = 50
        self.set_expanding(True, False)
        self.set_min_size(self.w, self.h)

        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        limit = [30.3, 0] # there is a case of tscl.tsfpos=24.28, so limit is at least 24.28 + 6 = 30.28
        front_init = 16
        self.rear1_pos=rear1_init = 4
        rear2_init = 10

        # top screen front/rear length/width
        self.screen_len = 6 # 6 meter
        screen_width = 0.2

        self.screen_color = 'green'
        self.normal_color = 'black'
        self.alarm_color = 'red'

        # front/rear top screen
        ts_kwargs = dict(alpha=0.8, fc=self.screen_color,
                         ec=self.screen_color, lw=1, )
        self.front = mpatches.Rectangle((front_init, screen_width - screen_width),
                                        self.screen_len, screen_width, **ts_kwargs)

        self.rear1 = mpatches.Rectangle((rear1_init, screen_width * 2),
                                        self.screen_len, screen_width,
                                        **ts_kwargs)
        self.rear2 = mpatches.Rectangle((rear2_init, screen_width),
                                        self.screen_len, screen_width,
                                        **ts_kwargs)

        self.axes.add_patch(self.front)
        self.axes.add_patch(self.rear1)
        self.axes.add_patch(self.rear2)

        # draw x-axis line
        line_kwargs = dict(alpha=0.7, ls='-', lw=0.7 , color=self.screen_color,
                           marker='|', ms=10.0, mew=2, markevery=(0,1))

        offset_drawing = 0.04
        middle = [max(limit) - offset_drawing, min(limit) + offset_drawing]
        line = Line2D(middle, [self.center_y] * len(middle), **line_kwargs)
        self.axes.add_line(line)

        # draw text
        self.text = self.axes.text(0.5, 0.2, 'Initializing',
                                   va='baseline', ha='center',
                                   transform = self.axes.transAxes,
                                   color=self.normal_color,
                                   fontsize=13)

        # set x,y limit values
        self.axes.set_xlim(max(limit), min(limit))
        self.axes.set_ylim(min(self.y_axis), max(self.y_axis))
        # disable default x/y axis drawing
        #self.axes.set_xlabel(False)
        #self.axes.apply_aspect()
        self.axes.set_axis_off()

        #self.axes.set_xscale(10)
        self.axes.axison = False
        #self.draw()

    def update_topscreen(self, mode, front , rear):
        ''' mode = TSCV.TopScreen
            front = TSCL.TSFPOS
            rear = TSCL.TSRPOS
        '''
        free = 0x10
        link = 0x0C
        color = self.normal_color

        self.logger.debug(f'mode={mode}')

        if mode in ERROR:
            mode = 'Top Screen Undefined'
            color = self.alarm_color
        elif mode & free:
            mode = 'Top Screen Free'
        elif mode & link:
            mode = 'Top Screen Link'
        else:
            mode = 'Top Screen Mode Undef'
            color = self.alarm_color

        self.text.set_text(mode)
        self.text.set_color(color)

        self.logger.debug(f'updating pre_rear1={self.rear1_pos}')

        try:
            if rear < self.rear1_pos:
                self.rear1_pos = rear
            elif ((self.rear1_pos+self.screen_len) < rear):
                self.rear1_pos = rear-self.screen_len
            self.logger.debug(f'updating front={front}, rear1={self.rear1_pos}, rear2={rear}')

            self.front.set_x(front)
            self.rear1.set_x(self.rear1_pos)
            self.rear2.set_x(rear)

        except Exception as e:
            self.logger.error(f'error: front={front}, rear={rear}. {e}')

        self.draw()


class Windscreen(PlotWidget):
    """ Windscreen """
    def __init__(self, parent=None, width=1, height=1,  dpi=None, logger=None):

        self.logger = logger
        sub = SubplotParams(left=0, bottom=0.03, right=1,
                            top=1, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height), facecolor='white',
                          subplotpars=sub)
        super().__init__(self.fig)

        self.axes = self.fig.add_subplot(111)

        self.limit = [-14.5, 14.5]

        self.wind = 'blue'
        self.normal = 'green'
        self.warn = 'orange'
        self.alarm = 'red'

        # y axis values. these are fixed values.
        self.x_axis = [0, 1]
        self.y_axis = [-14.5, 14.5]
        self.center_x = 0.5
        self.init_x = 0.0  # initial value of x

        self.set_expanding(True, True)

        # width/hight of widget
        self.w = 125
        self.h = 450
        #self.resize(self, self.w, self.h)

        # top screen lenght/width
        self.ts_len = 6
        self.ts_width = 0.1

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        # position of current/cmd display
        self.y_curoffset = 0.35
        self.y_cmdoffset = -0.65


        #self.axes.add_patch(self.rear)
        # draw x-axis
        line_kwargs = dict(alpha=0.7, ls='-', lw=1 , color=self.normal,
                         marker='_', ms=15.0, mew=1.0, markevery=(0,1))


        middle = [min(self.limit),  max(self.limit)]
        line = Line2D([0.87]*len(middle), [0, 14.5],
                      #transform=self.axes.transAxes,
                      **line_kwargs)
        self.axes.add_line(line)

        line_kwargs = dict(alpha=0.7, ls=':', lw=5, color=self.normal,
                         marker='', ms=7.0, mew=1.0, markevery=(1,2))

        y = math.tan(math.radians(90)) * 14.5
        self.light = Line2D([2.0, 0], [0, y],
                            #transform=self.axes.transAxes,
                            **line_kwargs)
        self.axes.add_line(self.light)

        ts_kwargs = dict(alpha=0.7, fc=self.wind, ec=self.wind, lw=1.5)

        self.windscreen = mpatches.Rectangle((self.center_x - (self.ts_width / 2.0) + 0.425, 0.0),
                                             self.ts_width, 0,
                                             **ts_kwargs)

        self.axes.add_patch(self.windscreen)

        # draw text
        self.msg = self.axes.text(0.9, 0.48, 'Init',
                                  color=self.normal,  va='top', ha='right',
                                  transform=self.axes.transAxes, fontsize=13)

        # set x,y limit values
        self.axes.set_ylim(min(self.limit),  max(self.limit))
        self.axes.set_xlim(min(self.x_axis), max(self.x_axis))
        # # disable default x/y axis drawing
        #self.axes.set_xlabel(False)
        #self.axes.apply_aspect()
        self.axes.set_axis_off()

        #self.axes.set_xscale(10)
        #self.axes.axison=False
        self.draw()

    def __msg(self,  drv, windscreen, cmd, pos):

        color = self.normal

        if windscreen == 0x02: # windscreen free
            msg = 'Windscreen\nFree'
        elif windscreen == 0x01: # windscreen link
            msg = 'Windscreen\nLink'
        else:# windscreen undefined
            msg = 'WindScreen\nMode Undef'
            color = self.alarm

        if pos in ERROR:
            color = self.alarm
            msg += '\nNo Pos Data'
        elif cmd in ERROR:
            color = self.alarm
            msg += '\nNo Cmd Data'
        elif not drv == 0x04 and pos <= 5.0: # drive not on
            pass #msg+='\n'
        elif not drv == 0x04 and pos > 5.0: # drive not on
            color=self.alarm
            msg += '\nDrvOff/PosHigh'
        elif  drv == 0x04 and windscreen == 0x02:# drive on and Free
            color = self.alarm
            msg += '\nDriveOn'
        # drive on/link/cmd==pos
        elif drv == 0x04 and windscreen == 0x01 and math.fabs(cmd-pos) <= 1.0:
            pass #msg+='\n'   # GREEN, no alerts
        # drive on/link/ cmd!=pos
        elif  drv == 0x04 and windscreen == 0x01 and (cmd-pos > 1.0):
            color = self.warn
            msg += '\nPos!=Cmd'
        #drive on/link/ cmd-pos < -1
        elif  drv == 0x04 and windscreen == 0x01:
            color = self.alarm
            msg += '\nWS OBSTRUCT'
        else:
            #color=self.warn
            pass
            #msg+='\n'
        return (msg, color)

    def __update_lightpath(self, el):

        try:
            y = math.tan(math.radians(el)) * 14.5
        except Exception:
            pass
        else:
            if 0 < el < 35:
                offset = 0.055 + (el-10) * 0.04
            elif 35 <= el < 50:
                offset = 1.1 + (el-35) * 0.06
            elif 50 <= el:
                offset = 2.15 + (el-50) * 0.12
            else:
                offset = 0

            # 10 0.1, 15 0.3, 20 0.5, 25 0.7, 30 0.9,
            # 35 1.1, 40 1.4, 45 1.7, 50 2.0,   55 2.6, 60 3.2
            self.light.set_ydata([0, y+offset])

    def update_windscreen(self, drv, windscreen, cmd, pos, el):
        ''' drv = TSCV.WINDSDRV
            windscreen = TSCV.WindScreen
            pos = TSCL.WINDSPOS
            cmd = TSCL.WINDSCMD
            el = TSCS.EL
        '''

        self.logger.debug(f'updating drv={drv}, ws={windscreen}, cmd={cmd}, pos={pos}')

        msg, color=self.__msg(drv, windscreen, cmd, pos)

        self.msg.set_text(msg)
        #self.msg.set_backgroundcolor(color)
        self.msg.set_color(color)

        self.windscreen.set_color(color)
        if not pos in ERROR:
            self.windscreen.set_height(pos)

        self.__update_lightpath(el)

        self.draw()


class FocusZ(Label):
    ''' telescope focus z '''
    def __init__(self, parent=None, logger=None):

        super().__init__(parent=parent, fs=14, width=250,
                         height=25, frame=True, linewidth=0.1,
                         logger=logger )

    def update_z(self, z):
        ''' z=TSCL.Z '''

        self.logger.debug(f'z={z}')
        #self.text='Focus: {0:<.04f} mm'.format(z)
        try:
            text = "Focus: %.4f mm" %z
            color = self.normal
        except Exception:
            text = "Focus: Undefined"
            color = self.alarm
            self.logger.error(f'error: focus z undef. z={z}')
        self.set_color(fg=color, bg=self.bg)
        self.set_text(text)


class Focus(Label):
    ''' telescope focus  '''

    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=18, width=250, height=35,
                         frame=True, linewidth=1,  logger=logger)

    def update_focus(self,focus, alarm):
        ''' focus = STATL.FOC_DESR
            alarm = TSCV.FOCUSALARM '''

        self.logger.debug(f'focus={focus} alarm={alarm}')

        color = self.normal
        text = focus

        if text.upper() == "FOCUS UNDEFINED":
            color = self.alarm

        try:
            if alarm & 0x40:
                text = 'Focus Changing'
                color = self.alarm
            if alarm & 0x80:
                text = 'Focus Conflict'
                color = self.alarm
                self.logger.error('error: focus in conflict with rot/adc')
        except TypeError:
            text = 'Focus Undefined'
            color = self.alarm
            self.logger.error(f'error: focusalarm undef. focusinfo={focus} focusalarm={alarm}')

        self.set_color(fg=color, bg=self.bg)
        self.set_text(text)


class M2(Label):
    ''' telescope 2nd mirror   '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=16, width=250, height=35,
                         logger=logger)

    def update_m2(self,focus):
        ''' focus = STATL.M2_DESCR  '''

        self.logger.debug(f'focus={focus}')

        color = self.normal

        if focus.upper() == "M2 UNDEFINED":
            color = self.alarm

        self.set_text(focus)
        self.set_color(fg=color, bg=self.bg)


class AzEl(PlotWidget):
    """ Azimuth/Elevation diagram """
    def __init__(self, parent=None, width=1, height=1,  dpi=None, logger=None):

        sub = SubplotParams(left=0.0, bottom=0, right=1,
                            top=1, wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height),
                          facecolor='white', subplotpars=sub)
        super().__init__(self.fig)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_aspect('equal')

        self.limit_low = 0.0
        self.limit_high = 90.0;

        self.alarm_high = 89.5
        self.alarm_low = 10.0

        self.warn_high = 89.0
        self.warn_low = 15.0


        self.normal_color = 'green'
        self.warn_color = 'orange'
        self.alarm_color = 'red'
        self.wind_color = 'blue'

        self.x_scale = [0, 1]
        self.y_scale = [0, 1]
        self.x_center = (max(self.x_scale) - min(self.x_scale) / len(self.x_scale))
        self.y_center = (max(self.y_scale) - min(self.y_scale) / len(self.y_scale))
        self.center = 0.5
        self.new_x = 0.5
        self.new_y = 0.375

        # width/hight of widget
        self.w = 250
        self.h = 250
        self.set_expanding(True, True)
        self.set_min_size(self.w, self.h)

        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        self.wind_kwargs =  dict(alpha=0.5, color=self.wind_color, lw=0)
        self.wind = mpatches.Polygon(xy=[[0, 0],
                                         [0, 0],
                                         [0, 0]],
                                     **self.wind_kwargs)
        self.axes.add_patch(self.wind)


        # wind direction
        # self.wind = self.axes.annotate('', xy=(self.center, self.center+0.4),
        #                          xytext=(self.center, self.center+0.498),
        #                          size=29.5,
        #                          arrowprops=dict(arrowstyle="wedge,tail_width=0.7",
        #                                          facecolor=self.wind_color, ec="none",
        #                                          alpha=0.5, patchA=None,
        #                                          relpos=(0.0, -0.1)),
        #                          horizontalalignment='center')

        # center +
        center_x = Line2D([self.center, self.center],
                          [self.center, self.center],
                          alpha=0.1, marker='+', ms=165.0,
                          mew=1.5, mec=self.normal_color, markevery=(0,1))
        self.axes.add_line(center_x)

        # inner circle
        inner_c = Circle((self.center, self.center), radius=0.25, alpha=0.8,
                         fc="white", ec=self.normal_color, lw=0.5, ls='solid')
        self.axes.add_patch(inner_c)

        d_offset = 0.2
        directions = {'N':(self.center, self.center+d_offset),
                      'S':(self.center, self.center-d_offset),
                      'E':(self.center + d_offset, self.center),
                      'W':(self.center - d_offset, self.center)}

        # dirctions
        for key, vals in directions.items():
            self.axes.text(vals[0], vals[1], key,
                           color='g', ha='center', va='center',
                           fontsize=18,
                           transform=self.axes.transAxes)

        # subaru telescope direction
        self.subaru_radius = 0.125
        # subaru's directions: south 0 , west 90, north 180, east 270/-90
        self.subaru = mpatches.RegularPolygon((self.center,
                                               self.center-self.subaru_radius),
                                               3, radius=self.subaru_radius,
                                               orientation=math.pi,
                                               fc='b', ec='none', alpha=0.5)
        self.axes.add_patch(self.subaru)


        # subaru text
        # self.axes.text(self.center, self.center, 'S',
        #                color='g', ha='center', va='center',
        #                fontsize=30, weight='bold',
        #                transform=self.axes.transAxes)
        #s_txt.set_rotation(angle)

        # subaru telescope
        subaru = mpatches.Circle((self.center, self.center),
                                  radius=self.subaru_radius,
                                  alpha=1, ec="b", fc='white', lw=2.5)


        # outter circle
        outer_c = Circle((self.center, self.center), radius=0.492,
                         fc="None", ec=self.normal_color, lw=1.5, ls='solid',
                         transform=self.axes.transAxes )
        self.axes.add_patch(outer_c)

        # telescope elevation
        self.el_kwargs = dict(r=0.5, theta2=180, alpha=0.5, lw=0.5, width=0.25)
        self.el = mpatches.Wedge((self.center, self.center), theta1=90,
                                  fc=self.normal_color, ec=self.normal_color,
                                  **self.el_kwargs)
        self.axes.add_patch(self.el)

        # light path
        line_kwargs = dict(alpha=0.7, ls=':', lw=5 , color=self.normal_color,
                           ms=7.0, mew=1.0, markevery=(1,2))

        self.light = Line2D([0.5, 0.5], [0.5, 1],
                            **line_kwargs)
        self.axes.add_line(self.light)

        self.axes.add_patch(subaru)

        self.axes.set_ylim(min(self.y_scale), max(self.y_scale))
        self.axes.set_xlim(min(self.x_scale), max(self.x_scale))
        # # disable default x/y axis drawing
        #self.axes.set_xlabel(False)
        #self.axes.apply_aspect()
        self.axes.set_axis_off()

        #self.axes.set_xscale(10)
        #self.axes.axison = False

        self.draw()

    def __update_wind(self, direction, speed):

        self.logger.debug(f'updating wind. dir={direction}, speed={speed}')
        radius_inner = 0.429
        radius_outer = 0.49
        offset_deg = 4.7
        try:
            #direction +=90 # adjust drawing north:up 0 east:left 90, west:right -90, south:bottom 180
            rotation = 270 # north:0 east:90 west:-90 south:180
            direction = (direction + rotation) * -1 # rotate direction and then flip it
            update_speed = speed / 100.0 # for drawing speed arrow
            # find out new position and shpe of both wind-direction and wind-spped

            a_x, a_y = self.__get_xy(degree=direction+offset_deg,
                                     radius=radius_outer)
            b_x, b_y = self.__get_xy(degree=direction-offset_deg,
                                     radius=radius_outer)
            c_x, c_y = self.__get_xy(degree=direction,
                                     radius=radius_inner-update_speed)

        except Exception as e:
            self.logger.error(f"error: calc wind direction: {e}")
        else:
            alpha = 0.5
            warn = 7.0
            alarm = 20.0
            if speed < warn:
                color = self.wind_color
            elif warn <= speed < alarm:
                color = self.warn_color
            else:
                color = self.alarm_color
                alpha = 0.8

            update_direction = [[a_x, a_y], [b_x, b_y], [c_x, c_y],]
            try:
                #self.logger.debug('wind set....')
                #self.wind.set_xy(update_direction)
                #self.wind_kwargs = dict(alpha=1, color=color, lw=0)
                #self.wind.set(**self.wind_kwargs)
                if self.wind is not None and self.wind.axes is not None:
                    Artist.remove(self.wind)
                self.wind_kwargs = dict(alpha=alpha, color=color, lw=0)
                self.wind = mpatches.Polygon(xy=update_direction,
                                            **self.wind_kwargs)

                self.axes.add_patch(self.wind)

            except Exception as e:
                self.logger.error(f'error: updating wind: {e}')

            #self.wind.set_xy=([[0.4, 0.9], [0.6, 0.9],[0.5, 0.8]])

    def __get_xy(self, degree, sign=1, radius=0):

        rad = math.radians(degree)
        new_y = self.center + sign * radius * math.sin(rad)
        new_x = self.center + sign * radius * math.cos(rad)

        return (new_x, new_y)

    def __update_az(self, az):

        #rotation = 270.0 # degree
        rotation = 180.0 # degree  south:0 north:180 east:-90 west:90
        try:
            #az += rotation # adjust drawing north:up 180 east:left -90, west:right 90, south:bottom 0
            new_x, new_y = self.__get_xy(degree=az, sign=-1, radius=self.subaru_radius)
        except Exception as e:
            self.logger.error(f"error: calc subaru's direction.  {e}")
        else:
            #self.arrow.xy=(new_x, new_y)
            #self.subaru._xy=(new_x, new_y)
            self.subaru.xy=(new_y, new_x)
            #self.subaru.orientation = math.radians(rotation+az)
            self.subaru.orientation = math.radians(rotation-az)
            #self.subaru.orientation = math.radians(az)

    def __update_el(self, el, state):

        color = self.normal_color
        if state == "Pointing":
            pass
        elif (el >= self.alarm_high or el <= self.alarm_low):
            color = self.alarm_color
        elif (el >= self.warn_high or el <= self.warn_low):
            color = self.warn_color

        try:
            if self.el is not None and self.el.axes is not None:
                Artist.remove(self.el)
            self.el = mpatches.Wedge((self.center, self.center),
                                      theta1=180-el,
                                      fc=color, ec=color, **self.el_kwargs)
            self.axes.add_patch(self.el)
        except Exception as e:
            self.logger.error(f'error: updating elevation: {e}')
            pass

    def __update_lightpath(self, el):

        try:
            y = math.tan(math.radians(el)) * 0.5
            self.logger.debug(f'y value {y}')
            #offset = math.fabs(offset)
        except Exception:
            pass
        else:
            # TO DO think about hardcoded values
            if el > 90.0:
                self.light.set_xdata([0.5, 1.0])
                y = math.fabs(y)
            else:

                self.light.set_xdata([0.5, 0.0])
            self.light.set_ydata([0.5, 0.495+y])

    def update_azel(self, az, el, winddir, windspeed, state):
        ''' az = TSCS.AZ
            el = TSCS.EL
            winddir = TSCL.WINDD
            windspeed = TSCL.WINDS_O
            state = STATL.TELDRIVE '''

        self.logger.debug(f'updating az={az}, el={el}, winddir={winddir}, windspeed={windspeed}, state={state}')
        self.__update_el(el, state)
        #self.__update_wind(direction=winddir, speed=windspeed)
        self.__update_az(az)
        self.__update_lightpath(el)
        self.__update_wind(direction=winddir, speed=windspeed)

        self.draw()


class M1Cover(PlotWidget):
    """ M1 Mirror """
    def __init__(self, parent=None, width=3, height=3, logger=None):

        sub = SubplotParams(left=0.0, right=1, bottom=0, top=1, wspace=0,
                            hspace=0)
        self.fig = Figure(figsize=(width, height), facecolor='white',
                          subplotpars=sub)
        super().__init__(self.fig)

        self.axes = self.fig.add_subplot(111)

        self.closed_color = 'black'
        self.open_color = 'white'
        self.onway_color = 'orange'
        self.alarm_color = 'red'

        # width/hight of widget
        self.w = 250
        self.h = 50
        self.set_min_size(self.w, self.h)
        self.set_expanding(True, False)
        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        # draw mirror
        m1_kwargs = dict(alpha=0.7, fc=self.closed_color, ec='grey', lw=2)
        self.m1 = mpatches.Wedge((0.5, 0.4), 0.495, 180, 360, **m1_kwargs)
        self.axes.add_patch(self.m1)

        # draw text
        self.text = self.axes.text(0.5, 0.5, 'Initializing', va='baseline',
                                 ha='center',
                                 transform=self.axes.transAxes, fontsize=13)

        self.axes.axison=False
        self.draw()

    def update_m1cover(self, m1cover, m1cover_onway):
        ''' m1cover = TSCV.M1Cover
            m1cover_onway = TSCV.M1CoverOnway '''

        self.logger.debug(f'updating m1cover={m1cover}, m1cover_type={type(m1cover)}, m1_onway={m1cover_onway}')

        try:
            if m1cover in ERROR:
                self.m1.set_facecolor(self.alarm_color)
                self.text.set_text('M1 Cover Undef')
            elif m1cover_onway in ERROR:
                self.m1.set_facecolor(self.alarm_color)
                self.text.set_text('M1 Cover OnWay Undef')
            elif m1cover_onway == 0x01: # m1 cover onway-open
                self.m1.set_facecolor(self.onway_color)
                self.text.set_text('M1 Cover OnWay-Open')
            elif m1cover_onway == 0x02: # m1 cover onway-close
                self.m1.set_facecolor(self.onway_color)
                self.text.set_text('M1 Cover OnWay-Closed')
            elif (m1cover & 0x5555555555555555555555) == 0x1111111111111111111111:
                self.m1.set_facecolor(self.open_color)
                self.text.set_text('M1 Cover Open')
            elif (m1cover & 0x5555555555555555555555) == 0x4444444444444444444444:
                self.m1.set_facecolor(self.closed_color)
                self.text.set_text('M1 Cover Closed')
            else:
                self.m1.set_facecolor(self.onway_color)
                self.text.set_text('M1 Cover Partial')
        except Exception as e:
            self.logger.error(f'Error: M1 cover. {e}')

        self.draw()


class CellCover(PlotWidget):
    """ AG/SV/FMOS/AO188 Plotting """
    def __init__(self, parent=None, width=3, height=3,  logger=None):

        sub = SubplotParams(left=0.0, right=1, bottom=0, top=1,
                            wspace=0, hspace=0)
        self.fig = Figure(figsize=(width, height), facecolor='white',
                          subplotpars=sub)
        super().__init__(self.fig)

        self.axes = self.fig.add_subplot(111)

        self.closed_color = 'black'
        self.open_color = 'white'
        self.onway_color = 'orange'
        self.alarm_color = 'red'

        # width/hight of widget
        self.w = 250
        self.h = 30
        self.set_expanding(True, False)
        self.set_min_size(self.w, self.h)
        self.logger = logger

        self.init_figure()

    def init_figure(self):
        ''' initial drawing '''

        # draw cell cover
        cell_kwargs = dict(alpha=0.7, fc=self.closed_color, ec='grey', lw=1.5)
        self.cell= mpatches.Rectangle((0.25, 0.75), 0.5, 0.2, **cell_kwargs)
        self.axes.add_patch(self.cell)

        # draw text
        self.text = self.axes.text(0.5, 0.5, 'Initializing', \
                                 va='top', ha='center', \
                                 transform=self.axes.transAxes, fontsize=11)

        self.axes.axison = False
        self.draw()

    def update_cell(self, cell):
        ''' cell = 'TSCV.CellCover'  '''
        self.logger.debug(f'updating cell={cell}')

        if cell == 0x01: # cell cover open
            self.text.set_text('Cell Cover Open')
            self.cell.set_facecolor(self.open_color)
        elif cell == 0x04: # cell cover close
            self.text.set_text('Cell Cover Closed')
            self.cell.set_facecolor(self.closed_color)
        elif cell == 0x00: # cell cover on-way
            self.text.set_text('Cell Cover OnWay')
            self.cell.set_facecolor(self.onway_color)
        else:  # # cell cover unknown status
            self.text.set_text('Cell Cover Undef')
            self.cell.set_facecolor(self.alarm_color)

        self.draw()


class InsRotBase(Label):
    ''' instrument rotator   '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=125,
                         height=35, logger=logger )

    def update_insrot(self, insrot, mode):
        self.logger.debug(f'insrot={insrot}, mode={mode}')

        if insrot == self.insrot_free or mode == self.mode_free:
            text = 'InsRot Free'
            color = self.warn
        elif insrot == self.insrot_link and mode == self.mode_link:
            text = 'InsRot Link'
            color = self.normal
        else:
            text = 'InsRot Undefined'
            color = self.alarm

        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)


class InsRotPf(InsRotBase):
    ''' prime focus rotator  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent, logger)

        self.insrot_free = 0x02
        self.insrot_link = 0x01
        self.mode_free = 0x20
        self.mode_link = 0x10

    def update_insrot(self, insrot, mode):
        ''' insrot=TSCV.INSROTROTATION_PF
            mode=TSCV.INSROTMODE_PF
        '''
        super().update_insrot(insrot, mode)


class InsRotCs(InsRotBase):
    ''' cassegrain rotator  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent, logger)

        self.insrot_free = 0x02
        self.insrot_link = 0x01
        self.mode_free = 0x02
        self.mode_link = 0x01

    def update_insrot(self, insrot, mode):
        ''' insrot=TSCV.InsRotRotation
            mode=TSCV.InsRotMode
        '''
        super().update_insrot(insrot, mode)


class Adc(Label):
    ''' Cs/Ns ADC  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=125, height=35,
                         logger=logger)

        self.adc_out = 16 # hex 0x10
        self.adc_in = 8 # hex 0x08
        self.mode_free = 8 # hex 0x08
        self.mode_link = 4 # hex 0x04
        self.adc_off = 2 # hex 0x02
        self.adc_on = 1 # hex 0x01

    def _adc_power(self, on_off, mode):

        power = {self.adc_off: ('ADC Free', self.alarm), \
                 self.adc_on: self._adc_mode(mode)}

        self.logger.debug(f'Adc power on_off={on_off} mode={mode}')
        try:
            #on_off = int('%s' %on_off, 16)
            text, color = power[on_off]
        except Exception as e:
            self.logger.error(f'error: adc power. {e}')
            text = 'ADC On/Off Undef'
            color = self.alarm
        finally:
            return (text, color)

    def _adc_mode(self, mode):

        adc = {self.mode_link: ('ADC Link', self.normal), \
               self.mode_free: ('ADC Free', self.alarm)}

        self.logger.debug(f'Adc mode mode={mode}')

        try:
            #mode = int('%s' %mode, 16)
            text, color = adc[mode]
        except Exception as e:
            self.logger.error(f'error: adc mode. {e}')
            text = 'ADC Mode Undef'
            color = self.alarm
        finally:
            return (text, color)

    def adc(self, on_off, mode, in_out):

        adc = {self.adc_out: ('ADC Out', self.normal), \
               self.adc_in: self._adc_power(on_off, mode)}

        self.logger.debug(f'Adc on_off={on_off}, mode={mode}, in_out={in_out}')
        try:
            #in_out = int('%s' %in_out, 16)
            text, color = adc[in_out]
        except Exception as e:
            self.logger.error(f'error: updating adc. {e}')
            text = 'ADC In/Out Undef'
            color = self.alarm
        finally:
            return (text, color)

    def update_adc(self, on_off, mode, in_out):
        ''' on_off = TSCV.ADCOnOff
            mode = TSCV.ADCMode
            in_out = TSCV.ADCInOut
        '''
        self.logger.debug(f'on_off={on_off}, mode={mode}, in_out={in_out}')

        text, color = self.adc(on_off=on_off, mode=mode, in_out=in_out)
        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)


class ImgRot(Label):
    ''' image rotatro  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=125, height=40,
                         logger=logger)

        self.img_out = 'ImgRot Out'
        self.img_free = 'ImgRot Free'
        self.img_link = 'ImgRot Link'
        self.img_zenith = 'ImgRot Zenith'
        self.img_undef = 'ImgRot Undefined'

    def update_imgrot(self, imgrot, mode, focus):
        ''' imgrot=TSCV.ImgRotRotation
            mode=TSCV.ImgRotMode
            focus=TSCV.FOCUSINFO
        '''

        imgout = [0x10000000, 0x20000000,  0x00040000,
                  0x00100000, 0x00200000,  0x00000400,
                  0x00002000, 0x00004000,  0x00000008, 0x00000000]

        color = self.normal

        if focus in imgout:
            text = self.img_out
        elif imgrot == 0x02 or mode == 0x02:
            text = self.img_free
            color=self.warn
        elif imgrot == 0x01 and mode == 0x01:
            text = self.img_link
        elif imgrot == 0x01 and mode == 0x40:
            text = self.img_zenith
        else:
            text = self.img_undef
            color = self.alarm
        return (text, color)


class ImgRotNsOpt(ImgRot):
    '''  Nasmyth Optical image rotator  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, logger=logger)

    def update_imgrot(self, imgrot, mode, focus, itype):

        self.logger.debug(f'imgrot={imgrot}, mode={mode}, focus={focus}, itype={itype}')

        # img-rot blue
        imrb = [0x40000000, 0x80000000, 0x00400000, 0x00800000, 0x00008000, 0x00000001]
        # img-rot red
        imrr = [0x00010000, 0x00020000,  0x00000100, 0x00000200, 0x00000002, 0x00000004]

        # image-rot type
        itypes = {0x12:imrb, 0x10:'(OnWay-Blue)', 0x0C:imrr, 0x04:'(OnWay-Red)', 0x14:'(none type)'}

        text, color = ImgRot.update_imgrot(self, imgrot, mode, focus)

        if text in [self.img_free, self.img_link, self.img_zenith]:

            try:
                res = itypes[itype]
                self.logger.debug('itype={res}')
            except KeyError:
                text += '\n(type undef)'
                color = self.warn
            else:
                if type(res) == list:
                    if focus in imrb:
                        text += '\n(Blue)'
                    elif focus in imrr:
                        text += '\n(Red)'
                    else:
                        text += '\n(type undef)'
                        color = self.warn
                else:
                    text += '\n'+res

        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)


class ImgRotNsIr(ImgRot):
    ''' state of the telescope in pointing/slewing/tracking/guiding  '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, logger=logger)

    def update_imgrot(self, imgrot, mode, focus, itype=None):

        self.logger.debug(f'rot={imgrot}, mode={mode}, focus={focus}')

        aoin = 0x00000000
        text, color = ImgRot.update_imgrot(self, imgrot, mode, focus)

        if text == self.img_out:
            if focus == aoin:
                self.logger.debug(f'focus ao={focus}')
                text += '\n(AO In)'
            else:
                text += '\n(AO Out)'

        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)


class AdcPf(Adc):
    ''' Prime ADC '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent, logger)
        self.mode_free = 128 # hex 0x80
        self.mode_link = 64 # hex 0x40
        # self.adc_off = 0 # hex 0x00
        # self.adc_on = 1 # hex 0x01 # need to check the value

    def update_adc(self, on_off, mode, in_out=8):
        ''' on_off = TSCV.ADCONOFF_PF
            mode = TSCV.ADCMODE_PF
            in_out = 8(always in) #TSCV.ADCInOut
        '''
        super().update_adc(on_off, mode, in_out)


class TipChop(Label):
    ''' telescope 2nd mirror   '''
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=16, width=125,
                         height=35, logger=logger)

    def update_tipchop(self, mode, drive, data, state, focus=None, focus2=None):
        '''
           mode=TSCV.TT_Mode
           drive=TSCV.TT_Drive
           data=TSCV.TT_DataAvail
           chop_state=TSCV.TT_ChopStat
           focus=
           focus2=
        '''

        self.logger.debug(f'mode={mode}, drive={drive}, data={data}, state={state}')
        self.logger.debug(f'focus={focus}, focus2={focus2}')

        color = self.normal

        if (mode in ERROR or drive in ERROR or
            data in ERROR or state in ERROR):
            text = ''
        elif not drive&0x01 and drive&0x02: # not drive on
            text = ''
        elif mode&0x47 == 0x04:  # positon mode is ok
            text = ''
        elif mode&0x47 == 0x02: # tip-tilt mode
            text = 'Tip-Tilt'
            if not data&0x01: # data not available
                color = self.warn
        elif mode&0x47 == 0x01: # chopping mode
            text = 'Chopping'
            # choppig stop/not chopping start/not chopping start ready
            if state&0x02 or (not state&0x05 == 0x05):
                color = self.warn
        else:
            text = 'Tip/Chop Undefined'
            color = self.alarm

        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)


class Stage(Label):
    def __init__(self, parent=None, name=None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=125, height=20,
                         logger=logger)
        self.name = name

    def update_stage(self, stage):

        self.logger.debug(f'stage={stage}')

        try:
            stage = float(stage)
            assert -0.0001 < stage < 0.0001  # stage=0.0
            text = '%s Out' %self.name
            color = self.normal
            bg = self.bg
        except AssertionError:
            try:
                assert 54.9999 < stage < 55.00001  # stage=55.0
                text = '%s In' %self.name
                color = self.bg
                bg = self.normal
            except AssertionError:
                text = '%s Undef' %self.name
                color = self.alarm
                bg = self.bg
        except Exception as e:
            text = '%s Undef' %self.name
            color = self.alarm
            bg = self.bg
        finally:
            self.set_text(text)
            self.set_color(fg=color, bg=bg)


class Waveplate(Widgets.VBox):
    ''' Waveplate Stage   '''
    def __init__(self, parent=None, logger=None):
        super().__init__()

        self.stage1 = Stage(parent=parent, name='Polarizer', logger=logger)
        self.stage2 = Stage(parent=parent, name='1/2 WP', logger=logger)
        self.stage3 = Stage(parent=parent, name='1/4 WP', logger=logger)
        self.logger = logger

        self._set_layout()

    def _set_layout(self):
        self.set_spacing(1)
        self.set_margins(0, 0, 0, 0)
        self.add_widget(self.stage1)
        self.add_widget(self.stage2)
        self.add_widget(self.stage3)

    def update_waveplate(self, stage1, stage2, stage3):
        ''' stage1=WAV.STG1_PS
            stage2=WAV.STG2_PS
            stage3=WAV.STG3_PS
            #focus = TSCV.FOCUSINFO
        '''
        self.logger.debug(f's1={stage1}, s2={stage2}, s3={stage3}')
        self.stage1.update_stage(stage1)
        self.stage2.update_stage(stage2)
        self.stage3.update_stage(stage3)


class Shutter(Label):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=70, height=20,
                         logger=logger)

        self.status = {'OPEN': self.alarm, 'CLOSE': self.normal}

    def shutter(self, shutter):
        self.logger.debug(f'shutter={shutter}')
        try:
            color = self.status[shutter]
            text = shutter
        except Exception:
            color = self.alarm
            text = 'Undef'

        self.set_text(text)
        self.set_color(fg=color, bg=self.bg)


class AoShutter(Widgets.VBox):
    ''' AO Shutters  '''
    def __init__(self, parent=None, logger=None):
        super().__init__()
        self.set_spacing(1)
        self.set_margins(0, 0, 0, 0)

        self.lwsh_label = Label(parent=parent, fs=11.5, width=50,
                                 height=20, align='vcenter', weight='normal',
                                 logger=logger)

        self.hwsh_label = Label(parent=parent, fs=11.5, width=50,
                                 height=20, align='vcenter', weight='normal',
                                 logger=logger)

        self.lwsh_label.set_text('  LWSH:')
        #self.lwsh_label.setIndent(2)
        self.hwsh_label.set_text('  HWSH:')
        #self.hwsh_label.setIndent(2)

        self.lwsh = Shutter(parent=parent, logger=logger)
        self.hwsh = Shutter(parent=parent, logger=logger)
        self.logger = logger

        self._set_layout()

    def _set_layout(self):
        lwshHbox = Widgets.HBox()
        lwshHbox.set_spacing(0)
        lwshHbox.set_margins(0, 0, 0, 0)
        lwshHbox.add_widget(self.lwsh_label)
        lwshHbox.add_widget(self.lwsh)

        hwshHbox = Widgets.HBox()
        hwshHbox.set_spacing(0)
        hwshHbox.set_margins(0, 0, 0, 0)
        hwshHbox.add_widget(self.hwsh_label)
        hwshHbox.add_widget(self.hwsh)

        self.add_widget(lwshHbox)
        self.add_widget(hwshHbox)

    def update_aoshutter(self, lwsh, hwsh):
        ''' lwsh = AON.LWFS.LASH
            hwsh = AON.HWFS.LASH
        '''
        self.logger.debug(f'lwsh={lwsh}, hwsh={hwsh}')

        self.lwsh.shutter(lwsh)
        self.hwsh.shutter(hwsh)


class M3(Label):

    def __init__(self, parent = None, logger=None):
        super().__init__(parent=parent, fs=11.5, width=125, height=35,
                         logger=logger)

    def update_m3(self, m3):
        ''' cell = 'TSCV.CellCover'  '''
        self.logger.debug(f'updating m3={m3}')

        if m3 == 0x09:
            self.set_text('NS OPT M3 In')
            color = self.normal

        elif m3 == 0x06:
            self.set_text('NS IR M3 In')
            color = self.normal

        elif m3 == 0x0a:
            self.set_text('M3 Out')
            color = self.normal

        else:
            self.set_text('M3 Conflict')
            color = self.alarm

        self.set_color(fg=color, bg=self.bg)


class Dummy(Widgets.Label):
    def __init__(self, parent=None, width=125, height=60, logger=None):
        super().__init__('')

        self.bg = 'white'

        self.resize(width, height)
        self.set_color(fg=self.bg, bg=self.bg)
