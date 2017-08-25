import os

"""
PySlot
Copyrights (C) 2017 Mason McElroy
masonic@gmail.com

**********************************************************************

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

 3. The names of its contributors may not be used to endorse or promote
    products derived from this software without specific prior written
    permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import random
import time
from random import randint


# A list of all symbols to be used
class Symbol:

    W1, W2,\
    M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, \
    H1, H2, H3, H4, H5, H6, H7, H8, H9, H10, \
    S1, S2,  B1, B2, SYMBOLS = range(27)

    symString = [
        "W1", "W2",\
        "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", \
        "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", \
        "S1", "S2", "B1", "B2", "XX"
    ]

# Game states
class Mode:
    BG, FG, MODES = range(3)

class PySlot:

    # List of program attributes
    sim = True
    simCount = 100000000

    # List of game specific attributes
    REELS = 5
    ROWS = 3
    LINES = 5
    ANTE = 0
    BET = LINES + ANTE
    XX = 1028

    comboPays = [[[0 for k in range(REELS+1)] for j in range(Symbol.SYMBOLS)] for i in range(Mode.MODES)]
    line = [[0 for j in range(REELS)] for i in range(LINES)]

    reel = [[[0 for k in range(XX)] for j in range(REELS)] for i in range(Mode.MODES)]
    reelWeights = [[[0 for k in range(XX)] for j in range(REELS)] for i in range(Mode.MODES)]
    reelLength = [[0 for k in range(REELS)] for j in range(Mode.MODES)]
    screen = [[Symbol.SYMBOLS for k in range(ROWS)] for j in range(REELS)]
    reelOffset = 1

    # Game tracking info

    Pay = [0 for k in range(Mode.MODES)]
    totalPay = 0
    squared_totalPay = 0
    volatility = 0

    def __init__(self):
        random.seed(time.time())
        self.loadGameLines()
        self.loadGameData()

    def Random(self, range):
        return randint(0, range - 1)

    def getWeightedTableIndex(self, weighted_table):
        rand = self.Random(sum(weighted_table))
        index = 0
        i = weighted_table[0] - 1

        while (i < rand):
            index += 1
            i += weighted_table[index]

        return index

    def printScreen(self):
        for row in range(self.ROWS):
            for reel in range(self.REELS):
                print Symbol.symString[self.screen[reel][row]], '\t',
            print '\n',

    def loadGameLines(self):
        self.line[0] = [1, 1, 1, 1, 1]
        self.line[1] = [0, 0, 0, 0, 0]
        self.line[2] = [2, 2, 2, 2, 2]
        self.line[3] = [0, 1, 2, 1, 0]
        self.line[4] = [2, 1, 0, 1, 2]

    def loadGameData(self):
        file = open("gamedata.txt", 'r')
        game_data = []

        for line in file:
            game_data.append(line)

        file.close()

        # Get game reels
        for mode in range(Mode.MODES):
            for i in range(self.REELS):
                # Get reel data
                self.reel[mode][i] = game_data[2 * mode * (self.REELS + 1) + i].replace('\n',"").split(' ')
                self.reelWeights[mode][i] = game_data[(2 * mode + 1) * (self.REELS + 1) + i].replace('\n',"").split(' ')

                # Convert to integer
                self.reel[mode][i] = map(int, self.reel[mode][i])
                self.reelWeights[mode][i] = map(int, self.reelWeights[mode][i])


        # Get game pays
        pay_start = 2 * Mode.MODES * (self.REELS + 1)

        for mode in range(Mode.MODES):
            for sym in range(Symbol.SYMBOLS):
                self.comboPays[mode][sym] = game_data[pay_start + sym].replace('\n',"").split(' ')
                self.comboPays[mode][sym] = map(int, self.comboPays[mode][sym])

    def spin(self, mode):
        for col in range(self.REELS):
            index = self.getWeightedTableIndex(self.reelWeights[mode][col])

            for row in range(self.ROWS):
                stop = index - self.reelOffset + row

                if stop < 0:
                    stop += len(self.reel[mode][col])

                self.screen[col][row] = self.reel[mode][col][stop % len(self.reel[mode][col])]

    def lineEval(self, line, mode):

        sym = line[0]
        combo_size = 1

        # Case where line starts with a Wild
        if sym == Symbol.W1 or sym == Symbol.W2:
            wild_combo_size = 1

            while wild_combo_size < len(line) and (line[wild_combo_size] == Symbol.W1 or line[wild_combo_size] == Symbol.W2):
                wild_combo_size += 1



            combo_size = wild_combo_size

            if combo_size == len(line):
                return sym, combo_size, self.comboPays[mode][sym][combo_size]

            # Check if we can make a larger line win from non-Wild symbols
            else:
                sym2 = line[combo_size]

                while combo_size < len(line) and \
                        (line[combo_size] == sym2 or line[combo_size] == Symbol.W1 or line[combo_size] == Symbol.W2):
                    combo_size += 1

                if self.comboPays[mode][sym][wild_combo_size] > self.comboPays[mode][sym2][combo_size]:
                    return sym, wild_combo_size, self.comboPays[mode][sym][wild_combo_size]
                else:
                    return sym2, combo_size, self.comboPays[mode][sym2][combo_size]

        # Case where line starts with a non-Wild symbol
        else:
            while combo_size < len(line) and \
                    (line[combo_size] == sym or line[combo_size] == Symbol.W1 or line[combo_size] == Symbol.W2):
                combo_size += 1

            return sym, combo_size, self.comboPays[mode][sym][combo_size]

    def totalLineEval(self, mode):
        total_pay = 0

        for line in self.line:

            # Get a list of symbols on the line
            symbols_on_line = [0] * self.REELS
            for i in range(self.REELS):
                symbols_on_line[i] = self.screen[i][line[i]]

            temp_sym, temp_combo_size, temp_pay = self.lineEval(symbols_on_line, mode)
            total_pay += temp_pay

        return total_pay

    def countScatters(self, mode):
        pass

    def printResults(self, sims=0):

        if sims % (self.simCount / 100) == 0:
            os.system('cls' if os.name == 'nt' else 'clear')

            print '\n'
            print 100 * sims / self.simCount, "%"
            print float(self.total_pay) / (self.BET * sims)

    def runSimulation(self, sim_count = 100000000):
        self.simCount = sim_count
        self.total_pay = 0

        sim = 0
        while sim < self.simCount:
            self.spin(Mode.BG)
            self.total_pay += self.totalLineEval(Mode.BG)

            sim += 1

            self.printResults(sim)
            
    def runTheoretical(self, mode):
        pass






test = PySlot()
print test.runSimulation(100000)


