#!/usr/bin/python
from Tkinter import *
import tkFont
import Queue
import sys
import threading
import traceback
from GUIThreading import GUIThreading


class du_queue_watcher(threading.Thread):

    def __init__(self, msgq, callback, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(1)
        self.msgq = msgq
        self.callback = callback
        self.keep_running = True
        self.start()

    def run(self):
        while (self.keep_running):
            msg = self.msgq.delete_head()
            self.callback(msg)

class GUIClient:
    root = Tk()

    tag = StringVar()
    talkgroup = StringVar()
    frequency = StringVar()
    options = Options()
    filterButtons = {}

    def __init__(self):
        self.recentlist = {}

        self.myFont = tkFont.Font(family='Helvetica', size=18, weight='bold')
        largeFont = tkFont.Font(family='Helvetica', size=48, weight='bold')

        self.root.title("OP25 GUI")
        self.root.geometry('800x480')

        self.tag.set("")
        self.talkgroup.set("")
        self.frequency.set("")

        # status bar
        status_frame = Frame(self.root)

        self.tagLabel = Label(status_frame, textvariable=self.tag, font=largeFont).pack(side=LEFT, fill=BOTH)
        # self.talkgroupLabel = Label(status_frame, textvariable=self.talkgroup, font = largeFont).pack(side=RIGHT)

        menu_left_frame = Frame(self.root, width=100)
        menu_center1_frame = Frame(self.root)
        menu_center2_frame = Frame(self.root)
        menu_right_frame = Frame(self.root)

        self.coloradoDTRSButton = Button(menu_center1_frame, text="Colorado DTRS", font=self.myFont,
                                         command=self.ColoradoDTRS)
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

        ##Button(menu_center1_frame, text = 'CSP', font = self.myFont, command = lambda: self.blacklistFilter('CSP')).pack(side=TOP, fill=BOTH)
        # Button(menu_center1_frame, text = 'CDOT', font = self.myFont, command = lambda: self.blacklistFilter('CDOT')).pack(side=TOP, fill=BOTH)
        # Button(menu_center1_frame, text = 'JFCO', font = self.myFont, command = lambda: self.blacklistFilter('JFCO')).pack(side=TOP, fill=BOTH)

        # frccButton = Button(self.menu_left, text = "FRCC", font = self.myFont, command = self.FRCC ).pack(side=TOP, fill=BOTH)
        # stopButton  = Button(self.menu_left_canvas, text = "Stop", font = self.myFont, command = self.stopProgram)#.pack(side=BOTTOM, fill=BOTH)

        # Button(menu_right_frame, text = "CPW", font = self.myFont, command = self.ColoradoDTRSCPW).pack(side=TOP, fill=BOTH)
        # Button(menu_right_frame, text = "Parks", font = self.myFont, command = self.ColoradoDTRSOPN).pack(side=TOP, fill=BOTH)
        # Button(menu_right_frame, text = "SAR", font = self.myFont, command = self.ColoradoDTRSSAR).pack(side=TOP, fill=BOTH)
        # Button(menu_right_frame, text = "Boulder", font = self.myFont, command = self.ColoradoDTRSBouldrCo).pack(side=TOP, fill=BOTH)

        exitButton = Button(menu_left_frame, text="Exit", bg='red', font=self.myFont, width=20,
                            command=self.exitProgram).pack(side=BOTTOM, fill=BOTH)

        self.menu_left_frame_canvas = self.createCanvas(menu_left_frame)
        # self.menu_center2_canvas = self.createCanvas(menu_center2_frame)

        status_frame.grid(row=0, column=1, columnspan=3, sticky="new")
        menu_left_frame.grid(row=0, rowspan=2, column=0, sticky="nsew")
        menu_center1_frame.grid(row=1, column=1, sticky="nsew")
        menu_center2_frame.grid(row=1, column=2, sticky="nsew")
        menu_right_frame.grid(row=1, column=3, sticky="nsew")

        self.root.grid_rowconfigure(1, weight=1)
        # self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=0)

        self.options.frequency = 853850000.0
        self.options.trunk_conf_file = 'ColoradoDTRSTrunk.tsv'
        self.guiThreading = GUIThreading(self.options, self.setTags)
        # self.blacklistFilter('RTD')

    def addButton(self, frame, tag, filterValues):

        button = Button(frame, text=tag, font=self.myFont, bg='green', activebackground='green',
                        command=lambda: self.blacklistFilterList(tag))
        button.pack(side=TOP, fill=BOTH)
        self.filterButtons[tag] = {'button': button, 'filterValues': filterValues, 'enabled': False}

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

    def ColoradoDTRSRTD(self):
        self.blacklistFilter('RTD')

    def ColoradoDTRSCSP(self):
        self.blacklistFilter('CSP')

    def ColoradoDTRSSAR(self):
        self.blacklistFilter('MtnTac', False)
        self.blacklistFilter('RckyMtnRscue', False)
        self.blacklistFilter('MAC', False)
        self.blacklistFilter('Rescue', False)

    def ColoradoDTRSCPW(self):
        self.blacklistFilter('DOW', False)

    def ColoradoDTRSOPN(self):
        self.blacklistFilter('OPS', False)
        self.blacklistFilter('Opn', False)

    def ColoradoDTRSCDOT(self):
        self.blacklistFilter('CDOT')

    def ColoradoDTRSJFCO(self):
        self.blacklistFilter('JFCO')

    def ColoradoDTRSBouldrCo(self):
        self.blacklistFilter('BouldrCo')
        self.blacklistFilter('Boulder PD')

    def getFrame(self, canvas):
        for child in canvas.children.values():
            if isinstance(child, Frame):
                return child

    def getScrollbar(self, canvas):
        for child in canvas.children.values():
            if isinstance(child, Scrollbar):
                return child

    def createCanvas(self, parent):
        vscrollbar = Scrollbar(parent)
        canvas = Canvas(parent, yscrollcommand=vscrollbar.set)
        canvas.configure(width=parent.winfo_width(), height=parent.winfo_height())

        vscrollbar.config(command=canvas.yview)
        vscrollbar.pack(side=RIGHT, fill=Y)

        frame = Frame(canvas)
        frame.configure(width=canvas.winfo_width())
        # Label(frame, text = 'Foooooooooooobar', font = self.myFont, bg='red').pack(side=TOP, fill=X)

        canvas.pack(side="right", fill=BOTH, expand=True)
        canvas.create_window(0, 0, window=frame, anchor='nw')
        parent.update()

        canvas.config(scrollregion=canvas.bbox("all"))
        return canvas

    def setTags(self, msg):
        if msg['tag']:
            tag = msg['tag']
            tgid = msg['tgid']
            self.tag.set("%s" % tag)

        if tgid in self.recentlist.keys():
            pass
        else:
            # print 'tag: %s (%d)' % (tag, tgid)
            frame = self.getFrame(self.menu_left_frame_canvas)
            scrollbar = self.getScrollbar(self.menu_left_frame_canvas)
            if (scrollbar != None):
                scrollbar.set(last)
            # button = Button(frame, text = '{:s} - {:d}'.format(tag, tgid), font = self.myFont, command = lambda: self.blacklist(tgid))
            button = Button(frame, text='{:s}'.format(tag), font=self.myFont, width=20,
                            command=lambda: self.blacklist(tgid))
            button.pack(side=TOP, fill=BOTH)
            self.recentlist[tgid] = [button, True]
            self.menu_left_frame_canvas.update()
            self.menu_left_frame_canvas.config(scrollregion=self.menu_left_frame_canvas.bbox("all"))

        if msg['tgid']:
            self.talkgroup.set("%s" % msg['tgid'])
        if msg['freq']:
            self.frequency.set("%f" % (msg['freq'] / 1000000.0))

        # print self.recentlist

    def FRCC(self):
        self.options.frequency = 772993750.0
        self.options.trunk_conf_file = 'trunkFRCC.tsv'
        self.guiThreading = GUIThreading(self.options, self.setTags)

    def blacklistFilterList(self, tag, on=True):
        print('filterlisting %s -  %s' % (tag, self.filterButtons[tag]['enabled']))

        self.tgid_map = self.guiThreading.get_tgid_map()

        for filter in self.filterButtons[tag]['filterValues']:
            filtered_dict = {v[0]: k for k, v in self.tgid_map.items() if filter in v[0]}

            for key in filtered_dict.keys():
                if self.filterButtons[tag]['enabled']:
                    print('Whitelisting - %s - %s' % (key, filtered_dict[key]))
                    self.guiThreading.remove_blacklist(filtered_dict[key])
                else:
                    print('Blacklisting - %s - %s' % (key, filtered_dict[key]))
                    self.guiThreading.add_blacklist(filtered_dict[key])

        if self.filterButtons[tag]['enabled']:
            self.filterButtons[tag]['button']['bg'] = 'green'
            self.filterButtons[tag]['button']['activebackground'] = 'green'
            self.filterButtons[tag]['enabled'] = False
        else:
            self.filterButtons[tag]['button']['bg'] = 'red'
            self.filterButtons[tag]['button']['activebackground'] = 'red'
            self.filterButtons[tag]['enabled'] = True

    def blacklistFilter(self, filter, on=True):
        self.tgid_map = self.guiThreading.get_tgid_map()
        filtered_dict = {v[0]: k for k, v in self.tgid_map.items() if filter in v[0]}

        for key in filtered_dict.keys():
            if (on):
                print('Blacklisting - %s - %s' % (key, filtered_dict[key]))
                self.guiThreading.add_blacklist(filtered_dict[key])
            else:
                print('Whitelisting - %s - %s' % (key, filtered_dict[key]))
                self.guiThreading.remove_blacklist(filtered_dict[key])

    def blacklistDictionary(self, dictionary, on=True):
        for key in dictionary.keys():
            print('Blacklisting - %s - %s' % (key, dictionary[key]))
            if (on):
                print('Blacklisting - %s - %s' % (key, dictionary[key]))
                self.guiThreading.add_blacklist(dictionary[key])
            else:
                print('Whitelisting - %s - %s' % (key, dictionary[key]))
                self.guiThreading.remove_blacklist(dictionary[key])

    def process_qmsg(self, msg):
        print(msg)

    def exitProgram(self):
        try:
            print('Exiting Program')
            stopProgram()
            print('Exited Program')
        except:
            pass
        self.root.quit()

    def stopProgram(self):
        self.guiThreading.keep_running = False

    def run(self):
        mainloop()

    def process_queue(self):
        try:
            msg = self.queue.get(0)
            example.set("process_queue")

        except Queue.Empty:
            self.master.after(100, self.process_queue)

    def cli_options(self):
        # command line argument parsing
        parser = OptionParser(option_class=eng_option)
        parser.add_option("--args", type="string", default="", help="device args")
        parser.add_option("--antenna", type="string", default="", help="select antenna")
        parser.add_option("-a", "--audio", action="store_true", default=False, help="use direct audio input")
        parser.add_option("-A", "--audio-if", action="store_true", default=False,
                          help="soundcard IF mode (use --calibration to set IF freq)")
        parser.add_option("-I", "--audio-input", type="string", default="",
                          help="pcm input device name.  E.g., hw:0,0 or /dev/dsp")
        parser.add_option("-i", "--input", default=None, help="input file name")
        parser.add_option("-b", "--excess-bw", type="eng_float", default=0.2, help="for RRC filter", metavar="Hz")
        parser.add_option("-c", "--calibration", type="eng_float", default=0.0,
                          help="USRP offset or audio IF frequency", metavar="Hz")
        parser.add_option("-C", "--costas-alpha", type="eng_float", default=0.04, help="value of alpha for Costas loop",
                          metavar="Hz")
        parser.add_option("-D", "--demod-type", type="choice", default="cqpsk", choices=('cqpsk', 'fsk4'),
                          help="cqpsk | fsk4")
        parser.add_option("-P", "--plot-mode", type="choice", default=None,
                          choices=(None, 'constellation', 'fft', 'symbol', 'datascope', 'mixer'),
                          help="constellation | fft | symbol | datascope | mixer")
        parser.add_option("-f", "--frequency", type="eng_float", default=0.0, help="USRP center frequency",
                          metavar="Hz")
        parser.add_option("-F", "--ifile", type="string", default=None, help="read input from complex capture file")
        parser.add_option("-H", "--hamlib-model", type="int", default=None, help="specify model for hamlib")
        parser.add_option("-s", "--seek", type="int", default=0, help="ifile seek in K, symbols file seek in seconds")
        parser.add_option("-l", "--terminal-type", type="string", default='curses',
                          help="'curses' or udp port or 'http:host:port'")
        parser.add_option("-L", "--logfile-workers", type="int", default=None,
                          help="number of demodulators to instantiate")
        parser.add_option("-M", "--metacfg", type="string", default=None, help="Icecast Metadata Config File")
        parser.add_option("-S", "--sample-rate", type="int", default=960000, help="source samp rate")
        parser.add_option("-t", "--tone-detect", action="store_true", default=False,
                          help="use experimental tone detect algorithm")
        parser.add_option("-T", "--trunk-conf-file", type="string", default=None, help="trunking config file name")
        parser.add_option("-v", "--verbosity", type="int", default=0, help="message debug level")
        parser.add_option("-V", "--vocoder", action="store_true", default=False, help="voice codec")
        parser.add_option("-n", "--nocrypt", action="store_true", default=False, help="silence encrypted traffic")
        parser.add_option("-o", "--offset", type="eng_float", default=0.0,
                          help="tuning offset frequency [to circumvent DC offset]", metavar="Hz")
        parser.add_option("-p", "--pause", action="store_true", default=False, help="block on startup")
        parser.add_option("-w", "--wireshark", action="store_true", default=False, help="output data to Wireshark")
        parser.add_option("-W", "--wireshark-host", type="string", default="127.0.0.1", help="Wireshark host")
        parser.add_option("-u", "--wireshark-port", type="int", default=23456, help="Wireshark udp port")
        parser.add_option("-r", "--raw-symbols", type="string", default=None, help="dump decoded symbols to file")
        parser.add_option("--symbols", type="string", default="", help="playback symbols file (captured using -r)")
        parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=(0, 0),
                          help="select USRP Rx side A or B (default=A)")
        parser.add_option("-g", "--gain", type="eng_float", default=None,
                          help="set USRP gain in dB (default is midpoint) or set audio gain")
        parser.add_option("--gain-mode", type="int", help="Control SDR AGC with set_gain_mode()")
        parser.add_option("-G", "--gain-mu", type="eng_float", default=0.025, help="gardner gain")
        parser.add_option("-N", "--gains", type="string", default=None, help="gain settings")
        parser.add_option("-O", "--audio-output", type="string", default="default", help="audio output device name")
        parser.add_option("-x", "--audio-gain", type="eng_float", default="1.0", help="audio gain (default = 1.0)")
        parser.add_option("-U", "--udp-player", action="store_true", default=False,
                          help="enable built-in udp audio player")
        parser.add_option("-q", "--freq-corr", type="eng_float", default=0.0, help="frequency correction")
        parser.add_option("-d", "--fine-tune", type="eng_float", default=0.0, help="fine tuning")
        parser.add_option("-2", "--phase2-tdma", action="store_true", default=False, help="enable phase2 tdma decode")
        parser.add_option("-Z", "--decim-amt", type="int", default=1, help="spectrum decimation")
        (options, args) = parser.parse_args()
        if len(args) != 0:
            parser.print_help()
            sys.exit(1)
        self.options = options

    def blacklist(self, tgid):
        if self.recentlist[tgid][1]:
            # print self.recentlist[tgid]
            # print self.recentlist[tgid][0]["bg"]
            self.recentlist[tgid][1] = False
            self.recentlist[tgid][0]["bg"] = "red"
            self.recentlist[tgid][0]['activebackground'] = 'red'
            self.guiThreading.add_blacklist(tgid)

        else:
            self.recentlist[tgid][0]["bg"] = '#d9d9d9'
            self.recentlist[tgid][0]['activebackground'] = '#d9d9d9'
            self.recentlist[tgid][1] = True
            self.guiThreading.remove_blacklist(tgid)

    def refreshTopTen(self):
        self.menu_center2.delete("all")


if __name__ == '__main__':
    try:
        guiClient = GUIClient()
        guiClient.run()
    except:
        sys.stderr.write('guiClient: exception occurred\n')
        sys.stderr.write('guiClient: exception:\n%s\n' % traceback.format_exc())
