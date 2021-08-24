
import pandas_datareader as pdr
import matplotlib.dates as mdates
import numpy as np
import matplotlib as mpl
import pandas as pd
import datetime
import matplotlib.pyplot as plt

mpl.rcParams['grid.color'] = 'gray'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linewidth'] = 0.1


class matBot():
    def __init__(self, symbol='601398', init_cash=1000000,
                 init_share=0, start='2021-01-01', end=None):
        # stock symbol
        self.stock_symbol = symbol
        self.cash = init_cash
        self.share = init_share
        self.buy_list = []
        self.sell_list = []
        self.capital_list = []

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

    def add_indicator(self, indicator_callback):
        """
        添加指标，这个函数会被直接调用，
        将计算结果直接合并汇总到系统pandas data frame里面去

        Parameters
        ----------
        indicator_callback - 回调函数

        Returns
        -------
        None
        """
        df = self.df
        if indicator_callback is not None:
            self.df = indicator_callback(df)

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
        execute_price = self.df['adjClose'].iloc[x]
        one_hand_price = execute_price * 100
        # buy
        if (action == 'buy') and (self.cash >= one_hand_price):
            num_hands = int(self.cash / one_hand_price)
            self.cash = self.cash - num_hands * one_hand_price
            self.share = num_hands * 100
            self.df['buy'].iloc[x] = execute_price
        # sell
        elif (action == 'sell') and (self.share >= 100):
            self.cash = self.share * execute_price + self.cash
            self.share = 0
            self.df['sell'].iloc[x] = execute_price
        self.df['capital'].iloc[x] = execute_price * self.share + self.cash

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
        self.profits_df = profits_df

    def view_full(self):
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(12, 8))
        fig.suptitle('macd strategy', fontsize=60)
        axs = fig.subplots(2)

        self.df['adjClose'].plot(ax=axs[0], color='purple',
                                 label='price', rot=90, grid=True)
        self.df['ema_long'].plot(ax=axs[0], color='yellow',
                                 label='price', rot=90, grid=True)

        axs[0].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        axs[0].xaxis.set_major_locator(mdates.DayLocator(interval=5))
        axs[0].vlines(x=self.buy_actions.index, ymin=0,
                      ymax=self.buy_actions.values, color='red', linestyle='--')
        axs[0].vlines(x=self.sell_actions.index, ymin=0,
                      ymax=self.sell_actions.values, color='green', linestyle='--')
        axs[0].scatter(self.df.index, y=self.df['buy'].values, label='buy',
                       marker='^', s=70, color='red')
        axs[0].scatter(self.df.index, y=self.df['sell'].values, label='sell',
                       marker='x', s=70, color='#00ff00')

        self.df['macd'].plot(ax=axs[1], color='green', label='macd', grid=True)
        self.df['macd_signal'].plot(ax=axs[1], color='yellow', label='signal')
        axs[1].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        axs[1].xaxis.set_major_locator(mdates.DayLocator(interval=5))
        axs[1].axhline(y=0, linestyle='--', color='gray')
        axs[1].vlines(x=self.buy_actions.index, ymin=-1,
                      ymax=1, color='red', linestyle='--')
        axs[1].vlines(x=self.sell_actions.index, ymin=-1,
                      ymax=1, color='green', linestyle='--')
        plt.legend(loc="best")
        plt.show()


def matBotRunner(symbol='601398', init_cash=1000000, init_share=0, start='2021-01-01', end=None):
    bot = matBot(symbol, init_cash, init_share, start, end)
    bot.fetch()
    print("fetch done")
    return bot
