import flynnBot.flynnBot as fbot
import flynnBot.plots    as fplt
import pandas as pd
import math

state = 'none'

def on_day_trade(i, df):
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
    df['kdj-k'] = dx['rsv'].ewm(com=2, adjust=False).mean()
    df['kdj-d'] = df['kdj-k'].ewm(com=2, adjust=False).mean()
    df['kdj-j'] = 3 * df['kdj-k'] - 2 * df['kdj-d']
    return df


bot = fbot.botRunner(symbol='600036', start='2020-01-01')
bot.add_indicator(kdj_indicator)
bot.add_indicator(None, 'macd')

bot.run(on_day_trade)

fplt.plot_overview(bot.df, title="my kdj first try",
indicators=['kdj', 'macd'])

fplt.plot_profits(bot.profits_df)
