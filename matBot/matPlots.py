
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

indicators_dictonary = {
    'macd': ['macd', 'macd_signal'],
    'kdj': ['kdj-k', 'kdj-j']
}


def plot_indicator_simple(df, target_ax, ind):

    if ind is None:
        return
    indicators = indicators_dictonary[ind]
    colours = ['green', 'yellow', 'red', 'blue']
    df[indicators].plot(ax=target_ax, color=colours,
                        grid=True, rot=60)
    target_ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    target_ax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    target_ax.axhline(y=0, linestyle='--', color='gray')
    min = df[indicators[0]].min()
    max = df[indicators[0]].max()
    target_ax.vlines(x=df['buy'].dropna().index, ymin=min/2,
                     ymax=max/2, color='red', linestyle='--')
    target_ax.vlines(x=df['sell'].dropna().index, ymin=min/2,
                     ymax=max/2, color='green', linestyle='--')
    plt.legend(loc="best")


def plot_price_with_orders(df, indicators=['macd']):
    """
    绘制一段时间的价格和指标走势，标注买卖点

    Parameters
    ----------
    indicators - 需要显示的指标列表，
    可以是一个['macd'], 
    也可以是大于一个的，如：['macd', 'kdj']
    机器人将选择对应的数据,目前支持：
        'macd'  - ['macd'  ,  'macd_signal']
        'kdj'   - ['kdj-k' ,  'kdj-j']

    Returns
    -------
    None
    """
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle('macd strategy', fontsize=10)
    num_plots = 2 + len(indicators)
    axs = fig.subplots(num_plots)
    fig.tight_layout()

    df['adjClose'].plot(ax=axs[0], color='purple',
                        label='price', rot=60, grid=True)
    ypadding = df['adjClose'].mean() * 0.2
    ymin = df['adjClose'].min() - ypadding * 0.2
    ymax = df['adjClose'].max() + ypadding * 0.2
    df['ema_long'].plot(ax=axs[0], color='yellow', ylim=(ymin, ymax),
                        label='price', rot=60, grid=True)

    axs[0].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    axs[0].xaxis.set_major_locator(mdates.DayLocator(interval=10))
    axs[0].scatter(df.index, y=df['buy'].values, label='buy',
                   marker='^', s=70, color='red')
    axs[0].scatter(df.index, y=df['sell'].values, label='sell',
                   marker='x', s=70, color='#00ff00')

    ax_twin = axs[0].twinx()
    rspine = ax_twin.spines['right']
    df['capital'].plot(ax=ax_twin, rot=60)

    df['capital'].plot(ax=axs[1], rot=60)
    axs[1].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    axs[1].xaxis.set_major_locator(mdates.DayLocator(interval=10))

    index = 2
    for ind in indicators:
        plot_indicator_simple(df, axs[index], ind)
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
