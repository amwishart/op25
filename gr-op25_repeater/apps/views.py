# FreqShow application views.
# These contain the majority of the application business logic.
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
import math
import sys
import time

import numpy as np
import pygame

import freqshow
import ui


# Color and gradient interpolation functions used by waterfall spectrogram.
def lerp(x, x0, x1, y0, y1):
    """Linear interpolation of value y given min and max y values (y0 and y1),
	min and max x values (x0 and x1), and x value.
	"""
    return y0 + (y1 - y0) * ((x - x0) / (x1 - x0))


def rgb_lerp(x, x0, x1, c0, c1):
    """Linear interpolation of RGB color tuple c0 and c1."""
    return (math.floor(lerp(x, x0, x1, float(c0[0]), float(c1[0]))),
            math.floor(lerp(x, x0, x1, float(c0[1]), float(c1[1]))),
            math.floor(lerp(x, x0, x1, float(c0[2]), float(c1[2]))))


def gradient_func(colors):
    """Build a waterfall color function from a list of RGB color tuples.  The
	returned function will take a numeric value from 0 to 1 and return a color
	interpolated across the gradient of provided RGB colors.
	"""
    grad_width = 1.0 / (len(colors) - 1.0)

    def _fun(value):
        if value <= 0.0:
            return colors[0]
        elif value >= 1.0:
            return colors[-1]
        else:
            pos = int(value / grad_width)
            c0 = colors[pos]
            c1 = colors[pos + 1]
            x = (value % grad_width) / grad_width
            return rgb_lerp(x, 0.0, 1.0, c0, c1)

    return _fun


def clamp(x, x0, x1):
    """Clamp a provided value to be between x0 and x1 (inclusive).  If value is
	outside the range it will be truncated to the min/max value which is closest.
	"""
    if x > x1:
        return x1
    elif x < x0:
        return x0
    else:
        return x


class ViewBase(object):
    """Base class for simple UI view which represents all the elements drawn
	on the screen.  Subclasses should override the render, and click functions.
	"""

    def render(self, screen):
        pass

    def click(self, location):
        pass


class MessageDialog(ViewBase):
    """Dialog which displays a message in the center of the screen with an OK
	and optional cancel button.
	"""

    def __init__(self, model, text, accept, cancel=None):
        self.accept = accept
        self.cancel = cancel
        self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
        self.buttons.add(3, 4, 'OK', click=self.accept_click, bg_color=freqshow.ACCEPT_BG)
        if cancel is not None:
            self.buttons.add(0, 4, 'CANCEL', click=self.cancel_click, bg_color=freqshow.CANCEL_BG)
        self.label = ui.render_text(text, size=freqshow.NUM_FONT, fg=freqshow.BUTTON_FG, bg=freqshow.MAIN_BG)
        self.label_rect = ui.align(self.label.get_rect(), (0, 0, model.width, model.height))

    def render(self, screen):
        # Draw background, buttons, and text.
        screen.fill(freqshow.MAIN_BG)
        self.buttons.render(screen)
        screen.blit(self.label, self.label_rect)

    def click(self, location):
        self.buttons.click(location)

    def accept_click(self, button):
        self.accept()

    def cancel_click(self, button):
        self.cancel()


