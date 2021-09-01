
import pandas_datareader as pdr
import matplotlib.dates as mdates
import numpy as np
import matplotlib as mpl
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matBot.indicators as mindicators

mpl.rcParams['grid.color'] = 'gray'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linewidth'] = 0.2
SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


class matBot():
    def __init__(self, symbol='601398', init_cash=1000000,
                 init_share=0, start='2021-01-01', end=None):
        # stock symbol
        self.stock_symbol = symbol
        self.cash = init_cash
        self.share = init_share

        self.start = start
        self.end = datetime.date.today()
        if end is not None:
            self.end = end

    def fetch(self):
        """
        开始从网络获取数据

        Parameters
        ----------
        None

        Returns
        -------
        pandas data frame
        """
        df = pdr.get_data_tiingo(
            self.stock_symbol, start=self.start, end=self.end)
        # format data
        df.reset_index(level=0, inplace=True)
        df.index = df.index.date
        df.drop('symbol', axis=1, inplace=True)
        self.df = df
        return df

    def add_indicator(self, indicator_callback, built_in=None):
        """
        添加指标，这个函数会被直接调用，
        将计算结果直接合并汇总到系统pandas data frame里面去

        Parameters
        ----------
        indicator_callback : 回调函数
        built_in           : str
         内置的指标 'macd','kdj'

        Returns
        -------
        None
        """
        df = self.df
        if indicator_callback is not None:
            self.df = indicator_callback(df)
        if built_in == 'macd':
            self.df = mindicators.macd(df)

    def run_step(self, x, action):
        """
        执行一次买或者卖的动作

        Parameters
        ----------
        indicator_callback - 回调函数

        Returns
        -------
        None
        """
        day = self.df.index.values[x]
        execute_price = self.df.loc[day, 'adjClose']
        one_hand_price = execute_price * 100
        # buy
        if (action == 'buy') and (self.cash >= one_hand_price):
            num_hands = int(self.cash / one_hand_price)
            self.cash = self.cash - num_hands * one_hand_price
            self.share = num_hands * 100
            self.df.loc[day, 'buy'] = execute_price
            self.holding_days = 1
        # sell
        elif (action == 'sell') and (self.share >= 100):
            self.cash = self.share * execute_price + self.cash
            self.share = 0
            self.df.loc[day, 'sell'] = execute_price
            self.holding_days = 0
        else:
            self.holding_days = self.holding_days + 1

        self.df.loc[day, 'holding_days'] = self.holding_days
        self.df.loc[day, 'capital'] = execute_price * self.share + self.cash

    def run(self, strategic_callback):
        """
        执行所有时间的模拟交易

        Parameters
        ----------
        indicator_callback - 回调函数

        Returns
        -------
        None
        """
        df = self.df
        df['buy'] = np.nan
        df['sell'] = np.nan
        df['capital'] = np.nan
        # how many days elapsed for holding the stock
        df['holding_days'] = np.zeros
        self.holding_days = 0

        for x in range(len(df)):
            # get action
            action = 'none'
            if strategic_callback is not None:
                action = strategic_callback(x, df)
            self.run_step(x, action)

        self.buy_actions = df['buy'].dropna()
        self.sell_actions = df['sell'].dropna()
        buy_df = self.buy_actions.reset_index()
        buy_df.rename(columns={'index': 'buyDate'}, inplace=True)
        sell_df = self.sell_actions.reset_index()
        sell_df.rename(columns={'index': 'sellDate'}, inplace=True)
        profits_df = pd.concat([buy_df, sell_df], axis=1)
        profits_df['profits'] = profits_df['sell'] - profits_df['buy']
        profits_df['return_rate'] = profits_df['profits'] / profits_df['buy']
        self.num_trade = profits_df['profits'].count()
        self.num_win = sum(profits_df['profits'] > 0)
        self.win_rate = self.num_win / self.num_trade
        self.profits_df = profits_df


def matBotRunner(
        symbol='601398', init_cash=1000000, init_share=0,
        start='2021-01-01', end=None):
    """
    创建matBot， 获取交易数据

    Parameters
    ----------
    symbol      - 股票的交易代码
    init_cash   - 初始资金， 建议大于100股的市值
    init_share  - 初始持股，建议是100的整数倍
    start       - 获取交易数据的开始时间，例如'2010-01-01'
    end         - 获取交易数据的结束时间，默认不填为今天

    Returns
    -------
    创建的mbot对象
    """
    bot = matBot(symbol, init_cash, init_share, start, end)
    bot.fetch()
    print("fetch completed")
    return bot
