from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import pmt
import time
from RPi import GPIO
from oled.serial import i2c
from oled.device import ssd1306, ssd1331, sh1106
from oled.render import canvas
from oled.virtual import viewport
from PIL import ImageFont, ImageDraw
from time import sleep
import socket
import threading
import os
import json
import serial

clk = 17
dt = 18
sw = 27
rf_control = 22
pathMenu = 1
counter = 0
power_gain = 0


GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(rf_control, GPIO.IN, pull_up_down=GPIO.PUD_UP)


port = serial.Serial("/dev/serial0", baudrate=115200, timeout=3.0)#thiet lap truyen UART0
serial = i2c(port=1, address=0x3C) #thiet lap dia chi man hinh
# device = sh1106(serial, rotate=0) #loai nan hinh
device = ssd1306(serial, rotate=0) #loai nan hinh
device.width=128
device.height=64

# raw_input("Enter anything")
# GPIO.cleanup()

class SignalGen(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Signalgen")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.freq = freq = 3e9
        self.gain = gain = 70
        self.pathfile = pathfile = 'data/1.KP1'

        ##################################################
        # Blocks
        ##################################################
        # Using uhd
        self.uhd_usrp_sink = uhd.usrp_sink(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink.set_clock_source('external', 0)
        self.uhd_usrp_sink.set_samp_rate(samp_rate)
        self.uhd_usrp_sink.set_center_freq(freq, 0)
        self.uhd_usrp_sink.set_gain(gain, 0)
        self.uhd_usrp_sink.set_antenna('TX/RX', 0)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, pathfile, True)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)

        # Using gr-osmosdr
        # self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + '' )
        # self.osmosdr_sink_0.set_sample_rate(samp_rate)
        # self.osmosdr_sink_0.set_center_freq(freq, 0)
        # self.osmosdr_sink_0.set_freq_corr(0, 0)
        # #USRP b210
        # self.osmosdr_sink_0.set_gain(73, 0)   #gain >74 sinh hai
        # self.osmosdr_sink_0.set_if_gain(0, 0)
        # self.osmosdr_sink_0.set_bb_gain(0, 0)
        # #Hackrf
        # # self.osmosdr_sink_0.set_gain(0, 0)
        # # self.osmosdr_sink_0.set_if_gain(0, 0)
        # # self.osmosdr_sink_0.set_bb_gain(47, 0)
        # self.osmosdr_sink_0.set_antenna('0', 0)
        # self.osmosdr_sink_0.set_bandwidth(1e6, 0)

        # self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        # self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, pathfile, True)
        # self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        # self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_char_to_float_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_char_to_float_0, 0))
        # Using uhd
        self.connect((self.blocks_float_to_complex_0, 0), (self.uhd_usrp_sink, 0))
        # Using gr-osmosdr
        # self.connect((self.blocks_float_to_complex_0, 0), (self.osmosdr_sink_0, 0))
        

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        # Using uhd
        self.uhd_usrp_sink.set_samp_rate(self.samp_rate)
        # Using gr-osmosdr
        #self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        # Using uhd
        self.uhd_usrp_sink.set_center_freq(self.freq, 0)
        # Using gr-osmosdr
        #self.osmosdr_sink_0.set_center_freq(self.freq, 0)
    
    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_sink.set_gain(self.gain, 0)
        
    
    def get_filesource(self):
        return self.pathfile
    
    def set_filesource(self, pathfile):
        self.pathfile = pathfile
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1,  self.pathfile, True)

#doc gia tri thiet lap lan truoc
#neu ko mo dc file thi thiet lap gia tri mac dinh
try:
    with open('conf.json', 'r') as f:
        dataConfig = json.load(f)
        print dataConfig
        frequency = dataConfig['freq']
        mode = str(dataConfig['mode'])
        power = dataConfig['power']
except ValueError:
    frequency = 3.9e9   
    mode = "data/1.KP1"
    power = 5
# print frequency
# print mode
# print power

#Gui den bo tao xung
def sendUART(modeFile):
    port.write('AA'.decode('hex'))
    port.write(open(modeFile,"rb").read())
    port.write('EE'.decode('hex'))

