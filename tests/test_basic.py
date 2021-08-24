

import matBot.matBot as mbot
print("basic test infrastructure")


def test_run():
    bot = mbot.matBotRunner()
    assert len(bot.df) != 0


def on_day_trade(x, df):
    pass


def macd_indicator(df):
    print("macd")
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


def test_run_set_start():
    print("set start time to 2020-01-01")
    bot = mbot.matBotRunner(start='2020-01-01')
    bot.add_indicator(macd_indicator)
    bot.run(on_day_trade)
    assert len(bot.df) != 0