class NumberDialog(ViewBase):
    """Dialog which asks the user to enter a numeric value."""

    def __init__(self, model, label_text, unit_text, initial='0', accept=None,
                 cancel=None, has_auto=False, allow_negative=False):
        """Create number dialog for provided model and with given label and unit
		text.  Can provide an optional initial value (default to 0), an accept
		callback function which is called when the user accepts the dialog (and
		the chosen value will be sent as a single parameter), a cancel callback
		which is called when the user cancels, and a has_auto boolean if an
		'AUTO' option should be given in addition to numbers.
		"""
        self.value = str(initial)
        self.unit_text = unit_text
        self.model = model
        self.accept = accept
        self.cancel = cancel
        # Initialize button grid.
        self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
        self.buttons.add(0, 1, '1', font_size=freqshow.NUM_FONT, click=self.number_click)
        self.buttons.add(1, 1, '2', font_size=freqshow.NUM_FONT, click=self.number_click)
        self.buttons.add(2, 1, '3', font_size=freqshow.NUM_FONT, click=self.number_click)
        self.buttons.add(0, 2, '4', font_size=freqshow.NUM_FONT, click=self.number_click)
        self.buttons.add(1, 2, '5', font_size=freqshow.NUM_FONT, click=self.number_click)
        self.buttons.add(2, 2, '6', font_size=freqshow.NUM_FONT, click=self.number_click)
        self.buttons.add(0, 3, '7', font_size=freqshow.NUM_FONT, click=self.number_click)
        self.buttons.add(1, 3, '8', font_size=freqshow.NUM_FONT, click=self.number_click)
        self.buttons.add(2, 3, '9', font_size=freqshow.NUM_FONT, click=self.number_click)
        self.buttons.add(1, 4, '0', font_size=freqshow.NUM_FONT, click=self.number_click)
        self.buttons.add(2, 4, '.', font_size=freqshow.NUM_FONT, click=self.decimal_click)
        self.buttons.add(0, 4, 'DELETE', click=self.delete_click)
        if not allow_negative:
            # Render a clear button if only positive values are allowed.
            self.buttons.add(3, 1, 'CLEAR', click=self.clear_click)
        else:
            # Render a +/- toggle if negative values are allowed.
            self.buttons.add(3, 1, '+/-', click=self.posneg_click)
        self.buttons.add(3, 3, 'CANCEL', click=self.cancel_click,
                         bg_color=freqshow.CANCEL_BG)
        self.buttons.add(3, 4, 'ACCEPT', click=self.accept_click,
                         bg_color=freqshow.ACCEPT_BG)
        if has_auto:
            self.buttons.add(3, 2, 'AUTO', click=self.auto_click)
        # Build label text for faster rendering.
        self.input_rect = (0, 0, self.model.width, self.buttons.row_size)
        self.label = ui.render_text(label_text, size=freqshow.MAIN_FONT,
                                    fg=freqshow.INPUT_FG, bg=freqshow.INPUT_BG)
        self.label_pos = ui.align(self.label.get_rect(), self.input_rect,
                                  horizontal=ui.ALIGN_LEFT, hpad=10)

    def render(self, screen):
        # Clear view and draw background.
        screen.fill(freqshow.MAIN_BG)
        # Draw input background at top of screen.
        screen.fill(freqshow.INPUT_BG, self.input_rect)
        # Render label and value text.
        screen.blit(self.label, self.label_pos)
        value_label = ui.render_text('{0} {1}'.format(self.value, self.unit_text),
                                     size=freqshow.NUM_FONT, fg=freqshow.INPUT_FG, bg=freqshow.INPUT_BG)
        screen.blit(value_label, ui.align(value_label.get_rect(), self.input_rect,
                                          horizontal=ui.ALIGN_RIGHT, hpad=-10))
        # Render buttons.
        self.buttons.render(screen)

    def click(self, location):
        self.buttons.click(location)

    # Button click handlers follow below.
    def auto_click(self, button):
        self.value = 'AUTO'

    def clear_click(self, button):
        self.value = '0'

    def delete_click(self, button):
        if self.value == 'AUTO':
            # Ignore delete in auto gain mode.
            return
        elif len(self.value) > 1:
            # Delete last character.
            self.value = self.value[:-1]
        else:
            # Set value to 0 if only 1 character.
            self.value = '0'

    def cancel_click(self, button):
        if self.cancel is not None:
            self.cancel()

    def accept_click(self, button):
        if self.accept is not None:
            self.accept(self.value)

    def decimal_click(self, button):
        if self.value == 'AUTO':
            # If in auto gain, assume user wants numeric gain with decimal.
            self.value = '0.'
        elif self.value.find('.') == -1:
            # Only add decimal if none is present.
            self.value += '.'

    def number_click(self, button):
        if self.value == '0' or self.value == 'AUTO':
            # Replace value with number if no value or auto gain is set.
            self.value = button.text
        else:
            # Add number to end of value.
            self.value += button.text

    def posneg_click(self, button):
        if self.value == 'AUTO':
            # Do nothing if value is auto.
            return
        else:
            if self.value[0] == '-':
                # Swap negative to positive by removing leading minus.
                self.value = self.value[1:]
            else:
                # Swap positive to negative by adding leading minus.
                self.value = '-' + self.value


