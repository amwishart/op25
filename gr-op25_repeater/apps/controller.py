import pygame
import sys
import view
import model

class BaseController(object):
    def __init__(self, model):
        self._current_view = None

    def change_view(self, view):
        """Change to specified view."""
        print('Change to view {}'.format(view))
        self._prev_view = self._current_view
        self._current_view = view

    def current(self):
        """Return current view."""
        return self._current_view

    def change_to_main(self, *args):
        """Change to main spectrogram view (either instant or waterfall depending on what was the last main view)."""
        print('Change to main - {}'.format(self._main_view))
        self.change_view(self._main_view)

class SystemController(BaseController):
    def __init__(self, model, op25):
        """Initialize controller with specified FreqShow model."""
        self.model = model
        self.SystemConfig = view.SystemConfig(model, self)
        self._main_view = op25
        self._current_view = None

    def change_to_main(self, *args):
        """Change to main spectrogram view (either instant or waterfall depending on what was the last main view)."""
        print('SystemController Change to main - {}'.format(self._main_view))
        self.change_view(self._main_view)

class OP25Controller(BaseController):
    def __init__(self, model):
        """Initialize controller with specified FreqShow model."""
        self.model = model
        # Create instantaneous and waterfall spectrogram views once because they
        # hold state and have a lot of data.
        self.op25 = view.OP25(model, self)
        # Start with instantaneous spectrogram.
        self._current_view = None
        #self.change_to_op25()
        self.change_view(self.op25)


    def change_to_op25(self, *args):
        """Change to op25 view."""
        self._main_view = self.op25
        self.change_view(self.op25)

    def ColoradoDTRS(self, button):
        print ('*** Blacklisting Everything ***')
        self.tgid_map = self.guiThreading.get_tgid_map()
        self.coloradoDTRSButton["bg"] = "red"
        self.coloradoDTRSButton["extra"] = False
        print (self.coloradoDTRSButton["extra"])
        # filtered_dict = {v[0]: k for k, v in tgid_map.items()}
        filtered_dict = {v[0]: k for k, v in self.tgid_map.items()}

        for key in filtered_dict.keys():
            # print 'Blacklisting {:s} - {:d}'.format(key, filtered_dict[key])
            self.guiThreading.add_blacklist(filtered_dict[key])

    def ColoradoFRCC(self, button):
        print ('*** Blacklisting Everything ***')
        self.tgid_map = self.guiThreading.get_tgid_map()
        self.coloradoDTRSButton["bg"] = "red"
        self.coloradoDTRSButton["extra"] = False
        print (self.coloradoDTRSButton["extra"])
        # filtered_dict = {v[0]: k for k, v in tgid_map.items()}
        filtered_dict = {v[0]: k for k, v in self.tgid_map.items()}

        for key in filtered_dict.keys():
            # print 'Blacklisting {:s} - {:d}'.format(key, filtered_dict[key])
            self.guiThreading.add_blacklist(filtered_dict[key])

    def exitProgram(self, button):
        try:
            print('Exiting Program')
            self.stopProgram()
            pygame.quit()
            sys.exit()
            # print('Exited Program')
        except:
            pass
            pygame.quit()
            sys.exit()

    def stopProgram(self):
        self.model.keep_running = False

    def change_to_SystemConfig(self, *args):
        print (self.model) #OP25Model
        config = self.model.get_config(1442)
        systemModel = model.SystemModel(self.model.width, self.model.height, config)
        systemController = SystemController(systemModel, self.op25)
        systemView = view.SystemConfig(systemModel, systemController)
        #self.change_view(view.SystemConfig(self.model, self))
        self.change_view(systemView)