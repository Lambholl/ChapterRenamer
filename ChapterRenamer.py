import os, re

class Chapter(object):
    
    def __init__(self, text, OP_range=[87,93], ED_range=[87,93]):
        if not isinstance(text, str):
            raise TypeError('Input must be a str containing Chapter Infos.')
        elif not isinstance(OP_range, (list, tuple)):
            raise TypeError('OP_range must be a list or a tuple.')
        elif not isinstance(ED_range, (list, tuple)):
            raise TypeError('ED_range must be a list or a tuple.')
        elif OP_range[0] > OP_range[1] or ED_range[0] > ED_range[1]:
            raise TypeError('The first number should not be greater than the second.')
        p1 = 'CHAPTER([0-9]+)=([0-9]+):([0-9]+):([0-9]+)\\.([0-9]+)'
        p2 = 'CHAPTER([0-9]+)NAME=(.+)'
        times = re.findall(p1, text)
        for i in range(len(times)):
            times[i] = list(map(int, list(times[i])))
        self.times = times
        chapterNames = []
        for i in re.findall(p2, text):
            chapterNames.append(i[1])
        self.chapterNames = chapterNames
        self.OP, self.ED = None, None
        self.OP_range, self.ED_range = OP_range, ED_range
    
    def seekForOP(self):
        for i in range(len(self.times)):
            if self.times[i][2] > 8: break
            elif self.OP_range[0] <= self.times[i+1][2]*60+self.times[i+1][3]-self.times[i][2]*60-self.times[i][3] <= self.OP_range[1]:
                self.OP = i; break
    
    def seekForED(self):
        for i in range(len(self.times)-1, -1, -1):
            if self.times[i][2] < 17: break
            elif self.ED_range[0] <= self.times[i][2]*60+self.times[i][3]-self.times[i-1][2]*60-self.times[i-1][3] <= self.ED_range[1]:
                self.ED = i-1; break
        
    def rename(self):
        self.seekForOP(); self.seekForED()
        if self.OP:
            self.chapterNames[self.OP] = 'OP'
            if self.OP == 1:
                self.chapterNames[0] = 'Avant'
            if self.ED:
                self.chapterNames[self.ED] = 'ED'
                for i in range(self.ED-self.OP - 1):
                    self.chapterNames[i + self.OP + 1] = 'Part ' + chr(65+i)
                if len(self.chapterNames) > self.ED + 1:
                    self.chapterNames[-1] = 'Preview'
                    if len(self.chapterNames) > self.ED + 2:
                        self.chapterNames[-2] = 'Part ' + chr(64+self.ED-self.OP)
            else:
                self.chapterNames[-1] = 'Preview'
                for i in range(len(self.chapterNames)-self.OP-2):
                    self.chapterNames[i+self.OP+1] = 'Part ' + chr(65+i)
        else:
            if self.ED:
                self.chapterNames[self.ED] = 'ED'
                if self.ED == 2:
                    noAvant = True
                    self.chapterNames[0], self.chapterNames[1] = 'Part A', 'Part B'
                else:
                    noAvant = False
                    self.chapterNames[0] = 'Avant'
                    for i in range(self.ED-1):
                        self.chapterNames[i+1] = 'Part ' + chr(65 + i)
                if len(self.chapterNames) > self.ED + 1:
                    self.chapterNames[-1] = 'Preview'
                    if len(self.chapterNames) > self.ED + 2:
                        self.chapterNames[-2] = 'Part ' + chr(65 + self.ED - int(not noAvant))
            else:
                if len(self.chapterNames) == 2:
                    self.chapterNames = ['Part A', 'Part B']
                elif len(self.chapterNames) == 3:
                    self.chapterNames = ['Part A', 'Part B', 'Preview']
                else:
                    self.chapterNames[0] = 'Avant'
                    self.chapterNames[-1] = 'Preview'
                    for i in range(len(self.chapterNames)-2):
                        self.chapterNames[i+1] = 'Part ' + chr(65 + i)
        result = ''
        for i in range(len(self.chapterNames)):
            result += 'CHAPTER{0:0>2}={1:0>2}:{2:0>2}:{3:0>2}.{4:0>3}\n'.format(i+1, self.times[i][1], self.times[i][2], self.times[i][3], self.times[i][4])
            result += 'CHAPTER{0:0>2}NAME={1}\n'.format(i+1, self.chapterNames[i])
        self.produced = result

def guiProceed():
    chapterFiles_original = filedialog.askopenfilenames(title='选择章节文件', initialdir=__file__, filetypes=[('章节文件', '.txt')])
    for i in chapterFiles_original:
        try:
            with open(i, 'r', encoding='utf-8') as fb:
                textOriginal = fb.read()
            chaps = Chapter(textOriginal)
            chaps.rename()
            with open(i, 'w', encoding='utf-8') as fb:
                fb.write(chaps.produced)
            if messagebox.askyesno('处理成功', '处理后的文件已覆盖原文件\n是否继续处理别的文件？'):
                guiProceed()
            else:
                os._exit(1)
        except Exception as e:
            messagebox.showerror('错误', str(e))
            guiProceed()

if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
    guiProceed()

# LPSub Chapters Proceeder
# Written by Lambholl on 26 Dec., 2022
