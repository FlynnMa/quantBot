
import pandas_datareader as pdr
import matplotlib.dates as mdates
import numpy as np
import matplotlib as mpl
import pandas as pd
import datetime
import matplotlib.pyplot as plt

mpl.rcParams['grid.color'] = 'gray'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linewidth'] = 0.2


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
        day = self.df.index.values[0]
        execute_price = self.df.loc[day, 'adjClose']
        one_hand_price = execute_price * 100
        # buy
        if (action == 'buy') and (self.cash >= one_hand_price):
            num_hands = int(self.cash / one_hand_price)
            self.cash = self.cash - num_hands * one_hand_price
            self.share = num_hands * 100
            self.df.loc[day, 'buy'] = execute_price
        # sell
        elif (action == 'sell') and (self.share >= 100):
            self.cash = self.share * execute_price + self.cash
            self.share = 0
            self.df.loc[day, 'sell'] = execute_price
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

    def plot_price_with_orders(self, indicator='macd'):
        """
        绘制一段时间的价格和指标走势，标注买卖点

        Parameters
        ----------
        indicator_callback - 回调函数

        Returns
        -------
        None
        """
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(12, 8))
        fig.suptitle('macd strategy', fontsize=60)
        axs = fig.subplots(2)
        fig.tight_layout()

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

        if indicator == 'macd':
            self.df['macd'].plot(ax=axs[1], color='green',
                                 label='macd', grid=True, rot=60)
            self.df['macd_signal'].plot(
                ax=axs[1], color='yellow', label='signal')
            axs[1].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
            axs[1].xaxis.set_major_locator(mdates.DayLocator(interval=5))
            axs[1].axhline(y=0, linestyle='--', color='gray')
            axs[1].vlines(x=self.buy_actions.index, ymin=-1,
                          ymax=1, color='red', linestyle='--')
            axs[1].vlines(x=self.sell_actions.index, ymin=-1,
                          ymax=1, color='green', linestyle='--')
        plt.legend(loc="best")
        plt.show()

    def plot_deals(self):
        fig = plt.figure(figsize=(12, 8))
        fig.suptitle('orders analysis', fontsize=60)
        axs = fig.subplots(3)
        fig.tight_layout()

        buy_df = self.buy_actions.reset_index()
        buy_df.rename(columns={'index': 'buyDate'}, inplace=True)
        sell_df = self.sell_actions.reset_index()
        sell_df.rename(columns={'index': 'sellDate'}, inplace=True)
        deal_df = pd.concat([buy_df, sell_df], axis=1)

        if (len(deal_df) == 0):
            print("no orders!")
            exit()
        color_dict = {'buy': 'red', 'sell': 'green'}
        df2 = deal_df.loc[:, ['buy', 'sell']]
        df2.plot(ax=axs[0], kind='bar', color=color_dict, rot=90)

        # profit
        deal_df['profits'] = deal_df['sell'] - deal_df['buy']
        deal_df['rate'] = deal_df['profits'] / deal_df['buy']
        colors = np.where(deal_df['profits'].values > 0, 'r', 'g')
        deal_df['profits'].plot(
            ax=axs[1], kind='bar', color=colors, title='profit')
        deal_df['rate'].plot(ax=axs[2], title='return rate')
        plt.show()


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
