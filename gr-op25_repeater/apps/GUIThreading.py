import os
import pickle
import sys
import threading
import math
import numpy
import time
import re
import json
import traceback
try:
    import Hamlib
except:
    pass

try:
    import Numeric
except:
    pass

#from gnuradio import audio, eng_notation, gr, gru, filter, blocks, fft, analog, digital
#from gnuradio.eng_option import eng_option
from math import pi
from optparse import OptionParser

#import op25
#import op25_repeater

import trunking

import p25_demodulator
import p25_decoder

sys.path.append('tdma')
#import lfsr

from gr_gnuplot import constellation_sink_c
from gr_gnuplot import fft_sink_c
from gr_gnuplot import symbol_sink_f
from gr_gnuplot import eye_sink_f
from gr_gnuplot import mixer_sink_c

from terminal import op25_terminal
from sockaudio  import audio_thread
from rx import p25_rx_block

#speeds = [300, 600, 900, 1200, 1440, 1800, 1920, 2400, 2880, 3200, 3600, 3840, 4000, 4800, 6000, 6400, 7200, 8000, 9600, 14400, 19200]
speeds = [4800, 6000]

os.environ['IMBE'] = 'soft'

WIRESHARK_PORT = 23456

_def_interval = 1.0	# sec
_def_file_dir = '../www/images'

class gui_du_queue_watcher(threading.Thread):

    def __init__(self, msgq,  callback, **kwds):
        #print("init gui_du_queue")
        threading.Thread.__init__ (self, **kwds)
        self.setDaemon(1)
        self.msgq = msgq
        self.callback = callback
        self.keep_running = True
        self.start()

    def run(self):
        while(self.keep_running):
            msg = self.msgq.delete_head()
            #print ("*** self.msgq.delete_head %s" % msg)
            self.callback(msg)

class GUIThreading(object):
    def __init__(self, options, callback=None):
        self.options = options
        self.keep_running = True
        self.callback = callback
        self.tb = None
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
    
    def setCallback(self, callback=None):
        #print('setting callback in GUIThreading 1')
        if(self.tb != None):
            #print ('setting callback in GUIThreading')
            self.tb.setCallback(callback)
        else: 
            #print ('cant set callback in GUIThreading yet.  set in local and then it will get set on start')
            self.callback = callback
        
    def run(self):
        #print('Running in Thread\r\n')
        self.tb = p25_rx_block(self.options, self.callback)
        self.q_watcher = gui_du_queue_watcher(self.tb.output_q, self.process_qmsg)

        print('self.tb.trunk_rx')
        print (self.tb.trunk_rx)
        try:
            self.tb.start()
            self.tb.get_nac()
            
            if self.options.symbols:
                self.tb.wait()
            else:
                while self.keep_running:
                    time.sleep(1)
                    if self.tb.callback != self.callback:
                        self.tb.setCallback(self.callback)
        except:
            sys.stderr.write('main: exception occurred\n')
            sys.stderr.write('main: exception:\n%s\n' % traceback.format_exc())
            if self.tb.terminal:
                self.tb.terminal.end_terminal()
            if self.tb.meta_server:
                self.tb.meta_server.stop()
            if self.tb.audio:
                self.tb.audio.stop()
                self.tb.stop()
                print ("self.tb.stop()")

        for sink in self.tb.plot_sinks:
            sink.kill()

    def process_qmsg(self, msg):
        #print ("*** process_qmsg %s\r\n" % msg)
        if self.tb.process_qmsg(msg):
            #self.tb.stop()
            self.keep_running = False

    def add_blacklist(self, current_tgid):
        #print 'GUIThreading add_blacklist %s ' % current_tgid
        self.tb.add_blacklist(current_tgid)

    def remove_blacklist(self, current_tgid):
        print ('GUIThreading remove_blacklist %s ' % current_tgid)
        self.tb.remove_blacklist(current_tgid)
    
    def get_tgid_map(self, nac):
        print ("GUIThreading: Getting tgid_map")
        return self.tb.get_tgid_map(nac)
        
    def get_nac(self):
        #print ("GUIThreading: Getting get_nac")
        return self.tb.get_nac()

    def get_trunked_systems(self):
        print ("GUIThreading: Getting get_trunked_systems")
        return self.tb.get_trunked_systems()

        