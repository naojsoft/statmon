#!/usr/bin/env python

import os
import sys

from qtpy import QtCore, QtWidgets

from g2base import ssdlog
from Propid import PropIdDisplay
from InsName import InsNameDisplay
from Object import ObjectDisplay
from Airmass import AirmassDisplay
from Pa import PaDisplay
from TimeAz import TimeAzLimitDisplay
from TimeEl import TimeElLimitDisplay
from TimeRot import TimeRotLimitDisplay

progname = os.path.basename(sys.argv[0])

class TargetGui(QtWidgets.QWidget):
    def __init__(self, parent=None, obcp=None, logger=None):
        super(TargetGui, self).__init__(parent)

        self.obcp = obcp  # instrument 3 letter code
        self.logger = logger
        self.propid = PropIdDisplay(logger=logger)
        self.insname = InsNameDisplay(logger=logger)
        self.object = ObjectDisplay(logger=logger)
        #self.airmass = AirmassDisplay(logger=logger)
        self.pa = PaDisplay(logger=logger)
        self.time_az = TimeAzLimitDisplay(logger=logger)
        self.time_el = TimeElLimitDisplay(logger=logger)
        self.time_rot = TimeRotLimitDisplay(logger=logger)
        self.set_layout()

    def set_layout(self):
        mainlayout = QtWidgets.QVBoxLayout()
        mainlayout.setSpacing(1)
        mainlayout.setContentsMargins(0, 0, 0, 0)

        mainlayout.addWidget(self.propid)
        mainlayout.addWidget(self.insname)
        mainlayout.addWidget(self.object)
        #mainlayout.addWidget(self.airmass)
        mainlayout.addWidget(self.pa)
        mainlayout.addWidget(self.time_az)
        mainlayout.addWidget(self.time_el)
        mainlayout.addWidget(self.time_rot)
        self.setLayout(mainlayout)


class Target(TargetGui):
    def __init__(self, parent=None, obcp=None, logger=None):
        super(Target, self).__init__(parent=parent, obcp=obcp, logger=logger)

    def get_pa_status(self):

        # TODO: redo this in Derive.py (status)
        if self.obcp in ['HSC', 'PFS']:
            # PF
            return ('TSCL.INSROTPA_PF', 'STATS.ROTDIF_PF')
        elif self.obcp in ['FCS', 'MCS', 'SWS', 'MMZ', 'COM']:
            # Cass
            return ('TSCL.InsRotPA', 'STATS.ROTDIF')
        else:
            # NS_IR and NS_OPT instruments
            return ('TSCL.ImgRotPA', 'STATS.ROTDIF')

    def update_target(self, **kargs):

        self.logger.debug(f'updating telescope. kargs={kargs}')

        try:
            propid = 'FITS.{0}.PROP_ID'.format(self.obcp)
            self.propid.update_propid(propid=kargs.get(propid))

            insname = 'FITS.SBR.MAINOBCP'
            self.insname.update_insname(insname=kargs.get(insname))

            obj = 'FITS.{0}.OBJECT'.format(self.obcp)
            self.object.update_object(obj=kargs.get(obj))

            #self.airmass.update_airmass(el=kargs.get('TSCS.EL'))

            # pa = TSCL.INSROTPA_PF | TSCL.InsRotPA | TSCL.ImgRotPA
            # cmd_diff = STATS.ROTDIF_PF | STATS.ROTDIF
            pa, cmd_diff = self.get_pa_status()
            self.pa.update_pa(pa=kargs.get(pa), \
                              cmd_diff=kargs.get(cmd_diff))

            self.time_az.update_azlimit(flag=kargs.get('TSCL.LIMIT_FLAG'), \
                                        az=kargs.get('TSCL.LIMIT_AZ'),)

            self.time_el.update_ellimit(flag=kargs.get('TSCL.LIMIT_FLAG'), \
                                        low=kargs.get('TSCL.LIMIT_EL_LOW'), \
                                        high=kargs.get('TSCL.LIMIT_EL_HIGH'))

            self.time_rot.update_rotlimit(flag=kargs.get('TSCL.LIMIT_FLAG'), \
                                          rot=kargs.get('TSCL.LIMIT_ROT'), \
                                          link=kargs.get('TSCV.PROBE_LINK'), \
                                          focus=kargs.get('TSCV.FOCUSINFO'), \
                                          focus2=kargs.get('TSCV.FOCUSINFO2'))
        except Exception as e:
            self.logger.error(f'error: target update. {e}')

    def tick(self):

        self.propid.tick()
        self.insname.tick()
        self.object.tick()
        #self.airmass.tick()
        self.pa.tick()
        self.time_az.tick()
        self.time_el.tick()
        self.time_rot.tick()

def main(options, args):

    # Create top level logger.
    logger = ssdlog.make_logger('target', options)


    try:
        qApp = QtWidgets.QApplication(sys.argv)
        tel = Target(obcp=options.ins, logger=logger)
        timer = QtCore.QTimer()
        timer.timeout.connect(tel.tick)
        timer.start(options.interval)
        tel.setWindowTitle("%s" % progname)
        tel.show()
        sys.exit(qApp.exec_())

    except KeyboardInterrupt as e:
        logger.warn('keyboard interruption....')
        sys.exit(0)


if __name__ == '__main__':
    # Create the base frame for the widgets
    from argparse import ArgumentParser

    argprs = ArgumentParser(description="Target status")

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
    # note: there are sv/pir plotting, but mode ag uses the same code.
    argprs.add_argument("--mode", dest="mode",
                      default='ag',
                      help="Specify a plotting mode [ag | sv | pir | fmos]")
    argprs.add_argument("--ins", dest="ins",
                      default='HDS',
                      help="Specify 3 character code of an instrument. e.g., HDS")
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