class SettingsList(ViewBase):
    """Setting list view. Allows user to modify some model configuration."""

    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        # Create button labels with current model values.
        centerfreq_text = 'CENTER FREQ: {0:0.2f} MHz'.format(model.get_center_freq())
        samplerate_text = 'SAMPLE RATE: {0:0.2f} MHz'.format(model.get_sample_rate())
        gain_text = 'GAIN: {0} dB'.format(model.get_gain())
        min_text = 'MIN: {0} dB'.format(model.get_min_string())
        max_text = 'MAX: {0} dB'.format(model.get_max_string())
        # Create buttons.
        self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
        self.buttons.add(0, 0, centerfreq_text, colspan=4, click=self.centerfreq_click)
        self.buttons.add(0, 1, samplerate_text, colspan=4, click=self.sample_click)
        self.buttons.add(0, 2, gain_text, colspan=4, click=self.gain_click)
        self.buttons.add(0, 3, min_text, colspan=2, click=self.min_click)
        self.buttons.add(2, 3, max_text, colspan=2, click=self.max_click)
        self.buttons.add(0, 4, 'BACK', click=self.controller.change_to_main)

    def render(self, screen):
        # Clear view and render buttons.
        screen.fill(freqshow.MAIN_BG)
        self.buttons.render(screen)

    def click(self, location):
        self.buttons.click(location)

    # Button click handlers follow below.
    def centerfreq_click(self, button):
        self.controller.number_dialog('FREQUENCY:', 'MHz',
                                      initial='{0:0.2f}'.format(self.model.get_center_freq()),
                                      accept=self.centerfreq_accept)

    def centerfreq_accept(self, value):
        self.model.set_center_freq(float(value))
        self.controller.waterfall.clear_waterfall()
        self.controller.change_to_settings()

    def sample_click(self, button):
        self.controller.number_dialog('SAMPLE RATE:', 'MHz',
                                      initial='{0:0.2f}'.format(self.model.get_sample_rate()),
                                      accept=self.sample_accept)

    def sample_accept(self, value):
        self.model.set_sample_rate(float(value))
        self.controller.waterfall.clear_waterfall()
        self.controller.change_to_settings()

    def gain_click(self, button):
        self.controller.number_dialog('GAIN:', 'dB',
                                      initial=self.model.get_gain(), accept=self.gain_accept,
                                      has_auto=True)

    def gain_accept(self, value):
        self.model.set_gain(value)
        self.controller.waterfall.clear_waterfall()
        self.controller.change_to_settings()

    def min_click(self, button):
        self.controller.number_dialog('MIN:', 'dB',
                                      initial=self.model.get_min_string(), accept=self.min_accept,
                                      has_auto=True, allow_negative=True)

    def min_accept(self, value):
        self.model.set_min_intensity(value)
        self.controller.waterfall.clear_waterfall()
        self.controller.change_to_settings()

    def max_click(self, button):
        self.controller.number_dialog('MAX:', 'dB',
                                      initial=self.model.get_max_string(), accept=self.max_accept,
                                      has_auto=True, allow_negative=True)

    def max_accept(self, value):
        self.model.set_max_intensity(value)
        self.controller.waterfall.clear_waterfall()
        self.controller.change_to_settings()


