Huong dan
0. Cai cac thu vien phu thuoc
+ sudo apt-get update\
Neu loi thì chay:\
sudo apt-get update --allow-releaseinfo-change
+ gnuradio
+ vsftp tai https://docs.google.com/document/d/1I5rZl4iO-pzb8lEGtGxOEf01My18t763Lo7kyMiaRro/edit
+ thiet lap I2C, SSH, Serial
+ sudo pip install setuptools==44.1.1
2. Cai thu vien cho oled sh1106 1.3"
+ git clone https://github.com/rm-hull/luma.oled
+ cd luma.oled
+ git checkout 1.5.0 #su dung voi python 2
+ sudo python setup.py install

2. Chay chuong trinh
+ python signalgen.py

3. Tao khoi dong cung Raspi
+ nano .bashrc

Add end file
+ cd fakeradar
+ python signalgen.py

