"""
单元测试， pytest调用
"""

import flynnBot.flynnBot as fbot
import flynnBot.plots as botplt
print("basic test infrastructure")


def test_run():
    bot = fbot.botRunner()
    assert len(bot.df_main) != 0


def on_day_trade(i, df_main, price):
    pass


def macd_indicator(df_main):
    print("macd")
    # 26 days by default for long term ema
    ema_win_long = 26
    # 12 days by default for short term ema
    ema_win_short = 12
    ema_signal_win = 9

    df_main['ema_long'] = df_main['adjClose'].ewm(span=ema_win_long).mean()
    df_main['ema_short'] = df_main['adjClose'].ewm(span=ema_win_short).mean()
    df_main['macd'] = df_main['ema_short'] - df_main['ema_long']
    df_main['macd_signal'] = df_main['macd'].ewm(span=ema_signal_win).mean()
    df_main['macd_diff'] = df_main['macd'] - df_main['macd_signal']
    return df_main


def test_run_set_start():
    print("set start time to 2020-01-01")
    bot = fbot.botRunner(start='2020-01-01')
    bot.add_indicator(macd_indicator)
    bot.run(on_day_trade)
    botplt.plot_overview(bot.df_main, ['macd'])
    assert len(bot.df_main) != 0


def test_built_in_indicators():
    print("test built in indicators")
    bot = fbot.botRunner(symbol='601012')
    bot.add_indicator(None, built_in='macd')