class SpectrogramBase(ViewBase):
    """Base class for a spectrogram view."""

    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
        self.buttons.add(0, 0, 'CONFIG', click=self.controller.change_to_settings)
        self.buttons.add(1, 0, 'SWITCH MODE', click=self.controller.toggle_main, colspan=2)
        self.buttons.add(3, 0, 'QUIT', click=self.quit_click,
                         bg_color=freqshow.CANCEL_BG)
        self.overlay_enabled = True

    def render_spectrogram(self, screen):
        """Subclass should implement spectorgram rendering in the provided
		surface.
		"""
        raise NotImplementedError

    def render_hash(self, screen, x, size=5, padding=2):
        """Draw a hash mark (triangle) on the bottom row at the specified x
		position.
		"""
        y = self.model.height - self.buttons.row_size + padding
        pygame.draw.lines(screen, freqshow.BUTTON_FG, False,
                          [(x, y), (x - size, y + size), (x + size, y + size), (x, y), (x, y + 2 * size)])

    def render(self, screen):
        # Clear screen.
        screen.fill(freqshow.MAIN_BG)
        if self.overlay_enabled:
            # Draw shrunken spectrogram with overlaid buttons and axes values.
            spect_rect = (0, self.buttons.row_size, self.model.width,
                          self.model.height - 2 * self.buttons.row_size)
            self.render_spectrogram(screen.subsurface(spect_rect))
            # Draw hash marks.
            self.render_hash(screen, 0)
            self.render_hash(screen, self.model.width / 2)
            self.render_hash(screen, self.model.width - 1)
            # Draw frequencies in bottom row.
            bottom_row = (0, self.model.height - self.buttons.row_size,
                          self.model.width, self.buttons.row_size)
            freq = self.model.get_center_freq()
            bandwidth = self.model.get_sample_rate()
            # Render minimum frequency on left.
            label = ui.render_text('{0:0.2f} Mhz'.format(freq - bandwidth / 2.0),
                                   size=freqshow.MAIN_FONT)
            screen.blit(label, ui.align(label.get_rect(), bottom_row,
                                        horizontal=ui.ALIGN_LEFT))
            # Render center frequency in center.
            label = ui.render_text('{0:0.2f} Mhz'.format(freq),
                                   size=freqshow.MAIN_FONT)
            screen.blit(label, ui.align(label.get_rect(), bottom_row,
                                        horizontal=ui.ALIGN_CENTER))
            # Render maximum frequency on right.
            label = ui.render_text('{0:0.2f} Mhz'.format(freq + bandwidth / 2.0),
                                   size=freqshow.MAIN_FONT)
            screen.blit(label, ui.align(label.get_rect(), bottom_row,
                                        horizontal=ui.ALIGN_RIGHT))
            # Render min intensity in bottom left.
            label = ui.render_text('{0:0.0f} dB'.format(self.model.min_intensity),
                                   size=freqshow.MAIN_FONT)
            screen.blit(label, ui.align(label.get_rect(), spect_rect,
                                        horizontal=ui.ALIGN_LEFT, vertical=ui.ALIGN_BOTTOM))
            # Render max intensity in top left.
            label = ui.render_text('{0:0.0f} dB'.format(self.model.max_intensity),
                                   size=freqshow.MAIN_FONT)
            screen.blit(label, ui.align(label.get_rect(), spect_rect,
                                        horizontal=ui.ALIGN_LEFT, vertical=ui.ALIGN_TOP))
            # Draw the buttons.
            self.buttons.render(screen)
        else:
            # Draw fullscreen spectrogram.
            self.render_spectrogram(screen)

    def click(self, location):
        mx, my = location
        if my > self.buttons.row_size and my < 4 * self.buttons.row_size:
            # Handle click on spectrogram.
            self.overlay_enabled = not self.overlay_enabled
        else:
            # Handle click on buttons.
            self.buttons.click(location)

    def quit_click(self, button):
        self.controller.message_dialog('QUIT: Are you sure?',
                                       accept=self.quit_accept)

    def quit_accept(self):
        sys.exit(0)


class WaterfallSpectrogram(SpectrogramBase):
    """Scrolling waterfall plot of spectrogram data."""

    def __init__(self, model, controller):
        super(WaterfallSpectrogram, self).__init__(model, controller)
        self.color_func = gradient_func(freqshow.WATERFALL_GRAD)
        self.waterfall = pygame.Surface((model.width, model.height))

    def clear_waterfall(self):
        self.waterfall.fill(freqshow.MAIN_BG)

    def render_spectrogram(self, screen):
        # Grab spectrogram data.
        freqs = self.model.get_data()
        # Scroll up the waterfall display.
        self.waterfall.scroll(0, -1)
        # Scale the FFT values to the range 0 to 1.
        freqs = (freqs - self.model.min_intensity) / self.model.range
        # Convert scaled values to pixels drawn at the bottom of the display.
        x, y, width, height = screen.get_rect()
        wx, wy, wwidth, wheight = self.waterfall.get_rect()
        offset = wheight - height
        # Draw FFT values mapped through the gradient function to a color.
        self.waterfall.lock()
        for i in range(width):
            power = clamp(freqs[i], 0.0, 1.0)
            self.waterfall.set_at((i, wheight - 1), self.color_func(power))
        self.waterfall.unlock()
        screen.blit(self.waterfall, (0, 0), area=(0, offset, width, height))


