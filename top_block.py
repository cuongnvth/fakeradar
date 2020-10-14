#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# GNU Radio version: 3.7.14.0
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import pmt
import time

from RPi import GPIO
from time import sleep


clk = 17
dt = 18
freq = 4e9
samp_rate = 1e6

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clkLastState = GPIO.input(clk)

def my_callback(channel):  
    global clkLastState
    global counter
    try:
                clkState = GPIO.input(clk)
                if clkState != clkLastState:
                        dtState = GPIO.input(dt)
                        if dtState != clkState:
                                counter += 1
                        else:
                                counter -= 1
						    #print counter
                clkLastState = clkState
                #sleep(0.01)
    finally:
               #print Ending


counter = 0
clkLastState = GPIO.input(clk)
GPIO.add_event_detect(17, GPIO.FALLING  , callback=my_callback, bouncetime=300)  
raw_input("Enter anything")
GPIO.cleanup()



class top_block(gr.top_block):

    def __init__(self,options):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        # self.samp_rate = samp_rate = 3.9e9
        samp_rate = 1e6

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + '000000000000000057b068dc2337c063' )
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(options.frequency, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(0, 0)
        self.osmosdr_sink_0.set_if_gain(0, 0)
        self.osmosdr_sink_0.set_bb_gain(47, 0)
        self.osmosdr_sink_0.set_antenna('0', 0)
        self.osmosdr_sink_0.set_bandwidth(1e6, 0)

        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, options.filename, True)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_char_to_float_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.osmosdr_sink_0, 0))

    # def get_samp_rate(self):
    #     return self.samp_rate

    # def set_samp_rate(self, samp_rate):
    #     self.samp_rate = samp_rate
    #     self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

def get_options():
    parser = OptionParser(option_class=eng_option)
    parser.add_option("-f", "--frequency", type="eng_float", default=4000000000,
                      help="set transmit frequency [default=4000000000]")
    parser.add_option("-t", "--filename", type="string", default="data.bin",
                      help="set output file name [default=data.bin]")
    
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.print_help()
        raise SystemExit, 1

    return (options)

if __name__ == '__main__':
    (options) = get_options()
    tb = top_block(options)
    tb.start()
    raw_input('Press Enter to quit: ')
    tb.stop()
    tb.wait()
