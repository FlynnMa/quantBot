import pandas as pd


def macd(df, win_long=26, win_short=12, win_signal=9):

    df['ema_long'] = df['adjClose'].ewm(span=win_long).mean()
    df['ema_short'] = df['adjClose'].ewm(span=win_short).mean()
    df['macd'] = df['ema_short'] - df['ema_long']
    df['macd_signal'] = df['macd'].ewm(span=win_signal).mean()
    df['macd_diff'] = df['macd'] - df['macd_signal']
    return df