sendUART(mode)

#Cau hinh tan so
subMenuFreq = []
def loadfreq():
    global startFreq
    global stopFreq
    global stepFreq
    global subMenuFreq
    global frequency
    try:
        with open('freq.json', 'r') as f:
            dataFreq = json.load(f)
            startFreq = dataFreq['startfreq']
            stopFreq = dataFreq['stopfreq']
            stepFreq = dataFreq['stepfreq']
            print dataFreq
            elementFreq = (stopFreq - startFreq)/stepFreq
            subMenuFreq = [0 for i in range(int(elementFreq)+1)]
            for i in range(int(elementFreq)+1):
                subMenuFreq[i] = str((startFreq + i*stepFreq)/1e9) + 'Ghz'
    except ValueError:
        subMenuFreq = ['3.9Ghz', '4.0Ghz', '4.1Ghz', '4.2Ghz']
        startFreq = 3.9e9
        stopFreq = 4.2e9
        stepFreq = 1e8
loadfreq()

#Cau hinh cac che do
if ((frequency < startFreq) or (frequency > stopFreq)): 
    frequency = startFreq
print (frequency,startFreq,stepFreq)
print (subMenuFreq)
subMenuMode = sorted(os.listdir("data/")) #lay ten cac file che do

#Cau hinh cong suat
subMenuPower = [50,55,60,65,73]

#Cau hinh MainMenu
mainMenu = ['Frequency: ', 'Mode: ','Power: ']
mainMenuConfig = ['','','']
mainMenuConfig[0] = mainMenu[0] + subMenuFreq[int((frequency%startFreq)/stepFreq)] #hien thi
mainMenuConfig[1] = mainMenu[1] + mode[5:]
mainMenuConfig[2] = mainMenu[2] + str(power) #Hien thi cong suat theo muc
# mainMenuConfig[2] = mainMenu[2] + str(power*20) + 'W' # Hien thi cong suat theo W


def invert(draw,x,y,text):
    font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", 11, encoding="unic")
    # font = ImageFont.load_default()
    draw.rectangle((x, y, x+120, y+12), outline=255, fill=255)
    draw.text((x, y), text, font=font, outline=0,fill="black")
	
# Box and text rendered in portrait mode
def menu(device, draw, menustr,index):
    font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", 11, encoding="unic")
    # font = ImageFont.load_default()
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    indexPages = index/5
    pages = len(menustr)/5
    print index
    for page in range(pages+1):
        if (indexPages >= 1) and page <= indexPages - 1:
            continue
        if(page == indexPages):            
            for i in range(len(menustr)%5):
                j =  indexPages * 5 + i
                if( j == index):
                    invert(draw, 2, i*13, menustr[j])
                else:
                    draw.text((2, i*13), menustr[j], font=font, fill=255)
        else:
            # print ('indexPages',indexPages)
            for i in range(0,5):      
                j =  indexPages * 5 + i
                if( j == index):
                    invert(draw, 2, i*13, menustr[j])
                else:
                    draw.text((2, i*13), menustr[j], font=font, fill=255)

		

def display(pathMenu):
    if pathMenu == 1:
        with canvas(device) as draw:
            menu(device, draw, mainMenuConfig,counter%3)
            # font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
            draw.text((40, 45), "96L6E", font=font, fill=255)
            # draw.text((20, 52), "Generator", font=font, fill=255)
    elif pathMenu == 21:
        with canvas(device) as draw:
            menu(device, draw, subMenuFreq,counter%len(subMenuFreq))
    elif pathMenu == 22:
        with canvas(device) as draw:
            menu(device, draw, subMenuMode,counter%(len(subMenuMode)))
    elif pathMenu == 23:
        with canvas(device) as draw:
            menu(device, draw, map(str,range(1,6)),counter%5) #Hien thi muc cong suat 1-5
            # menu(device, draw, map(str,range(20,120,20)),counter%5) #Hien thi cong suat theo W

print subMenuPower[power-1]

