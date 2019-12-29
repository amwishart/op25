# FreqShow controller class.
# This owns the views and controls application movement between views.
#
# Author: Tony DiCola (tony@tonydicola.com)
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from views import *
class FreqShowController(object):
    """Class which controls the views shown in the application and mediates
    changing between views.
    """
    def __init__(self, model):
        print("************** Fooooooooo *************")
        """Initialize controller with specified FreqShow model."""
        self.model = model
        # Create instantaneous and waterfall spectrogram views once because they
        # hold state and have a lot of data.
        self.instant = InstantSpectrogram(model, self)
        self.waterfall = WaterfallSpectrogram(model, self)
        #self.op25 = OP25(self.model, 'QUIT: Are you sure?')
        #self.op25 = OP25(self.model, 'Make Me A Tag')
        # Start with instantaneous spectrogram.
        self._current_view = None
        self.change_to_instant()

    def change_view(self, view):
        """Change to specified view."""
        self._prev_view = self._current_view
        self._current_view = view

    def current(self):
        """Return current view."""
        return self._current_view

    def message_dialog(self, text, **kwargs):
        """Open a message dialog which goes back to the previous view when
        canceled.
        """
        self.change_view(MessageDialog(self.model, text, 
            cancel=self._change_to_previous, **kwargs))

    def number_dialog(self, label_text, unit_text, **kwargs):
        """Open a number dialog which goes back to the previous view when
        canceled.
        """
        self.change_view(NumberDialog(self.model, label_text, unit_text,
            cancel=self._change_to_previous, **kwargs))

    def _change_to_previous(self, *args):
        # Change to previous view, note can only go back one level.
        self.change_view(self._prev_view)

    # Functions that switch between views and are able to work as a click handler
    # because they ignore any arguments passed in (like clicked button).
    def change_to_main(self, *args):
        """Change to main spectrogram view (either instant or waterfall depending
        on what was the last main view).
        """
        self.change_view(self._main_view)

    def toggle_main(self, *args):
        """Switch between instantaneous and waterfall spectrogram views."""
        if self._current_view == self.waterfall:
            self.change_to_instant()
        else:
            self.change_to_waterfall()

    def change_to_instant(self, *args):
        """Change to instantaneous spectrogram view."""
        self._main_view = self.instant
        self.change_view(self.instant)

    def change_to_waterfall(self, *args):
        """Change to waterfall spectrogram view."""
        self._main_view = self.waterfall
        self.change_view(self.waterfall)

    def change_to_settings(self, *args):
        """Change to settings list view."""
        # Create a new settings list view object because the setting values might
        # change and need to be rendered with different values.
        self.change_view(SettingsList(self.model, self))

class OP25Controller(object):
    def __init__(self, model):
        """Initialize controller with specified FreqShow model."""
        self.model = model
        # Create instantaneous and waterfall spectrogram views once because they
        # hold state and have a lot of data.
        self.op25 = OP25(model, self)
        # Start with instantaneous spectrogram.
        self._current_view = None
        self.change_to_op25()
    def current(self):
        """Return current view."""
        return self._current_view
        
    def change_view(self, view):
        """Change to specified view."""
        self._prev_view = self._current_view
        self._current_view = view

    def change_to_op25(self, *args):
        """Change to op25 view."""
        self._main_view = self.op25
        self.change_view(self.op25)
    
    def change_to_main(self, *args):
        """Change to main spectrogram view (either instant or waterfall depending on what was the last main view)."""
        self.change_view(self._main_view)
    
    def ColoradoDTRS(self, button):
        print ('*** Blacklisting Everything ***')
        self.tgid_map = self.guiThreading.get_tgid_map()
        self.coloradoDTRSButton["bg"]="red"
        self.coloradoDTRSButton["extra"]=False
        print (self.coloradoDTRSButton["extra"])
        #filtered_dict = {v[0]: k for k, v in tgid_map.items()}
        filtered_dict = {v[0]: k for k, v in self.tgid_map.items() }

        for key in filtered_dict.keys():
            #print 'Blacklisting {:s} - {:d}'.format(key, filtered_dict[key])
            self.guiThreading.add_blacklist(filtered_dict[key])

    def ColoradoFRCC(self, button):
        print ('*** Blacklisting Everything ***')
        self.tgid_map = self.guiThreading.get_tgid_map()
        self.coloradoDTRSButton["bg"]="red"
        self.coloradoDTRSButton["extra"]=False
        print (self.coloradoDTRSButton["extra"])
        #filtered_dict = {v[0]: k for k, v in tgid_map.items()}
        filtered_dict = {v[0]: k for k, v in self.tgid_map.items() }

        for key in filtered_dict.keys():
            #print 'Blacklisting {:s} - {:d}'.format(key, filtered_dict[key])
            self.guiThreading.add_blacklist(filtered_dict[key])
    
    def exitProgram(self, button):
        try:
            print('Exiting Program')
            stopProgram()
            pygame.quit()
            sys.exit()
            #print('Exited Program')
        except:
            pass	
            pygame.quit()
            sys.exit()
    
    def change_to_ColoradoDTRS(self, *args):
        self.change_view(ColoradoDTRSSettingsList(self.model, self))
        
    def change_to_ColoradoFRCC(self, *args):
        self.change_view(FRCCSettingsList(self.model, self))

    def change_to_SystemConfig(self, *args):
        self.change_view(SystemConfig(self.model, self))

    def get_nac(self, *args):
        print ('controller get_nac')
        print (self.op25.model.get_nac())