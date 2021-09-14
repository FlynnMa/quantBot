"""
macd算法和交易策略的基础实现
"""
# %%

import flynnBot.flynnBot as fbot
import flynnBot.plots as botplt

state = 'none'

def on_day_trade(i, df_main, holding_price):
    """
    买卖策略，决定这一天是否买入
    """
    global state

    diff = df_main['macd_diff'].iloc[i]

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


def macd_indicator(df):
    """
    macd指标的计算， 可以依据实际情况和回测结果调整时间窗口
    """
    # 26 days by default for long term ema
    ema_win_long = 26
    # 12 days by default for short term ema
    ema_win_short = 12
    ema_signal_win = 9

    df['ema_long'] = df['adjClose'].ewm(span=ema_win_long).mean()
    df['ema_short'] = df['adjClose'].ewm(span=ema_win_short).mean()
    df['macd'] = df['ema_short'] - df['ema_long']
    df['macd_signal'] = df['macd'].ewm(span=ema_signal_win).mean()
    df['macd_diff'] = df['macd'] - df['macd_signal']
    return df


bot = fbot.botRunner(symbol='000333', start='2021-01-01')
bot.add_indicator(macd_indicator)
bot.run(on_day_trade)

# %%
botplt.plot_overview(bot.df_main, indicators=['macd'])
botplt.plot_profits(bot.df_profits)

# %%