def runSDR(power_gain):
    tb.stop()
    tb.wait()
    # tb.lock()
    tb.disconnect((tb.blocks_file_source_0, 0), (tb.blocks_char_to_float_0, 0))
    tb.set_freq(frequency)
    tb.set_filesource(mode)
    # tb.set_gain(subMenuPower[power-1])
    tb.set_gain(power_gain)
    print(tb.get_freq())
    print(tb.get_filesource())
    print(tb.get_gain())
    tb.connect((tb.blocks_file_source_0, 0), (tb.blocks_char_to_float_0, 0))
    # tb.unlock()
    tb.start()

def rfControl(channel):
    time.sleep(0.5)
    if GPIO.input(22) == 0:
        runSDR(subMenuPower[power-1])
    elif  GPIO.input(22) == 1:
        runSDR(0)

display(pathMenu)
tb = SignalGen()
rfControl(22)




def sw_callback(channel):  
    global pathMenu
    global counter
    global mainMenu
    global mainMenuConfig
    global subMenuMode
    global frequency
    global mode
    global startFreq
    global stopFreq
    global stepFreq
    global subMenuFreq
    global power
    global modeString
    
    if pathMenu == 1:
        if(counter%3 == 0):
            loadfreq() #cap nhat tan so
            print (frequency,startFreq,stepFreq)
            print (subMenuFreq)
            pathMenu = 21
        elif (counter%3 == 1):
            subMenuMode = sorted(os.listdir("data/")) #Cap nhat che do
            pathMenu = 22
        elif (counter%3 == 2):
            # subMenuMode = sorted(os.listdir("data/")) #Cap nhat che do
            pathMenu = 23
        counter = 0
        display(pathMenu)
        return # chua luu cau hinh
    elif pathMenu == 21:
        frequency = startFreq + stepFreq * (counter%len(subMenuFreq))
        mainMenuConfig[0] = ''
        mainMenuConfig[0] = mainMenu[0] + subMenuFreq[counter%len(subMenuFreq)]
        pathMenu = 1
        counter = 1
    elif pathMenu == 22:
        mode = ''
        mainMenuConfig[1] = ""
        mode = subMenuMode[counter%(len(subMenuMode))]
        mainMenuConfig[1] = mainMenu[1] + str(mode)
        mode = 'data/' + mode
        pathMenu = 1
        counter = 2
    elif pathMenu == 23:
        power = ''
        mainMenuConfig[2] = ""
        power = counter%5 + 1
        mainMenuConfig[2] = mainMenu[2] + str(power) #Hien thi cong suat theo muc
        # mainMenuConfig[2] = mainMenu[2] + str(power*20) + 'W' #Hien thi cong suat theo W
        pathMenu = 1
        counter = 0
        
    display(pathMenu)
    try:
        with open('conf.json', 'r') as f:
            dataConfig = json.load(f)
            dataConfig['freq'] = frequency
            dataConfig['mode'] = mode
            dataConfig['power'] = power
            print dataConfig
    except ValueError: 
            dataConfig ={'freq':'','mode':'','power':''}
            dataConfig['freq'] = frequency
            dataConfig['mode'] = mode
            dataConfig['power'] = power
    with open('conf.json', 'w') as f:
        json.dump(dataConfig, f, indent=4)
    sendUART(mode)
    rfControl(22)



def rotary_callback(channel):  
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
                # time.sleep(0.2)
                # print counter
                display(pathMenu)
        # clkLastState = clkState
    finally:
        print "Ending"


counter = 0
clkLastState = GPIO.input(clk)
GPIO.add_event_detect(clk, GPIO.FALLING , callback=rotary_callback,bouncetime=200)  
GPIO.add_event_detect(sw, GPIO.FALLING , callback=sw_callback, bouncetime=1000)
GPIO.add_event_detect(rf_control, GPIO.BOTH , callback=rfControl, bouncetime=300)

try:
    raw_input('Press Enter to quit: ')
except EOFError:
    pass
# tb.stop()
# tb.wait()



# def main(top_block_cls=SignalGen, options=None):

#     tb = top_block_cls()
#     tb.set_freq(frequency)
#     print(tb.get_freq())
#     tb.start()
#     try:
#         raw_input('Press Enter to quit: ')
#     except EOFError:
#         pass
#     tb.stop()
#     tb.wait()


# if __name__ == '__main__':
#     main()