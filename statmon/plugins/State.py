#
# T. Inagaki
#
from CustomLabel import Label, ERROR


class State(Label):
    ''' state of the telescope in pointing/slewing/tracking/guiding  '''
    def __init__(self, parent=None, logger=None ):
        super().__init__(parent=parent, fs=23, fg='white', bg='green',
                         logger=logger)

    def update_state(self, state, intensity, valerr, calc_mode=None):
        ''' state = STATL.TELDRIVE,
            intensity = TSCL.AG1Intensity | TSCL.SV1Intensity
                        TSCL.AGPIRIntensity | TSCL.AGFMOSIntensity
                        TSCL.HSC.SCAG.Intensity | TSCL.HSC.SHAG.Intensity
                        TSCL.PFS.AG.Intensity
            valerr = STATL.AGRERR | STATL.SVRERR
            calc_mode = STATL.SV_CALC_MODE '''

        self.logger.debug(f'state={state}, intensity={intensity}, valerr={valerr}, calc_mode={calc_mode}')

        guiding = ("Guiding(AG1)", "Guiding(AG2)", \
                   "Guiding(SV1)","Guiding(SV2)", \
                   "Guiding(AGPIR)", "Guiding(AGFMOS)", \
                   "Guiding(HSCSCAG)", "Guiding(HSCSHAG)", "Guiding(PFSAG)")
        slewing = 'Slewing'
        sv_guiding = ("Guiding(SV1)", "Guiding(SV2)")

        bg = self.normal
        if state in ERROR:
            self.logger.debug(f'state={state} in error')
            state = "Unknown"
            bg = self.alarm
        elif state == slewing:
            bg = self.warn
        elif state in guiding:
            if intensity in ERROR or valerr in ERROR:
                bg = self.alarm
            elif intensity < 1.0:
                bg = self.alarm
            elif valerr >= 1000.0:
                bg = self.alarm
            elif valerr >= 500.0:
                bg = self.warn

            # if sv guiding, add calculation mode to state
            if state in sv_guiding:
                state = '%s(%s)' %(state, calc_mode)
                self.logger.debug(f'sv state={state}')
        # else is pointing, tracking with green color

        self.logger.debug(f'state={state}, bg={bg}')
        self.set_text(state)
        self.set_color(fg=self.fg, bg=bg)