class InstantSpectrogram(SpectrogramBase):
    """Instantaneous point in time line plot of the spectrogram."""

    def __init__(self, model, controller):
        super(InstantSpectrogram, self).__init__(model, controller)

    def render_spectrogram(self, screen):
        # Grab spectrogram data.
        freqs = self.model.get_data()
        # Scale frequency values to fit on the screen based on the min and max
        # intensity values.
        x, y, width, height = screen.get_rect()
        freqs = height - np.floor(((freqs - self.model.min_intensity) / self.model.range) * height)
        # Render frequency graph.
        screen.fill(freqshow.MAIN_BG)
        # Draw line segments to join each FFT result bin.
        ylast = freqs[0]
        for i in range(1, width):
            y = freqs[i]
            pygame.draw.line(screen, freqshow.INSTANT_LINE, (i - 1, ylast), (i, y))
            ylast = y


class FRCCSettingsList(ViewBase):
    """Setting list view. Allows user to modify some model configuration."""

    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        # Create button labels with current model values.
        centerfreq_text = 'FRCC FREQ: {0:0.2f} MHz'.format(model.get_freq())

        # Create buttons.
        self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
        self.buttons.add(0, 0, centerfreq_text, colspan=4, click=self.centerfreq_click, bg_color=freqshow.INPUT_FG)
        self.buttons.add(0, 1, 'Get NAC', colspan=4, click=self.sample_click)
        # self.buttons.add(0, 2, gain_text,       colspan=4, click=self.gain_click)
        # self.buttons.add(0, 3, min_text,        colspan=2, click=self.min_click)
        # self.buttons.add(2, 3, max_text,        colspan=2, click=self.max_click)
        self.buttons.add(0, 4, 'BACK', click=self.controller.change_to_main)

    def render(self, screen):
        # Clear view and render buttons.
        screen.fill(freqshow.MAIN_BG)
        self.buttons.render(screen)

    def click(self, location):
        self.buttons.click(location)

    # Button click handlers follow below.
    def centerfreq_click(self, button):
        self.controller.number_dialog('FREQUENCY:', 'MHz', initial='{0:0.2f}'.format(self.model.get_center_freq()),
                                      accept=self.centerfreq_accept)

    def centerfreq_accept(self, value):
        self.model.set_center_freq(float(value))
        self.controller.waterfall.clear_waterfall()
        self.controller.change_to_settings()

    def sample_click(self, button):
        # self.controller.number_dialog('FREQUENCY:', 'MHz', initial='{0:0.2f}'.format(self.model.get_center_freq()), accept=self.centerfreq_accept)
        # self.controller.get_nac()
        print('Sample Click get NAC')
        print(self.controller.model.get_nac())


