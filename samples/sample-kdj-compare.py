"""
比较两种kdj算法的不同,
也可借鉴这个方法来比较其他的指标之间的差异
"""

import math
import pandas as pd
import flynnBot.flynnBot as fbot

state = 'none'

def on_day_trade(i, df, holding_price):
    """
    买卖策略，决定这一天是否买入
    """

    global state

    k = df['kdj-k'].iloc[i]
    if math.isnan(k):
        return 'none'

    # 如果获取了合法的k值
    d = df['kdj-d'].iloc[i]
    diff = k - d

    # 初始的状态
    action = 'none'
    if state == 'none':
        if diff > 0:
            state = 'crossup'
        elif diff < 0:
            state = 'crossdown'
        action = 'none'
    elif state == 'crossup':
        if diff < 0:
            action = 'sell'
            state = 'crossdown'
    elif state == 'crossdown':
        if diff > 0:
            action = 'buy'
            state = 'crossup'

    return action


def kdj_indicator(df_main):
    """
    KDJ的指标计算，来源于investopedia和wikipedia
    """
    # 14 days by default for the k time window
    k_window = 14

    dx = pd.DataFrame(df_main[['adjClose', 'adjLow', 'adjHigh']])
    dx['max14'] = df_main['adjHigh'].rolling(window=k_window).max()
    dx['min14'] = df_main['adjLow'].rolling(window=k_window).min()

    df_main['kdj-k'] = 100 * ((dx['adjClose'] - dx['min14']) /
                         (dx['max14'] - dx['min14']))
    df_main['kdj-d'] = df_main['kdj-k'].ewm(com=2, adjust=False).mean()
    df_main['kdj-j'] = 3 * df_main['kdj-k'] - 2 * df_main['kdj-d']
    return df_main


def kdj_indicator2(df_main):
    """
    KDJ的指标计算，第二种方法，这个方法我回测下来，表现略好
    """
    # 14 days by default for the k time window
    k_window = 14

    dx = pd.DataFrame(df_main[['adjClose', 'adjLow', 'adjHigh']])
    dx['max14'] = df_main['adjHigh'].rolling(window=k_window).max()
    dx['min14'] = df_main['adjLow'].rolling(window=k_window).min()

    df_main['rsv'] = 100 * ((dx['adjClose'] - dx['min14']) /
                       (dx['max14'] - dx['min14']))
    df_main['kdj-k'] = df_main['rsv'].ewm(com=2, adjust=False).mean()
    df_main['kdj-d'] = df_main['kdj-k'].ewm(com=2, adjust=False).mean()
    df_main['kdj-j'] = 3 * df_main['kdj-k'] - 2 * df_main['kdj-d']
    return df_main


def run_once(sym, indicator_func):
    """
    执行一次回测
    """
    bot = fbot.botRunner(symbol=sym, start='2018-01-01')
    bot.add_indicator(indicator_func)
    bot.add_indicator(None, 'macd')
    bot.run(on_day_trade)
    print("win rate: %f" % bot.win_rate)
    print("capital return %f " % (bot.capital_return_rate * 100))
    print("capital: enter(%f) exit(%f) " % (bot.enter_capital, bot.exit_capital))


def compare_indicators(sym):
    """
    执行两次回测，分别基于不同的指标
    """
    print("******************")
    print("Run comperation test with :" + sym)
    print("indicator 1 :")
    run_once(sym, kdj_indicator)
    print("indicator 2 :")
    run_once(sym, kdj_indicator2)

compare_indicators('600519')
compare_indicators('600036')
compare_indicators('601318')
compare_indicators('000858')
compare_indicators('601012')
compare_indicators('000333')
compare_indicators('300059')
compare_indicators('601166')
compare_indicators('603259')
compare_indicators('002415')
