# 比较两种kdj算法的不同

import flynnBot.flynnBot as fbot
import flynnBot.plots    as fplt
import pandas as pd
import math

state = 'none'

def on_day_trade(i, df, holding_price):
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

def kdj_indicator(df):
    # 14 days by default for the k time window
    k_window = 14

    dx = pd.DataFrame(df[['adjClose', 'adjLow', 'adjHigh']])
    dx['max14'] = df['adjHigh'].rolling(window=k_window).max()
    dx['min14'] = df['adjLow'].rolling(window=k_window).min()

    df['kdj-k'] = 100 * ((dx['adjClose'] - dx['min14']) /
                         (dx['max14'] - dx['min14']))
    df['kdj-d'] = df['kdj-k'].ewm(com=2, adjust=False).mean()
    df['kdj-j'] = 3 * df['kdj-k'] - 2 * df['kdj-d']
    return df


def kdj_indicator2(df):
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
    return df


def run_once(sym, indicator_func):
    bot = fbot.botRunner(symbol=sym, start='2018-01-01')
    bot.add_indicator(indicator_func)
    bot.add_indicator(None, 'macd')
    bot.run(on_day_trade)
    print("win rate: %f" % bot.win_rate)
    print("capital return %f " % (bot.capital_return_rate * 100))
    print("capital: enter(%f) exit(%f) " % (bot.enter_capital, bot.exit_capital))

def compare_indicators(sym):
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

