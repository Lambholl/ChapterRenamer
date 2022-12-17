import os, re

class Chapter(object):
    
    def __init__(self, text, OP_range=[87,93], ED_range=[87,93], OP_at_end=False):
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
        self.__OP, self.__ED = None, None
        self.__OP_range, self.__ED_range = OP_range, ED_range
        self.__OP_at_end = OP_at_end
    
    def seekForOP(self):
        if self.__OP_at_end:
            for i in range(len(self.times)-1, -1, -1):
                if self.times[i][2] < 17: break
                elif self.__OP_range[0] <= self.times[i][2]*60+self.times[i][3]-self.times[i-1][2]*60-self.times[i-1][3] <= self.__OP_range[1]:
                    self.__OP = i; break
        else:
            for i in range(len(self.times)):
                if self.times[i][2] > 8: break
                elif self.__OP_range[0] <= self.times[i+1][2]*60+self.times[i+1][3]-self.times[i][2]*60-self.times[i][3] <= self.__OP_range[1]:
                    self.__OP = i; break

    
    def seekForED(self):
        for i in range(len(self.times)-1, -1, -1):
            if self.times[i][2] < 17: break
            elif self.__ED_range[0] <= self.times[i][2]*60+self.times[i][3]-self.times[i-1][2]*60-self.times[i-1][3] <= self.__ED_range[1]:
                self.__ED = i-1; break
        
    def rename(self):
        if self.__OP_at_end:
            self.seekForOP()
        else:
            self.seekForOP(); self.seekForED()
        if self.__OP:
            self.chapterNames[self.__OP] = 'OP'
            if not self.__OP_at_end:
                if self.__OP == 1:
                    self.chapterNames[0] = 'Avant'
            else:
                if self.__OP >= 2:
                    self.chapterNames[0] = 'Avant'
            if self.__ED:
                self.chapterNames[self.__ED] = 'ED'
                for i in range(self.__ED-self.__OP - 1):
                    self.chapterNames[i + self.__OP + 1] = 'Part ' + chr(65+i)
                if len(self.chapterNames) > self.__ED + 1:
                    self.chapterNames[-1] = 'Preview'
                    if len(self.chapterNames) > self.__ED + 2:
                        self.chapterNames[-2] = 'Part ' + chr(64+self.__ED-self.__OP)
            else:
                if not self.__OP_at_end:
                    self.chapterNames[-1] = 'Preview'
                    for i in range(len(self.chapterNames)-self.__OP-2):
                        self.chapterNames[i+self.__OP+1] = 'Part ' + chr(65+i)
                else:
                    if len(self.chapterNames) > self.__OP + 1:
                        self.chapterNames[-1] = 'Preview'
                    if self.__OP >= 2:
                        for i in range(self.__OP -1):
                            self.chapterNames[i+1] = 'Part ' + chr(65+i)
                    else:
                        for i in range(self.__OP):
                            self.chapterNames[i] = 'Part ' + chr(65+i)
        else:
            if self.__ED:
                self.chapterNames[self.__ED] = 'ED'
                if self.__ED == 2:
                    noAvant = True
                    self.chapterNames[0], self.chapterNames[1] = 'Part A', 'Part B'
                else:
                    noAvant = False
                    self.chapterNames[0] = 'Avant'
                    for i in range(self.__ED-1):
                        self.chapterNames[i+1] = 'Part ' + chr(65 + i)
                if len(self.chapterNames) > self.__ED + 1:
                    self.chapterNames[-1] = 'Preview'
                    if len(self.chapterNames) > self.__ED + 2:
                        self.chapterNames[-2] = 'Part ' + chr(65 + self.__ED - int(not noAvant))
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
    chapterFiles_original = filedialog.askopenfilenames(title='[LP-Raws@LPSub] 选择章节文件 - Chapters Renamer by Lambholl', initialdir=__file__, filetypes=[('章节文件', '.txt')])
    try:
        for i in chapterFiles_original:
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
