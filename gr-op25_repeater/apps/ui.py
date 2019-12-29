# FreqShow user interface classes.
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
import pygame


# Alignment constants.
ALIGN_LEFT   = 0.0
ALIGN_TOP    = 0.0
ALIGN_CENTER = 0.5
ALIGN_RIGHT  = 1.0
ALIGN_BOTTOM = 1.0

def align(child, parent, horizontal=ALIGN_CENTER, vertical=ALIGN_CENTER, hpad=0, vpad=0):
    """Return tuple of x, y coordinates to render the provided child rect
    aligned inside the parent rect using the provided horizontal and vertical
    alignment.  Each alignment value can be ALIGN_LEFT, ALIGNT_TOP, ALIGN_CENTER,
    ALIGN_RIGHT, or ALIGN_BOTTOM.  Can also specify optional horizontal padding
    (hpad) and vertical padding (vpad).
    """
    cx, cy, cwidth, cheight = child
    px, py, pwidth, pheight = parent
    return (px+(horizontal*pwidth-horizontal*cwidth)+hpad,
            py+(vertical*pheight-vertical*cheight)+vpad)

font_cache = {}
def get_font(size):
    """Get font of the specified size.  Will cache fonts internally for faster
    repeated access to them.
    """
    if size not in font_cache:
        font_cache[size] = pygame.font.Font(None, size)
    return font_cache[size]

def render_text(text, size=64, fg=(255, 255, 255), bg=(0, 0, 0)):
    """Render the provided text to a surface which is returned."""
    if bg is not None:
        # Optimized case when the background is known.
        return get_font(size).render(text, True, fg, bg)
    else:
        # Less optimized case with transparent background.
        return get_font(size).render(text, True, fg)

class Button(object):
    # Default color and other button configuration.  Can override these values
    # to change all buttons.
    fg_color     = (255, 255, 255)
    bg_color     = (60, 60, 60)
    border_color = (200, 200, 200)
    padding_px   = 2
    border_px    = 2
    font_size    = 33

    def __init__(self, rect, text, click=None, font_size=None, bg_color=None):
        self.text = text
        self.bg_color = bg_color if bg_color is not None else self.bg_color
        self.font_size = font_size if font_size is not None else self.font_size
        self.click_func = click
        # Determine rendered dimensions based on padding.
        x, y, width, height = rect
        x += self.padding_px
        y += self.padding_px
        width -= 2*self.padding_px
        height -= 2*self.padding_px
        self.rect = (x, y, width, height)
        # Draw label centered in the button for quick rendering later.
        self.label = render_text(text, size=self.font_size, fg=self.fg_color,
        bg=self.bg_color)
        self.label_pos = align(self.label.get_rect(), self.rect)
    
    def place(self, rect):
        x, y, width, height = rect
        x += self.padding_px
        y += self.padding_px
        width -= 2*self.padding_px
        height -= 2*self.padding_px
        self.rect = (x, y, width, height)
        # Draw label centered in the button for quick rendering later.
        self.label = render_text(self.text, size=self.font_size, fg=self.fg_color, bg=self.bg_color)
        self.label_pos = align(self.label.get_rect(), self.rect)
    
    def render(self, screen):
        self.label = render_text(self.text, size=self.font_size, fg=self.fg_color, bg=self.bg_color)
        self.label_pos = align(self.label.get_rect(), self.rect)
        screen.fill(self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_px)
        screen.blit(self.label, self.label_pos)
    
    def click(self, location):
        """Click handler will fire the button's click handler if the provided
        location x, y tuple is inside the button.
        """
        x, y, width, height = self.rect
        mx, my = location
        if mx >= x and mx <= (x + width) and my >= y and my <= (y + height) and self.click_func is not None:
            #print ('click Func: {} {} {} - {}'.format(x,y, width, height))
            self.click_func(self)

class Label(Button):
    bg_color     = (0, 0, 0)
    def __init__(self, rect, text, click=None, font_size=None, bg_color=None):
        self.text = text
        self.bg_color = bg_color if bg_color is not None else self.bg_color
        self.font_size = font_size if font_size is not None else self.font_size
        self.click_func = click
        # Determine rendered dimensions based on padding.
        x, y, width, height = rect
        x += self.padding_px
        y += self.padding_px
        width -= 2*self.padding_px
        height -= 2*self.padding_px
        self.rect = (x, y, width, height)
        # Draw label centered in the button for quick rendering later.
        self.label = render_text(text, size=self.font_size, fg=self.fg_color,
        bg=self.bg_color)
        self.label_pos = align(self.label.get_rect(), self.rect)
        
    def render(self, screen):
        self.label = render_text(self.text, size=self.font_size, fg=self.fg_color, bg=self.bg_color)
        self.label_pos = align(self.label.get_rect(), self.rect)
        #screen.fill(self.bg_color, self.rect)
        #pygame.draw.rect(screen, self.border_color, self.rect, self.border_px)
        screen.blit(self.label, self.label_pos)

