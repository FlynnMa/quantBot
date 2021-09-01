import matBot.matBot as mbot
import pandas as pd

def kdj_indicator(df):
    # 14 days by default for the k time window
    k_window = 14

    dx = pd.DataFrame(df[['adjClose', 'adjLow', 'adjHigh']])
    dx['max14'] = df['adjHigh'].rolling(window=k_window).max()
    dx['min14'] = df['adjLow'].rolling(window=k_window).min()
    
    df['kdj-k'] = 100 * ((dx['adjClose'] - dx['min14']) / (dx['max14'] - dx['min14']))
    df['kdj-d'] = df['kdj-k'].ewm(com=2, adjust=False).mean()
    return df

def kdj_indicator2(df):
    # 14 days by default for the k time window
    k_window = 14

    dx = pd.DataFrame(df[['adjClose', 'adjLow', 'adjHigh']])
    dx['max14'] = df['adjHigh'].rolling(window=k_window).max()
    dx['min14'] = df['adjLow'].rolling(window=k_window).min()
    
    df['rsv'] = 100 * ((dx['adjClose'] - dx['min14']) / (dx['max14'] - dx['min14']))
    df['kdj-k'] = dx['rsv'].ewm(com=2, adjust=False).mean()
    df['kdj-d'] = df['kdj-k'].ewm(com=2, adjust=False).mean()
    return df


bot = mbot.matBotRunner(symbol='002032', start='2019-01-01')
bot.add_indicator(kdj_indicator)

