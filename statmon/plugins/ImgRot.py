#
# T. Inagaki
#
from CustomLabel import Label
from g2cam.status.common import STATNONE, STATERROR


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