class ColoradoDTRSSettingsList(ViewBase):
    """Setting list view. Allows user to modify some model configuration."""

    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        # Create button labels with current model values.
        centerfreq_text = 'ColoradoDTRS FREQ: {0:0.2f} MHz'.format(model.get_freq())

        # Create buttons.
        self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
        self.buttons.add(0, 0, centerfreq_text, colspan=4, click=self.centerfreq_click, bg_color=freqshow.INPUT_FG)
        self.buttons.add(0, 1, 'Douglas SO', colspan=4, click=self.sample_click)
        # self.buttons.add(0, 2, gain_text,       colspan=4, click=self.gain_click)
        # self.buttons.add(0, 3, min_text,        colspan=2, click=self.min_click)
        # self.buttons.add(2, 3, max_text,        colspan=2, click=self.max_click)
        self.buttons.add(0, 4, 'BACK', click=self.controller.change_to_main)

    def render(self, screen):
        # Clear view and render buttons.
        screen.fill(freqshow.MAIN_BG)
        self.buttons.render(screen)

    def click(self, location):
        self.buttons.click(location)

    # Button click handlers follow below.
    def centerfreq_click(self, button):
        self.controller.number_dialog('FREQUENCY:', 'MHz', initial='{0:0.2f}'.format(self.model.get_center_freq()),
                                      accept=self.centerfreq_accept)

    def centerfreq_accept(self, value):
        self.model.set_center_freq(float(value))
        self.controller.waterfall.clear_waterfall()
        self.controller.change_to_settings()

    def sample_click(self, button):
        self.controller.model.blacklist('bar', 'Foo')
    # self.controller.number_dialog('FREQUENCY:', 'MHz', initial='{0:0.2f}'.format(self.model.get_center_freq()), accept=self.centerfreq_accept)


class SystemConfig(ViewBase):
    """Setting list view. Allows user to modify some model configuration."""

    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        # Create button labels with current model values.
        system_text = '{0} FREQ: {1:0.2f} MHz'.format(model.get_system_name(), model.get_freq())

        # Create buttons.
        self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
        self.buttons.add(0, 0, system_text, colspan=4, click=self.sample_click, bg_color=freqshow.INPUT_FG)
        self.buttons.add(0, 1, 'SystemConfig', colspan=4, click=self.sample_click)
        self.buttons.add(0, 4, 'BACK', click=self.controller.change_to_main)

    def render(self, screen):
        # Clear view and render buttons.
        screen.fill(freqshow.MAIN_BG)
        self.buttons.render(screen)

    def click(self, location):
        self.buttons.click(location)

    # Button click handlers follow below.
    def sample_click(self, button):
        print (self.controller.model)
        #self.controller.model.blacklist('bar', 'Foo')
        #self.controller.number_dialog('FREQUENCY:', 'MHz', initial='{0:0.2f}'.format(self.model.get_center_freq()), accept=self.centerfreq_accept)


import subprocess


