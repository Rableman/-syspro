import numpy as np
import math
import rec_sound

def readfunc(filename):
  f = open(filename, "r")
  data = f.readlines()
  func1 = data[0].split(",")
  func2 = data[1].split(",")
  func1[0] = int(func1[0])
  func2[0] = int(func2[0]) 
  for i in range(1,3):
    func1[i] = float(func1[i])
    func2[i] = float(func2[i])
  f.close()
  return func1, func2

class Calcdist: 

    def __init__(self):

        self.rec = rec_sound.Record()
        A, B = readfunc("func.txt")
        #音源周波数        
        #第１音源
        self.freqA = A[0]
        self.sourceA = [0, 5]
        self.funcA = list(A[1],A[2])
        #第２音源
        self.freqB = B[0]
        self.sourceB = [5, 5]
        self.funcB = list(B[1],B[2])
        #位置座標情報
        self.grid = self.init_grid()
    
    def get_dist(self, debug =True):
        sec = 2 #録音時間
        dist=[]
        source=["A","B"]
        dist.append = self.calc_dist(self.rec.record(self.freqA,sec), self.freqA)
        dist.append = self.calc_dist(self.rec.record(self.freqB,sec), self.freqB)
        if debug == True: 
            for i in range(2):
                print("Dist_%s: %d[cm]" % source[i], dist[i])
        return dist

    #音の振幅を元に距離を計算 
    def calc_dist(self, amp, freq):

        if freq == self.freqA:
            ret = self.funcA[0] * math.log(amp) + self.funcA[1]
        elif freq == self.freqB:
            ret = self.funcB[0] * math.log(amp) + self.funcB[1]

        return ret
    
    #座標初期化
    def init_grid(self):
        grid_num = 5
        grid = [[0 for i in range(grid_num)] for i in range(grid_num)]
        return grid

    #座標表示
    def show_grid(self):
        self.set_grid(0,0)
        for x in range(5):
            print(self.grid[x])

    #座標提供
    def get_coord(self):
        dist = self.get_dist()        
        x, y = self.calc_coord(dist[0], self.cos_rule(dist[0], dist[1], self.sourceB[0] - self.sourceA[0]))
        #debug
        #self.grid[x][y] = 1
        #self.show_grid()
        return x, y

    #座標算出
    def calc_coord(self, dist, ang):
        u = dist * math.cos(ang)
        v = dist * math.sin(ang)
        x = self.sourceA[0] + round(u)
        y = self.sourceA[1] - round(v)
        return x, y

    #余弦定理
    def cos_rule(self, a, b, c):
        ret = (a**2 + c**2 - b**2)/(2 * a * c)
        ret = math.acos(ret)
        return ret