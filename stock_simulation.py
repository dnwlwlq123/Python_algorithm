from util import company_lists, plot_line_graph
from random import random
import os 
from collections import defaultdict

class Stock:
    HISTORY_DIR = 'stock_history'
    def __init__(self, name):
        self.name = name 
        self.initial_price = 10000
        self.price_history = [10000]
        self.momentum = 10
        self.momentum_upper_bound = max(abs(random()-0.5), 0.5)
        self.momentum_lower_bound = -max(abs(random()-0.5), 0.5)
        self.price = self.initial_price
        
    
    def __hash__(self):
        return hash(self.name)
    
    def step(self, market):
        if random() < 0.05:
            self.price = self.price * 1.10
        elif random() > 0.95:
            self.price = self.price * 0.80
        else:
            self.momentum += (random() - 0.5) * 0.1 #+ self.momentum
            if self.momentum_upper_bound < self.momentum:
                self.momentum = self.momentum_lower_bound
            elif self.momentum_lower_bound > self.momentum:
                self.momentum = self.momentum_lower_bound
            delta = random() - 0.5 + self.momentum + market.momentum 
            self.price += self.momentum * self.price 
        self.price_history.append(self.price)

    def plot_history(self):
        if not os.path.exists(Stock.HISTORY_DIR):
            os.makedirs(Stock.HISTORY_DIR)
        
        plot_line_graph(self.price_history, save_to = f'stock_history/{self.name}.png', title = f'Price graph of {self.name}', x_label = 'time', y_label = '{self.name} price')
         

class StockMarket:
    def __init__(self, listed_stocks):
        self.listed_stocks = listed_stocks
        self.momentum = 0.01

    def step(self):
        for stock in self.listed_stocks: # 
            stock.step(self)

class Investor:
    def __init__(self, name = 'investor1', initial_asset = 10000000, strategy = lambda investor, market:None):
        self.name = name 
        self.asset = initial_asset
        self.cash = initial_asset 
        self.asset_history = [initial_asset]
        self.portfolio = defaultdict(float)
        self.strategy = strategy

    def buy(self, stock, amount):
        if self.cash - stock.price * amount >= 0:
            self.portfolio[stock] += amount
            self.cash -= stock.price * amount
        else:
            print('Out of money')

    def sell(self, stock, amount):
        if stock in self.portfolio and self.portfolio[stock] >= amount:
            self.portfolio[stock] -= amount 
            self.cash += stock.price * amount 
        else:
            print('Not enough stocks')

    def buy_or_sell(self, market):
        self.strategy(self, market)
        stock_asset = 0
        for stock, amount in self.portfolio.items():
            stock_asset += stock.price * amount
        self.asset = stock_asset + self.cash 
        self.asset_history.append(self.asset)

    def plot_history(self):
        plot_line_graph(self.asset_history, save_to = f'{self.name}.png', title = f'Asset History of {self.name}', x_label = 'time', y_label = '{self.name} Asset')


# def my_strategy(investor, market):

#     good_stocks = []
#     for stock in market.listed_stocks:
#         if len(stock.price_history) > 0:
#             initial_price = stock.price_history[0]
#             current_price = stock.price
#             if current_price < initial_price * 1.05:  
#                 good_stocks.append(stock)
    

#     if good_stocks:
#         for stock in good_stocks:
#             amount_to_buy = min(1, investor.cash // stock.price) 
#             if amount_to_buy > 0:
#                 investor.buy(stock, amount_to_buy)


def my_strategy(investor, market):
    day = 7
    top_stock = None
    max_increase = float('-inf')
    
    for stock in market.listed_stocks:
        if len(stock.price_history) > day:
            initial_price = stock.price_history[-day]
            current_price = stock.price
            increase = current_price - initial_price
            
            if increase > max_increase:
                max_increase = increase
                top_stock = stock

    if top_stock:
        amount_to_buy = min(100, investor.cash // top_stock.price)
        if amount_to_buy > 0:
            investor.buy(top_stock, amount_to_buy)
    
    for stock in list(investor.portfolio.keys()):
        if len(stock.price_history) > day:
            initial_price = stock.price_history[-day]
            if stock.price < initial_price:
                investor.sell(stock, investor.portfolio[stock])





def simulate(strategy, n_steps = 100, n_company = 10):
    investor = Investor(strategy=strategy) 
    stocks = []
    
    company_list = []

    if not os.path.exists(Stock.HISTORY_DIR):
        company_list = company_lists(n_company)
    else:
        company_list = [e.strip('.png') for e in os.listdir(Stock.HISTORY_DIR)]
        
        if len(company_list) > n_company:
            company_list = company_list[:n_company]
        else:
            company_list = company_list + company_lists(n_company - len(company_list))

    for name in company_list:
        stocks.append(Stock(name))

    market = StockMarket(stocks)

    for step in range(n_steps):
        market.step()
        investor.buy_or_sell(market)

    for stock in stocks:
        stock.plot_history()
    investor.plot_history()

if __name__ == '__main__':
    simulate(strategy = my_strategy)
    