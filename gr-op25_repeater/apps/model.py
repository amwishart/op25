import sys
import threading
import time
import traceback
import rx

class Options:
    def __init__(self):
        #self.sample_rate = 2400000
        self.sample_rate = 960000
        self.audio_gain = 1.0
        #self.audio_output = 'bluealsa:DEV=00:1D:43:BA:A8:34'
        # self.audio_output = 'bluealsa:DEV=00:1E:AE:2F:B3:F5'
        self.audio_output = 'hw:0,0'
        self.offset = 25000.0
        self.excess_bw = 0.2
        self.symbols = ''
        self.frequency = 853850000.0
        self.audio_input = ''
        self.wireshark_host = '127.0.0.1'
        self.metacfg = None
        self.ifile = None
        self.pause = False
        self.gain_mode = None
        self.costas_alpha = 0.04
        self.calibration = 0.0
        self.seek = 0
        self.wireshark_port = 23456
        self.nocrypt = True
        self.phase2_tdma = True
        self.input = None
        self.audio_if = False
        self.rx_subdev_spec = (0, 0)
        self.wireshark = False
        self.gains = 'LNA:47'
        self.gain_mu = 0.025
        self.args = 'rtl'
        self.demod_type = 'cqpsk'
        self.freq_corr = -1.0
        self.raw_symbols = None
        self.gain = None
        self.trunk_conf_file = 'ColoradoDTRSTrunk.tsv'
        self.decim_amt = 1
        self.terminal_type = '56111'
        self.tone_detect = False
        self.plot_mode = None
        self.verbosity = 0
        self.hamlib_model = None
        self.vocoder = True
        self.sample_rate = 2400000
        self.logfile_workers = None
        self.fine_tune = 0.0
        self.udp_player = True
        self.audio = False
        self.antenna = ''

class gui_du_queue_watcher(threading.Thread):
    def __init__(self, msgq, callback, **kwds):
        print("init gui_du_queue")
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(1)
        self.msgq = msgq
        self.callback = callback
        self.keep_running = True
        self.start()

    def run(self):
        while (self.keep_running):
            msg = self.msgq.delete_head()
            # print ("*** self.msgq.delete_head %s" % msg)
            self.callback(msg)


class SystemModel(object):
    def __init__(self, width, height, config):
        print("*** Create main SystemModel model. ***")
        # Set properties that will be used by views.
        self.width = width
        self.height = height
        self.config = config

    def system_name(self):
        return self.config['sysname']

    def get_tgids(self):
        return self.config['tgid_map']


    def get_config(self):
        print ("SystemModel: Getting get_config")
        return self.config

class OP25Model(object):
    def __init__(self, width, height, callback=None):
        # print("""**** Create main FreqShow application model.  Must provide the width and height of the screen in pixels.""")
        # Set properties that will be used by views.
        self.width = width
        self.height = height
        self.options = Options()
        # options.frequency = 853.850e6
        # options.trunk_conf_file = 'ColoradoDTRSTrunk.tsv'
        self.options.frequency = 772.99375e6
        self.options.frequency = 853.850e6
        self.options.trunk_conf_file = 'tsv/Colorado.tsv'

        # self.guiThreading = GUIThreading(self.options, self.setTags)

        self.keep_running = True
        self.callback = callback
        self.tb = rx.p25_rx_block(self.options, self.callback)
        self.tb.setCallback(self.callback)
        self.q_watcher = gui_du_queue_watcher(self.tb.output_q, self.process_qmsg)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        print('Running OP25Model  Thread')
        try:
            self.tb.start()
            #self.tb.get_nac()

            if self.options.symbols:
                self.tb.wait()
            else:
                while self.keep_running:
                    time.sleep(1)
                    #print ('checking call back %s == %s ' % (self.callback, self.tb.callback))
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
        # print ("*** process_qmsg %s\r\n" % msg)
        if self.tb.process_qmsg(msg):
            # self.tb.stop()
            self.keep_running = False

    def add_blacklist(self, current_tgid):
        # print 'GUIThreading add_blacklist %s ' % current_tgid
        self.tb.add_blacklist(current_tgid)

    def remove_blacklist(self, current_tgid):
        print ('GUIThreading remove_blacklist %s ' % current_tgid)
        self.tb.remove_blacklist(current_tgid)

    def get_tgid_map(self, nac):
        print ("GUIThreading: Getting tgid_map")
        return self.tb.get_tgid_map(nac)

    def get_nac(self):
        # print ("GUIThreading: Getting get_nac")
        return self.tb.get_nac()

    def get_configs(self):
        print ("OP25Model: Getting get_configs")
        configs = self.tb.get_configs()
        return configs

    def get_config(self, nac):
        print('OP25Model: Getting get_config: {}'.format(nac))
        #print(self.tb.get_configs()[nac])
        return self.tb.get_configs()[nac]

    def getTag(self, tgid):
        print('getting tag in OP25Model')
        tgidMap = self.guiThreading.get_tgid_map()
        # tgidMap = {v[0]: k for k, v in self.guiThreading.get_tgid_map() }

        print('Key: {}'.format(tgid))

        if (tgidMap.has_key(tgid)):
            print(tgidMap[tgid])
            return tgidMap[tgid][0]
        return None

    def blacklist(self, system, tgid):
        print('OP25Model - blacklist - {}:{}'.format(system, tgid))
        self.add_blacklist(tgid)

    def setCallback(self, callback):
        print('setting callback in OP25Model to %s' % callback)
        if (self.tb != None):
            print ('setting callback in OP25Model')
            self.tb.setCallback(callback)
        else:
            print ('cant set callback in OP25Model yet.  set in local and then it will get set on start')
            self.callback = callback

    def setRender(self, callback=None):
        print('setting renderer in OP25Model')

    def callRender(self, callback=None):
        # print('calling renderer in OP25Model')
        pass

    def get_system_name(self):
        return self.options.trunk_conf_file

    def get_freq(self):
        return self.options.frequency

    def set_freq(self, freq_mhz):
        self.options.frequency = freq_mhz
