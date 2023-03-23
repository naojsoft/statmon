#!/usr/bin/env python

import sys
import os

from CustomLabel import Label, QtCore, QtWidgets, ERROR
from g2base import ssdlog
from g2cam.status.common import STATNONE, STATERROR

long = int

progname = os.path.basename(sys.argv[0])


class Stage(Label):
    def __init__(self, parent=None, name=None, logger=None):
        super(Stage, self).__init__(parent=parent, fs=11.5, width=125, \
                                    height=20, logger=logger )
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
                assert 54.9999 < stage < 55.00001 # stage=55.0
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
            self.setText(text)
            self.setStyleSheet("QLabel {color: %s; background-color: %s}" \
                               %(color, bg))


class Waveplate(QtWidgets.QWidget):
    ''' Waveplate Stage   '''
    def __init__(self, parent=None, logger=None):
        super(Waveplate, self).__init__(parent)

        self.stage1 = Stage(parent=parent, name='Polarizer', logger=logger)
        self.stage2 = Stage(parent=parent, name='1/2 WP', logger=logger)
        self.stage3 = Stage(parent=parent, name='1/4 WP', logger=logger)
        self.logger = logger

        self._set_layout()

    def _set_layout(self):
        wavelayout = QtWidgets.QVBoxLayout()
        wavelayout.setSpacing(1)
        wavelayout.setContentsMargins(0, 0, 0, 0)
        wavelayout.addWidget(self.stage1)
        wavelayout.addWidget(self.stage2)
        wavelayout.addWidget(self.stage3)
        self.setLayout(wavelayout)

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

    def tick(self):
        ''' testing solo mode '''
        import random
        random.seed()

        findx = random.randrange(0, 35)
        sindx = random.randrange(0, 3)

        foci = [0x01000000, 0x02000000, 0x04000000, 0x08000000,
              0x10000000, 0x20000000, 0x40000000, long(0x80000000),
              0x00010000, 0x00020000, 0x00040000, 0x00080000,
              0x00100000, 0x00200000, 0x00400000, 0x00800000,
              0x00000100, 0x00000200, 0x00000400, 0x00000800,
              0x00001000, 0x00002000, 0x00004000, 0x00008000,
              0x00000001, 0x00000002, 0x00000004, 0x00000008,
              0x00000010, 0x00000000,
              "Unknown", None, STATNONE, STATERROR]

        stage = [0.0, 55.0, None]

        try:
            focus = foci[findx]
            stage = stage[sindx]
        except Exception as e:
            focus = 0x00000008
            stage = 0.0
            print(e)
        self.update_waveplate(stage1=stage, stage2=stage, stage3=stage)


def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('waveplate', options)

    class AppWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AppWindow, self).__init__()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.w=125; self.h=60;
            self.init_ui()

        def init_ui(self):
            self.resize(self.w, self.h)

            self.main_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.main_widget)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            w = Waveplate(parent=self.main_widget, logger=logger)
            l.addWidget(w)

            timer = QtCore.QTimer(self)
            timer.timeout.connect(w.tick)
            timer.start(options.interval)

            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)
            self.statusBar().showMessage("Waveplate starting..." , options.interval)

        def closeEvent(self, ce):
            self.close()

    try:
        qApp = QtWidgets.QApplication(sys.argv)
        aw = AppWindow()
        aw.setWindowTitle("%s" % progname)
        aw.show()
        sys.exit(qApp.exec_())
    except KeyboardInterrupt as e:
        logger.warn('keyboard interruption....')
        sys.exit(0)


if __name__ == '__main__':
    # Create the base frame for the widgets
    from argparse import ArgumentParser

    argprs = ArgumentParser(description="EL status")

    argprs.add_argument("--debug", dest="debug", default=False, action="store_true",
                      help="Enter the pdb debugger on main()")
    argprs.add_argument("--display", dest="display", metavar="HOST:N",
                      help="Use X display on HOST:N")
    argprs.add_argument("--profile", dest="profile", action="store_true",
                      default=False,
                      help="Run the profiler on main()")
    argprs.add_argument("--interval", dest="interval", type=int,
                      default=1000,
                      help="Inverval for plotting(milli sec).")

    ssdlog.addlogopts(argprs)
    (options, args) = argprs.parse_known_args(sys.argv[1:])

    if len(args) != 0:
        argprs.error("incorrect number of arguments")

    if options.display:
        os.environ['DISPLAY'] = options.display

    # Are we debugging this?
    if options.debug:
        import pdb

        pdb.run('main(options, args)')

    # Are we profiling this?
    elif options.profile:
        import profile

        print("%s profile:" % sys.argv[0])
        profile.run('main(options, args)')

    else:
        main(options, args)
