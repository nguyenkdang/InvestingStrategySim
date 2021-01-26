import random
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from time import clock, sleep, process_time


def perChange( old, new):
    return (new - old) / old

class simulation:
    def __init__(self, balance, stockPool, startDate, endDate):
        self.startBal = balance
        self.balance = balance
        self.portfolio = {}
        self.stockPool = stockPool
        self.startDate = startDate
        self.endDate = endDate
        sp = ''
        for s in stockPool: sp += s + ' '
        
        self.stockData = yf.download(sp, start=startDate, end=endDate)
        print(self.stockData)
        self.recInfo = {}
        self.today  = 0
        self.newDay = 1
    
    def printSummary(self):
        msg = "Cash Balance:  ${:.5f}\n".format(self.balance)       +\
            "Portfolio original Value: ${:.5f}\n".format(self.getPortBVal())   +\
            "Portfolio current Value: ${:.5f}\n".format(self.getPortMVal())   +\
            "Current Balance: ${:.5f}\n".format(self.getTotalVal())   +\
            "Current Profit: ${:.5f}\n".format(self.getProfit()) +\
            "% Profit: {:.5f}%\n".format(perChange(self.startBal, self.getTotalVal()) * 100 )

        print(msg)
    
    def printPortf(self):
        for symb, val in self.portfolio.items():
            print(symb)
            for s in val:
                print('${:.2f}  x{} {}'.format(s[0], s[1], str(s[2])))
    
    def getProfit(self):
        return self.getTotalVal() - self.startBal

    def getPortMVal(self):
        portVal = 0
        for symb, val in self.portfolio.items():
            date = str(self.newDay.date())
            price = self.stockData.loc[date]['Low'][symb]
            if price != price: continue
            for s in val:
                portVal += price * s[1]
        
        return portVal

    def getPortBVal(self):
        portVal = 0 
        for symb, val in self.portfolio.items():
            for s in val:
                portVal += s[0] * s[1]
        return portVal

    def getTotalVal(self):
        return self.getPortMVal() + self.balance

    def getAvgPrice(self, stockHist):
        p = 0
        n = 0
        for s in stockHist:
            p += s[0] * s[1]
            n += s[1]

        if n == 0: return 0
        else: return p/n

    def SB_random(self, mode):
        #return a dictionary or randomly ordered stock
        amnt = 1
        rank = {}
        for symb in self.stockPool:
            rank[symb] = (random.choice([1, 0]), amnt)

        return rank

    def buyAction(self, symbol, amount):
        date = self.newDay
        try:
            price = self.stockData.loc[str(date.date())]['High'][symbol]
        except KeyError:
            return 0
        
        if self.balance >= price*amount:
            self.balance -= price*amount
            if symbol in self.portfolio: self.portfolio[symbol].append([price, amount, date]) 
            else: self.portfolio[symbol] = [ [price, amount, date] ]
            return price
        return 0
    
    def sellAction(self, symbol, amount):
        toSell = amount
        date = self.newDay
        price = self.stockData.loc[str(date.date())]['Low'][symbol]
        if symbol in self.portfolio and amount <= sum([s[1] for s in self.portfolio[symbol]]):
            while toSell > 0:
                m = min(self.portfolio[symbol], key= lambda k: k[2])
                i =  self.portfolio[symbol].index(m)
                if m[2] == date: return 1 #Prevent Day Trading
                
                if self.portfolio[symbol][i][1] > toSell: self.portfolio[symbol][i][1] -= toSell
                else: self.portfolio[symbol].remove(m)
                toSell -= m[1]

            self.balance += price *amount
            if self.portfolio[symbol] == []: del self.portfolio[symbol]
            return price  
        return 0

    def simulate(self, buyMethod, sellMethod):   
        for time, stocks in self.stockData.iterrows():
                startTime = process_time()
                self.newDay = datetime.fromisoformat(str(time))
                print("Time:", time)

                #Decide to buy
                rank = buyMethod('BUY')
                if bool(rank):
                    topRnk = max(rank, key=lambda key: rank[key][0])
                    rsp = self.buyAction(topRnk, rank[topRnk][1])
                    if rsp > 0: print("Bought {} at {} x{} \nBalance: {}".format(topRnk, rsp, rank[topRnk][1], self.balance))
                
                #Decide to sell
                rank = sellMethod('SELL')
                if bool(rank):
                    topRnk = max(rank, key=lambda key: rank[key][0])
                    rsp = self.sellAction(topRnk, rank[topRnk][1])
                    if rsp > 0: print("Sold {} at {} x{} \nBalance: {}".format(topRnk, rsp, rank[topRnk][1], self.balance))
                self.today = self.newDay
                print("--- %s seconds ---" % (process_time() - startTime))
                print()
        return 0


if __name__ == "__main__":
    #Data Accumulation
    stockPool = {'BAC', 'CRSP', 'UAL', 'ET', 'NVDA', 'GOOGL', 'MSFT', 'ZM'}    
    sim = simulation(1000, stockPool, '2019-1-25', '2019-12-25')
    sim.simulate(sim.SB_random, sim.SB_random)
    sim.printSummary()