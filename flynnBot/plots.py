
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib.ticker import (MultipleLocator,AutoMinorLocator)

mpl.rcParams['grid.color'] = 'gray'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linewidth'] = 0.4
SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12
plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=SMALL_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

# 指标显示有关的定义
indicators_dictonary = {
    'macd': ['macd', 'macd_signal'],
    'kdj': ['kdj-k', 'kdj-d', 'kdj-j']
}
style_list = ['-', '-', '--', '--', '--']
linewidth_list  = [1.1, 1, 0.8, 0.8, 0.8]
zorder_list  = [5,4,3,2,1]
colours_list = ['darkcyan', 'yellow', 'slategray', 'salmon']


def plot_indicator_simple(df, target_ax, ind, show_label):

    if ind is None:
        return
    indicators = indicators_dictonary[ind]
    
    for i in range(len(indicators)):
        data = indicators[i]
        s = style_list[i]
        w = linewidth_list[i]
        z = zorder_list[i]
        c = colours_list[i]
        df[data].plot(ax=target_ax, color=c,
                        style=s, linewidth=w, zorder=z)
    target_ax.set_xlim(0, len(df))
    target_ax.set_xticks(df.index)
    target_ax.grid(True)
    if show_label == True:
        target_ax.set_xticklabels(df['date_str'], rotation=30)
    else :
        target_ax.set_xticklabels(df['date_str'].str.slice(start=5, stop=10))
    

    target_ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    target_ax.xaxis.set_major_locator(mdates.DayLocator(interval=20))
    target_ax.axhline(y=0, linestyle='--', color='gray')
    # min = df[indicators[0]].min()
    # max = df[indicators[0]].max()
    buy_indexes = df['buy'].dropna().index
    buy_indicators = df.loc[buy_indexes, indicators[0]]

    sell_indexes = df['sell'].dropna().index
    sell_indicators = df.loc[sell_indexes, indicators[0]]
    target_ax.vlines(x=buy_indexes, ymin=0, ymax=buy_indicators,
                     color='orangered', linestyle='--', linewidth=0.8)
    target_ax.vlines(x=sell_indexes, ymin=0, ymax=sell_indicators,
                     color='green', linestyle='--', linewidth=0.8)
    target_ax.legend(loc='best')


def plot_overview(df, title="overview", indicators=['macd']):
    """
    绘制一段时间的价格和指标走势，标注买卖点

    Parameters
    ----------
    indicators - 需要显示的指标列表，
    可以是一个['macd'], 
    也可以是大于一个的，如：['macd', 'kdj']
    机器人将选择对应的数据,目前支持：
        'macd'  - ['macd'  ,  'macd_signal']
        'kdj'   - ['kdj-k' ,  'kdj-d']

    Returns
    -------
    None
    """
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle(title, fontsize=10)
    num_plots = 1 + len(indicators)
    axs = fig.subplots(num_plots)
    fig.tight_layout()

    df['capital'].plot(ax=axs[0], color='yellow')
    ax_twin = axs[0].twinx()

    colours = ['green', 'red']
    ypadding = df['adjClose'].mean() * 0.2
    ymin = df['adjClose'].min() - ypadding * 0.2
    ymax = df['adjClose'].max() + ypadding * 0.2
    df[['ema_60', 'adjClose']].plot(ax=ax_twin, color=colours,
                                      ylim=(ymin, ymax), label=[
                                          'ema_long', 'price'],
                                      grid=True, linewidth=1)
    ax_twin.set_xticks(df.index)
    ax_twin.set_xticklabels(df['date_str'].str.slice(start=5, stop=10), rotation=60)
    axs[0].set_xlim(0, len(df))
    ax_twin.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax_twin.xaxis.set_major_locator(mdates.DayLocator(interval=20))
    # ax_twin.xaxis.set_major_locator(MultipleLocator(10))

    buy_indexes = df['buy'].dropna().index
    buy_prices = df['buy'].dropna().values

    sell_indexes = df['sell'].dropna().index
    sell_prices = df['sell'].dropna().values
    ax_twin.scatter(buy_indexes, y=buy_prices, label='buy',
                    marker='^', s=20, color='red')
    ax_twin.scatter(sell_indexes, y=sell_prices, label='sell',
                    marker='v', s=20, color='green')
    ax_twin.vlines(x=buy_indexes, ymin=0, ymax=buy_prices,
                   color='red', linestyle='--', linewidth=0.8)
    ax_twin.vlines(x=sell_indexes, ymin=0, ymax=sell_prices,
                   color='green', linestyle='--', linewidth=0.8)

    axs[0].legend(loc='lower left')
    ax_twin.legend(loc='best')

    index = 1
    for ind in indicators:
        show_label = False
        if index == len(indicators):
            show_label = True
        plot_indicator_simple(df, axs[index], ind, show_label)
        index = index + 1

    plt.tight_layout()
    plt.show()


def plot_profits(profits_df):
    """
    绘制所有交易的盈利与亏损情况

    Parameters
    ----------
    indicator_callback - 回调函数

    Returns
    -------
    None
    """
    if (len(profits_df) == 0):
        print("no orders!")
        exit()

    fig = plt.figure(figsize=(12, 8))
    fig.suptitle('orders analysis', fontsize=12)
    axs = fig.subplots(3)
    fig.tight_layout()

    color_dict = {'buy': 'red', 'sell': 'green'}
    df2 = profits_df.loc[:, ['buy', 'sell']]
    df2.plot(ax=axs[0], kind='bar', color=color_dict, rot=90)

    # profit
    colors = np.where(profits_df['profits'].values > 0, 'r', 'g')
    profits_df['profits'].plot(
        ax=axs[1], kind='bar', color=colors, title='profit')
    title_str = 'return rate analysis'
    profits_df['return_rate'].plot(ax=axs[2], title=title_str)
    num_trade = profits_df['profits'].count()
    num_win = sum(profits_df['profits'] > 0)
    win_rate = num_win / num_trade
    percent = win_rate * 100
    trade_info = "total earn rate:%.2f percent\n" % percent
    info = "Win : %d -  Total : %d" % (num_win, num_trade)
    trade_info += info
    axs[2].text(0, 0, trade_info,  fontsize=8, color="orange")

    plt.tight_layout()
    plt.xticks(fontsize=8)
    plt.show()
