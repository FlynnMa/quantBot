"""
交易机器人
"""
import time
import datetime
import numpy as np

import pandas as pd
import pandas_datareader as pdr

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib as mpl

import flynnBot.indicators as mindicators

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


class flynnBot():
    """
    交易机器人
    """

    def __init__(self, symbol='601398', init_cash=1000000,
                 init_share=0, start='2021-01-01', end=None):
        # stock symbol
        self.stock_symbol = symbol
        self.cash = init_cash
        self.share = init_share
        self.enter_capital = 0.0
        self.exit_capital = 0.0
        self.capital_return = 0.0
        self.capital_return_rate = 0.0
        self.holding_days = 0
        self.holding_price = 0.0
        self.starting_price = 0.0
        self.num_win = 0
        self.win_rate = 0.0
        self.num_trade = 0

        self.df_main = None
        self.df_profits = None
        self.buy_actions = None
        self.sell_actions = None
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
        pandas data frame or None failed
        """
        df_main = None
        try:
            df_main = pdr.get_data_tiingo(
                self.stock_symbol, start=self.start, end=self.end)
        except Exception as e:
            print(e)
            print("tiingo timeout accurrs")
            time.sleep(2)
            return df_main


        # format data
        df_main.reset_index(level=0, inplace=True)
        df_main.index = df_main.index.date
        df_main.drop('symbol', axis=1, inplace=True)
        df_main = df_main.rename_axis('date').reset_index()
        df_main['date_str'] = df_main['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        # df.set_index('date_str', inplace=True)
        self.starting_price = df_main.head(1)['adjClose'].values[0]
        df_main['ema_48'] = df_main['adjClose'].ewm(span=22).mean()
        df_main['ema_14'] = df_main['adjClose'].ewm(span=5).mean()
        self.enter_capital = self.starting_price * self.share + self.cash
        self.df_main = df_main
        return df_main

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
        df_main = self.df_main
        if indicator_callback is not None:
            self.df_main = indicator_callback(df_main)
        if built_in == 'macd':
            self.df_main = mindicators.macd(df_main)

    def run_step(self, i, action):
        """
        执行一次买或者卖的动作

        Parameters
        ----------
        indicator_callback - 回调函数

        Returns
        -------
        None
        """
        day = self.df_main.index.values[i]
        execute_price = self.df_main.loc[day, 'adjClose']
        one_hand_price = execute_price * 100
        # buy
        if (action == 'buy') and (self.cash >= one_hand_price):
            num_hands = int(self.cash / one_hand_price)
            self.cash = self.cash - num_hands * one_hand_price
            self.share = num_hands * 100 + self.share
            self.df_main.loc[day, 'buy'] = execute_price
            self.holding_days = 1
            self.holding_price = execute_price
        # sell
        elif (action == 'sell') and (self.share >= 100):
            self.cash = self.share * execute_price + self.cash
            self.share = 0
            self.df_main.loc[day, 'sell'] = execute_price
            self.holding_days = 0
            self.holding_price = 0
        elif self.share >= 100:
            self.holding_days = self.holding_days + 1

        self.df_main.loc[day, 'holding_days'] = self.holding_days
        self.df_main.loc[day, 'capital'] = execute_price * self.share + self.cash

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
        df_main = self.df_main
        df_main['buy'] = np.nan
        df_main['sell'] = np.nan
        df_main['capital'] = np.nan
        # how many days elapsed for holding the stock
        df_main['holding_days'] = np.zeros
        self.holding_days = 0

        for i in range(len(df_main)):
            # get action
            action = 'none'
            if strategic_callback is not None:
                action = strategic_callback(i, df_main, self.starting_price)
            self.run_step(i, action)

        self.buy_actions = df_main['buy'].dropna()
        self.sell_actions = df_main['sell'].dropna()
        buy_df = self.buy_actions.reset_index()
        buy_df.rename(columns={'index': 'buyDate'}, inplace=True)
        sell_df = self.sell_actions.reset_index()
        sell_df.rename(columns={'index': 'sellDate'}, inplace=True)
        profits_df = pd.concat([buy_df, sell_df], axis=1)
        profits_df['profits'] = profits_df['sell'] - profits_df['buy']
        profits_df['return_rate'] = profits_df['profits'] / profits_df['buy']
        self.num_trade = profits_df['profits'].count()
        self.num_win = sum(profits_df['profits'] > 0)
        if self.num_trade != 0:
            self.win_rate = self.num_win / self.num_trade
        self.df_profits = profits_df
        self.exit_capital = self.df_main.tail(1)['capital'].values[0]
        self.capital_return = self.exit_capital - self.enter_capital
        self.capital_return_rate = self.capital_return / self.enter_capital

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
        fig.suptitle('macd strategy', fontsize=10)
        axs = fig.subplots(3)

        self.df_main['adjClose'].plot(ax=axs[0], color='purple',
                                 label='price', rot=60, grid=True)
        ypadding = self.df_main['adjClose'].mean() * 0.2
        ymin = self.df_main['adjClose'].min() - ypadding * 0.2
        ymax = self.df_main['adjClose'].max() + ypadding * 0.2
        self.df_main['ema_long'].plot(ax=axs[0], color='yellow', ylim=(ymin, ymax),
                                 label='price', rot=60, grid=True)

        axs[0].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        axs[0].xaxis.set_major_locator(mdates.DayLocator(interval=20))
        axs[0].vlines(x=self.buy_actions.index, ymin=ymin,
                      ymax=self.buy_actions.values, color='red', linestyle='--')
        axs[0].vlines(x=self.sell_actions.index, ymin=ymin,
                      ymax=self.sell_actions.values, color='green', linestyle='--')
        axs[0].scatter(self.df_main.index, y=self.df_main['buy'].values, label='buy',
                       marker='^', s=70, color='red')
        axs[0].scatter(self.df_main.index, y=self.df_main['sell'].values, label='sell',
                       marker='x', s=70, color='#00ff00')
        axs[0].legend()

        percent = self.capital_return_rate * 100
        ret_info = "return rate : %.2f percent\n" % percent
        ret_info += "exit capital : %d" % self.exit_capital
        self.df_main['capital'].plot(ax=axs[1], rot=60)
        # axs[1].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        # axs[1].xaxis.set_major_locator(mdates.DayLocator(interval=10))
        axs[1].text(0.1, 0.8, ret_info, fontsize=8,
                    color="orange", transform=axs[1].transAxes)

        if indicator == 'macd':
            self.df_main['macd'].plot(ax=axs[2], color='green',
                                 label='macd', grid=True, rot=60)
            self.df_main['macd_signal'].plot(
                ax=axs[2], color='yellow', label='signal', rot=60)
            # axs[2].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
            # axs[2].xaxis.set_major_locator(mdates.DayLocator(interval=10))
            axs[2].axhline(y=0, linestyle='--', color='gray')
            min_macd = self.df_main['macd'].min()
            max_macd = self.df_main['macd'].max()
            axs[2].vlines(x=self.buy_actions.index, ymin=min_macd/2,
                          ymax=max_macd/2, color='red', linestyle='--')
            axs[2].vlines(x=self.sell_actions.index, ymin=min_macd/2,
                          ymax=max_macd/2, color='green', linestyle='--')
            plt.legend(loc="best")

        plt.tight_layout()
        plt.show()

    def plot_deals(self):
        """
        这个函数不再维护了，使用plots.plot_profits 替代
        """
        fig = plt.figure(figsize=(12, 8))
        fig.suptitle('orders analysis', fontsize=12)
        axs = fig.subplots(3)
        fig.tight_layout()

        buy_df = self.buy_actions.reset_index()
        buy_df.rename(columns={'index': 'buyDate'}, inplace=True)
        sell_df = self.sell_actions.reset_index()
        sell_df.rename(columns={'index': 'sellDate'}, inplace=True)
        deal_df = pd.concat([buy_df, sell_df], axis=1)

        if len(deal_df) == 0:
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
        title_str = 'return rate diagram'
        deal_df['rate'].plot(
            ax=axs[2], title=title_str)
        percent = self.win_rate * 100
        trade_info = "win rate:%.2f percent\n" % percent
        info = "Win : %d -  Total : %d" % (self.num_win, self.num_trade)
        trade_info += info
        axs[2].text(0, 1, trade_info,  fontsize=8, color="orange")

        plt.tight_layout()
        plt.show()


def botRunner(
        symbol='601398', init_cash=1000000, init_share=0,
        start='2021-01-01', end=None):
    """
    这是一个帮助函数，负责创建flynnBot，并且获取交易数据

    Parameters
    ----------
    symbol      - 股票的交易代码
    init_cash   - 初始资金， 建议大于100股的市值
    init_share  - 初始持股，建议是100的整数倍
    start       - 获取交易数据的开始时间，例如'2010-01-01'
    end         - 获取交易数据的结束时间，默认不填为今天

    Returns
    -------
    创建的mbot对象, 或者None 表示失败
    """
    bot = flynnBot(symbol, init_cash, init_share, start, end)
    ret = bot.fetch()
    if ret is None:
        return None
    print("fetch completed")
    return bot
