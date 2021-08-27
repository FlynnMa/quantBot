# %%

import matBot.matBot as mbot

state = 'none'


def on_day_trade(x, df):
    global state
    cur_price = df['adjClose'].iloc[x]
    macd = df['macd'].iloc[x]
    diff = df['macd_diff'].iloc[x]
    one_hand = cur_price * 100

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


bot = mbot.matBotRunner(symbol='601012', start='2020-01-01')
bot.add_indicator(macd_indicator)
bot.run(on_day_trade)
bot.plot_price_with_orders()

bot.plot_deals()

# %%
