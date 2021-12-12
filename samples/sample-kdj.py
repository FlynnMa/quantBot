#%%
"""
kdj算法和交易策略的基础实现
"""
import math
import pandas as pd
import flynnBot.flynnBot as fbot
import flynnBot.plots    as fplt

kdState = 'none'
kdProp = 0

def on_day_trade(i, df, holding_price):
    """
    交易策略的主体部分，决定是否买入卖出
    """
    global kdState, kdProp

    k = df['kdj-k'].iloc[i]
    if math.isnan(k):
        return 'none'

    # 如果获取了合法的k值
    d = df['kdj-d'].iloc[i]
    diff = k - d

    j1 = df['kdj-j'].iloc[i]
    j2 = df['kdj-j'].iloc[i-1]
    j3 = df['kdj-j'].iloc[i-2]
    jkDiff = df['kdj-jkdiff'].iloc[i]
    jkDiffHip = False
    jkDiffLop = False
    if j2 > j1 and j2 > j3:
        jkDiffHip = True
    if j2 < j1 and j2 < j3:
        jkDiffLop = True
    # 初始的状态
    crossAction = 'none'
    if kdState == 'none':
        if diff > 0:
            kdState = 'up'
        elif diff < 0:
            kdState = 'down'
        crossAction = 'none'
    elif kdState == 'up':
        if diff < 0:
            crossAction = 'crossDown'
            kdState = 'down'
    elif kdState == 'down':
        if diff > 0:
            crossAction = 'crossUp'
            kdState = 'up'

    action = 'none'
    if j2 < 0 and jkDiffLop is True:
        action = 'buy'
    elif (j2 > 60 and jkDiffHip is True) or jkDiff > 20:
        action = 'sell'
    # elif crossAction == 'crossDown':
    #     action = 'sell'

    if action == 'none':
        return action
    price = df['adjClose'].iloc[i]
    date = df['date'].iloc[i]
    print('%s @ %s - price:%s'%(action, date, price))
    #todo: add buy and sell confirmation signal
    # 假设
    #      prop5 = (ema5 - price) / close * 100
    #      prop22 = (ema22 - price) / close * 100
    # 增加买入条件:
    #  1. price < ema5 < ema22
    #  2. prop5 / prop22 >= 50%
    #  3. prop5 大于 2个点
    ema14 = df['ema_14'].iloc[i]
    ema48 = df['ema_48'].iloc[i]
    buy_confirmation = False
    sell_confirmation = False
    if price < ema14 and ema14 < ema48:
        buy_confirmation = True
        tmp = (ema14 - price) / price
        prop14 = tmp * 100
        tmp = (ema48 - ema14) / price
        prop48 = tmp * 100
        print('\tdown prop1(14) is:%s, prop2(48) is:%s'%(prop14, prop48))
    elif price > ema14 and ema14 > ema48:
        sell_confirmation = True
        tmp = (price - ema14) / price
        prop14 = tmp * 100
        tmp = (ema14 - ema48) / price
        prop48 = tmp * 100
        print('\tup prop1(14) is :%s, prop2(48) is:%s'%(prop14, prop48))

    final_action = 'none'
    if action == 'buy' and buy_confirmation is True:
        final_action = 'buy'
    if action == 'sell' and sell_confirmation is True:
        final_action = 'sell'
    return final_action

def kdj_indicator(df):
    """
    KDJ的指标计算，来源于investopedia和wikipedia
    """
    # 14 days by default for the k time window
    k_window = 14

    dx = pd.DataFrame(df[['adjClose', 'adjLow', 'adjHigh']])
    dx['max14'] = df['adjHigh'].rolling(window=k_window).max()
    dx['min14'] = df['adjLow'].rolling(window=k_window).min()

    df['kdj-k'] = 100 * ((dx['adjClose'] - dx['min14']) /
                         (dx['max14'] - dx['min14']))
    df['kdj-d'] = df['kdj-k'].ewm(com=2, adjust=False).mean()
    df['kdj-j'] = 3 * df['kdj-k'] - 2 * df['kdj-d']
    df['kdj-jkdiff'] = df['kdj-j'] - df['kdj-k']
    return df


def kdj_indicator2(df):
    """
    KDJ的指标计算，第二种方法，这个方法我回测下来，表现略好
    """

    # 14 days by default for the k time window
    k_window = 14

    dx = pd.DataFrame(df[['adjClose', 'adjLow', 'adjHigh']])
    dx['max14'] = df['adjHigh'].rolling(window=k_window).max()
    dx['min14'] = df['adjLow'].rolling(window=k_window).min()

    df['rsv'] = 100 * ((dx['adjClose'] - dx['min14']) /
                       (dx['max14'] - dx['min14']))
    df['kdj-k'] = df['rsv'].ewm(com=2, adjust=False).mean()
    df['kdj-d'] = df['kdj-k'].ewm(com=2, adjust=False).mean()
    df['kdj-j'] = 3 * df['kdj-k'] - 2 * df['kdj-d']
    df['kdj-jkdiff'] = df['kdj-j'] - df['kdj-k']
    return df


bot = fbot.botRunner(symbol='600918', start='2021-01-01')
bot.add_indicator(kdj_indicator2)
bot.add_indicator(None, 'macd')

bot.run(on_day_trade)

print("win rate: %f" % bot.win_rate)
print("capital return %f " % (bot.capital_return_rate * 100))
print("capital: enter(%f) exit(%f) " % (bot.enter_capital, bot.exit_capital))
print(bot.df_profits)

fplt.plot_overview(bot.df_main, title="my kdj first try",
indicators=['kdj', 'macd'])

fplt.plot_profits(bot.df_profits)

# %%