class OP25(ViewBase):
    filterButtons = {}

    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        self.model.setCallback(self.setTags)
        self.labels = ui.LabelGrid(model.width, model.height, 4, 7)
        self.labels.add(0, 0, 'System')
        self.labels.add(1, 0, 'Freq', colspan=2)
        self.labels.add(3, 0, 'TGID')
        self.labels.add(0, 1, 'Tag', colspan=4, font_size=72)

        self.buttons = ui.ButtonGrid(model.width, model.height, 4, 7)

        self.buttons.add(3, 2, 'X', click=self.controller.exitProgram, bg_color=freqshow.CANCEL_BG)
        self.labels.add(0, 2, 'Tag1', colspan=3, font_size=36)

        self.buttons.add(3, 3, 'X', click=self.controller.exitProgram, bg_color=freqshow.CANCEL_BG)
        self.labels.add(0, 3, 'Tag2', colspan=3, font_size=36)

        self.buttons.add(3, 4, 'X', click=self.controller.exitProgram, bg_color=freqshow.CANCEL_BG)
        self.labels.add(0, 4, 'Tag3', colspan=3, font_size=36)

        self.buttons.add(3, 5, 'X', click=self.controller.exitProgram, bg_color=freqshow.CANCEL_BG)
        self.labels.add(0, 5, 'Tag4', colspan=3, font_size=36)

        # self.historyLabels = ui.ButtonGrid(model.width, model.height, 3, 6)

        self.buttons.add(0, 6, 'CO DTRS', click=self.controller.change_to_SystemConfig, bg_color=freqshow.ACCEPT_BG)
        self.buttons.add(1, 6, 'FRCC', click=self.controller.change_to_SystemConfig, bg_color=freqshow.ACCEPT_BG)
        # self.buttons.add(2, 6, 'MARC', click=self.ColoradoFRCC, bg_color=freqshow.ACCEPT_BG)
        self.buttons.add(2, 6, 'CONFIG', click=self.controller.change_to_SystemConfig)
        self.buttons.add(3, 6, 'Exit', click=self.controller.exitProgram, bg_color=freqshow.CANCEL_BG)

    # self.tgidButtonGrid = ui.TGIDButtonGrid(model.width, model.height, 4, 6)

    # self.tagLabel = ui.render_text('Tag', size=128, fg=freqshow.BUTTON_FG, bg=freqshow.MAIN_BG)
    # self.tagLabel_rect = ui.align(self.tagLabel.get_rect(), (-180, 0, model.width, model.height))

    def render(self, screen):
        screen.fill(freqshow.MAIN_BG)
        self.labels.render(screen)
        self.buttons.render(screen)

    # self.tgidButtonGrid.render(screen)

    def blacklist(self, button):
        print('***** blacklist - {}:{} ***** '.format(button.system, button.tgid))
        button.bg_color = (255, 0, 0)
        self.model.blacklist(button.system, button.tgid)

    def click(self, location):
        self.buttons.click(location)

    def new__init__(self, model, text):
        self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
        self.buttons.add(3, 4, 'Colorado DTRS', click=self.ColoradoDTRS, bg_color=freqshow.ACCEPT_BG)
        self.buttons.add(0, 4, 'Exit', click=self.exitProgram, bg_color=freqshow.CANCEL_BG)
        self.label = ui.render_text(text, size=freqshow.NUM_FONT, fg=freqshow.BUTTON_FG, bg=freqshow.MAIN_BG)
        self.label_rect = ui.align(self.label.get_rect(), (0, 0, model.width, model.height))

        """
		self.overlay_enabled = False
		self.recentlist = {}
		self.myFont = tkFont.Font(family = 'Helvetica', size = 18, weight = 'bold')
		self.largeFont = tkFont.Font(family = 'Helvetica', size = 48, weight = 'bold')

		self.root.title("OP25 GUI")
		self.root.geometry('800x480')

		self.tag.set("")
		self.talkgroup.set("")
		self.frequency.set("")

		# status bar
		status_frame = Frame(self.root)

		self.tagLabel = Label(status_frame, textvariable=self.tag, font = self.largeFont).pack(side=LEFT, fill=BOTH) 

		menu_left_frame = Frame(self.root, width=100)
		menu_center1_frame = Frame(self.root)
		menu_center2_frame = Frame(self.root)
		menu_right_frame = Frame(self.root)

		self.coloradoDTRSButton = Button(menu_center1_frame, text = "Colorado DTRS", font = self.myFont, command = self.ColoradoDTRS)
		self.coloradoDTRSButton.pack(side=TOP, fill=BOTH)


		self.addButton(menu_center1_frame, 'RTD', ['RTD'])
		self.addButton(menu_center1_frame, 'CDOT', ['CDOT'])
		self.addButton(menu_center1_frame, 'State Patrol', ['CSP'])
		self.addButton(menu_center1_frame, 'Corrections', ['CDOC'])
		self.addButton(menu_center2_frame, 'Jefferson', ['JFCO'])
		self.addButton(menu_center2_frame, 'Douglas', ['Douglas'])
		self.addButton(menu_center2_frame, 'Larimer', ['Larimer'])
		self.addButton(menu_center2_frame, 'Boulder', ['BouldrCo', 'Boulder PD'])
		self.addButton(menu_right_frame, 'SAR', ['MtnTac', 'RckyMtnRscue', 'MAC', 'Rescue'])
		self.addButton(menu_right_frame, 'CPW', ['DOW'])
		self.addButton(menu_right_frame, 'Parks', ['OPS', 'Opn'])

		exitButton  = Button(menu_left_frame, text = "Exit", bg='red', font = self.myFont, width = 20, command = self.exitProgram).pack(side=BOTTOM, fill=BOTH)

		self.menu_left_frame_canvas  = self.createCanvas(menu_left_frame)
		status_frame.grid(row=0, column=1, columnspan=3, sticky="new")
		menu_left_frame.grid(row=0, rowspan=2, column=0, sticky="nsew")
		menu_center1_frame.grid(row=1, column=1, sticky="nsew")
		menu_center2_frame.grid(row=1, column=2, sticky="nsew")
		menu_right_frame.grid(row=1, column=3, sticky="nsew")

		self.root.grid_rowconfigure(1, weight=1)
		self.root.grid_columnconfigure(1, weight=1)
		self.root.grid_columnconfigure(2, weight=1)
		self.root.grid_columnconfigure(3, weight=0)

		self.options.frequency = 853850000.0
		self.options.trunk_conf_file = 'ColoradoDTRSTrunk.tsv'
		self.guiThreading = GUIThreading(self.options, self.setTags)
		"""

    def ColoradoDTRS(self):
        print('*** Blacklisting Everything ***')
        self.tgid_map = self.guiThreading.get_tgid_map()
        self.coloradoDTRSButton["bg"] = "red"
        self.coloradoDTRSButton["extra"] = False
        print(self.coloradoDTRSButton["extra"])
        # filtered_dict = {v[0]: k for k, v in tgid_map.items()}
        filtered_dict = {v[0]: k for k, v in self.tgid_map.items()}

        for key in filtered_dict.keys():
            # print 'Blacklisting {:s} - {:d}'.format(key, filtered_dict[key])
            self.guiThreading.add_blacklist(filtered_dict[key])

    def ColoradoFRCC(self):
        print('*** Blacklisting Everything ***')
        self.tgid_map = self.guiThreading.get_tgid_map()
        self.coloradoDTRSButton["bg"] = "red"
        self.coloradoDTRSButton["extra"] = False
        print(self.coloradoDTRSButton["extra"])
        # filtered_dict = {v[0]: k for k, v in tgid_map.items()}
        filtered_dict = {v[0]: k for k, v in self.tgid_map.items()}

        for key in filtered_dict.keys():
            # print 'Blacklisting {:s} - {:d}'.format(key, filtered_dict[key])
            self.guiThreading.add_blacklist(filtered_dict[key])

    def addButton(self, frame, tag, filterValues):
        button = Button(frame, text=tag, font=self.myFont, bg='green', activebackground='green',
                        command=lambda: self.blacklistFilterList(tag))
        button.pack(side=TOP, fill=BOTH)
        self.filterButtons[tag] = {'button': button, 'filterValues': filterValues, 'enabled': False}

    def exitProgram(self, button):
        try:
            print('Exiting Program')
            stopProgram()
            pygame.quit()
            sys.exit()
            print('Exited Program')
        except:
            pass
            pygame.quit()
            sys.exit()

    def stopProgram(self):
        self.model.keep_running = False

    def createCanvas(self, parent):
        vscrollbar = Scrollbar(parent)
        canvas = Canvas(parent, yscrollcommand=vscrollbar.set)
        canvas.configure(width=parent.winfo_width(), height=parent.winfo_height())

        vscrollbar.config(command=canvas.yview)
        vscrollbar.pack(side=RIGHT, fill=Y)

        frame = Frame(canvas)
        frame.configure(width=canvas.winfo_width())

        canvas.pack(side="right", fill=BOTH, expand=True)
        canvas.create_window(0, 0, window=frame, anchor='nw')
        parent.update()

        canvas.config(scrollregion=canvas.bbox("all"))
        return canvas

    def setTags(self, msg):
        # print '{}'.format(msg)
        tagTime = time.time()
        # self.tgidButtonGrid.readTag(msg, tagTime)

        if(msg['tag'] != self.labels.getText('Tag')):
            self.labels.setText('Tag4', self.labels.getText('Tag3'))
            self.labels.setText('Tag3', self.labels.getText('Tag2'))
            self.labels.setText('Tag2', self.labels.getText('Tag1'))
            self.labels.setText('Tag1', self.labels.getText('Tag'))

            self.labels.setText('TGID', '{}'.format(msg['tgid']))
            self.labels.setText('Tag', msg['tag'])
            self.labels.setText('System', msg['system'])
            #self.labels.setText('Freq', '{}'.format(msg['freq']))
            self.labels.setText('Freq', "%f" % (msg['freq'] / 1000000.0))

            # print 'tell model to render'
            self.model.callRender()
