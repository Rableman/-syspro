#Taken from http://takeshid.hatenadiary.jp/entry/2015/11/27/045123
#プロット関係のライブラリ
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from scipy import signal
import sys

#音声関係のライブラリ
import pyaudio
import struct


def filt(data, s_freq, fp, fs, gp, gs, ftype):
    nyq = s_freq / 2                           #ナイキスト周波数
    if type(fp) == "list":
        Wp = [x/nyq for x in fp]
        Ws = [x/nyq for x in fs]
    else:  
        Wp = fp/nyq
        Ws = fs/nyq
    N, Wn = signal.buttord(Wp, Ws, gp, gs)
    b, a = signal.butter(N, Wn, ftype)
    data = signal.filtfilt(b, a, data)
    return data

class PlotWindow:
    def __init__(self):
        #マイクインプット設定
        self.CHUNK=512           #1度に読み取る音声のデータ幅
        self.RATE=44100             #サンプリング周波数
        self.update_seconds=1      #更新時間[ms]
        self.audio=pyaudio.PyAudio()
        self.stream=self.audio.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=self.RATE,
                                    input=True,
                                    frames_per_buffer=self.CHUNK)

        #音声データの格納場所(プロットデータ)
        self.data=np.zeros(self.CHUNK)
        self.axis=np.fft.fftfreq(len(self.data), d=1.0/self.RATE)

        #プロット初期設定
        self.win=pg.GraphicsWindow()
        self.win.setWindowTitle("SpectrumAnalyzer")
        self.plt=self.win.addPlot() #プロットのビジュアル関係
        self.plt.setYRange(0,20)    #y軸の制限

        #アップデート時間設定
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.update_seconds)

    def update(self):
        self.data=np.append(self.data,self.AudioInput())
        if len(self.data)/self.CHUNK > 10:
            self.data=self.data[self.CHUNK:]
        self.fft_data=self.FFT_AMP(self.data)
        self.axis=np.fft.fftfreq(len(self.data), d=1.0/self.RATE)
        for i in range (len(self.fft_data)):
            if self.axis[i] < 7000:
                self.fft_data[i] = 0
        self.plt.plot(x=self.axis, y=self.fft_data, clear=True, pen="y")  #symbol="o", symbolPen="y", symbolBrush="b")

    def AudioInput(self):
        ret=self.stream.read(self.CHUNK, exception_on_overflow = False)    #音声の読み取り(バイナリ) CHUNKが大きいとここで時間かかる
        #バイナリ → 数値(int16)に変換
        #32768.0=2^16で割ってるのは正規化(絶対値を1以下にすること)
        ret=np.frombuffer(ret, dtype="int16")/32768.0
        #ret=filt(ret, self.RATE, 18000, 19000, 3, 40, "low")
        return ret

    def FFT_AMP(self, data):
        data=np.hamming(len(data))*data
        data=np.fft.fft(data)
        #data=np.real(data)
        data=np.abs(data)
        return data

if __name__=="__main__":
    plotwin=PlotWindow()
    if (sys.flags.interactive!=1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()