class TGIDButton(Button):
    
    def __init__(self, text, system, tgid, tagTime, enabled=True, click=None, font_size=None, bg_color=None):
        #print('Created TGIDButton * {} * {}'.format(text, click))
        self.system = system
        self.tgid = tgid
        self.text = text
        self.tagTime = tagTime
        self.bg_color = bg_color if bg_color is not None else self.bg_color
        self.font_size = font_size if font_size is not None else self.font_size
        if enabled is False:
            self.bg_color = (255, 0, 0)
        
        self.click_func = click
        # Determine rendered dimensions based on padding.
    
    def render(self, screen):
        self.label = render_text(self.text, size=self.font_size, fg=self.fg_color, bg=self.bg_color)
        self.label_pos = align(self.label.get_rect(), self.rect)
        screen.fill(self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_px)
        screen.blit(self.label, self.label_pos)
        
    def click(self, location):
        x, y, width, height = self.rect
        mx, my = location
        if mx >= x and mx <= (x + width) and my >= y and my <= (y + height) \
            and self.click_func is not None:
            self.click_func(self, self.system, self.tgid)

class ButtonGrid(object):
    def __init__(self, width, height, cols, rows):
        self.col_size = width / cols
        self.row_size = height / rows
        self.buttons = []

    def add(self, col, row, text, rowspan=1, colspan=1, **kwargs):
        x = col*self.col_size
        y = row*self.row_size
        width = colspan*self.col_size
        height = rowspan*self.row_size
        
        button = Button((x,y,width,height), text, **kwargs)
        self.buttons.append(button)

    def render(self, screen):
        for button in self.buttons:
            button.render(screen)
            
    def click(self, location):
        
        for button in self.buttons:
            #try:
                button.click(location)
            #except AttributeError:
            #    print 'Cant Click Button: {}'.format(button.text)
            
class TGIDButtonGrid(ButtonGrid):
    def __init__(self, width, height, cols, rows):
        self.col_size = width / cols
        self.row_size = height / rows
        #self.buttons = []
        self.tagHistory = {}
 
    def readTag(self, msg, tagTime):
        
        if msg['tag']:
            if not msg['tgid'] in self.tagHistory:
                #self.tagHistory[msg['tgid']] = { 'system': msg['system'], 'tag': '{}'.format(msg['tag']), 'time': tagTime, 'enabled': True}
                self.tagHistory[msg['tgid']] = TGIDButton('{}'.format(msg['tag']), '{}'.format(msg['system']), '{}'.format(msg['tgid']), tagTime)
            else:
                self.tagHistory[msg['tgid']].time = tagTime
                #print 'UPDATING TIME!!!! {}'.format(self.tagHistory[msg['tgid']]['time'])
        else:
            print ('msg: %s' % msg)
            
        #self.tagHistory.append(tgidButton)
        
    def render(self, screen):
        col = 0
        row = 0
        #for tgidButton in sorted(self.buttons, key=lambda x:x.tagTime, reverse=True):
        for tag in self.tagHistory:
            print ('TGIDButtonGrid rendering tagHistory: {}'.format(tag))
            """
            x = col*self.col_size
            y = row*self.row_size
            width = self.col_size
            height = self.row_size
            #print tgidButton
            if isinstance(button, TGIDButton):
                button.place((x,y,width,height))
                print '*** rendering button: {} at {} : {}'.format(button.text, col, row)
            
            button.render(screen)
            
            col = col + 1
            if col > self.col_size:
                col = 0
                row = row + 1
            if row > self.row_size:
                break
            """
            
class LabelGrid(object):
    def __init__(self, width, height, cols, rows):
        """Create grid of buttons with the provided total width and height in
        pixels and subdivided into cols x rows equally sized buttons.
        """
        self.col_size = width / cols
        self.row_size = height / rows
        self.labels = {}
        
    def __getitem__(self, key):
        return self.labels[key]
        
    def add(self, col, row, key, text=None, rowspan=1, colspan=1, **kwargs):

        if text is None:
            text = key

        x = col*self.col_size
        y = row*self.row_size
        width = colspan*self.col_size
        height = rowspan*self.row_size

        self.labels[key] = Label((x,y,width,height), text, **kwargs)
    
    def setText(self, key, value):
        self.labels[key].text = value

    def getText(self, key):
        return self.labels[key].text

    def render(self, screen):
        for label in self.labels.values():
            label.render(screen)

    def click(self, location):
        """Handle click events at the provided location tuple (x, y) for all the
        buttons.
        """
        for label in self.labels.values():
            label.click(location)
