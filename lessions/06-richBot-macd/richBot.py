# %%

import pandas_datareader as pdr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import numpy as np
import matplotlib as mpl
import pandas as pd

mpl.rcParams['grid.color'] = 'gray'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linewidth'] = 0.1

# stock symbol
stock_symbol = '002594'
# stock_symbol = '601398'

cash = 1000000


# get data
df = pdr.get_data_tiingo(stock_symbol, start='2020-08-18', end='2021-08-18')
df.reset_index(level=0, inplace=True)
df.index = df.index.date
# %%

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
# %%
share = 0
buy_list = []
sell_list = []
hold_price = 0
diff_list_buy = []
diff_list_sell = []
macd = 100
macd_old = 100

state = 'none'
# trading bot starts
for x in range(len(df)):
    cur_price = df['adjClose'].iloc[x]
    one_hand = cur_price * 100
    macd = df['macd'].iloc[x]
    # signal  = df['macd_signal'].iloc[x]
    diff = df['macd_diff'].iloc[x]
    action = 'none'

    if state == 'none':
        if diff > 0:
            state = 'crossup'
        elif diff < 0:
            state = 'crossdown'
        else:
            action = 'none'
    elif state == 'crossup':
        if diff < 0:
            action = 'sell'
            state = 'crossdown'
    elif state == 'crossdown':
        if diff > 0:
            action = 'buy'
            state = 'crossup'

    if (action == 'buy') and (cash > one_hand):
        buy_list.append(cur_price)
        sell_list.append(np.nan)
        # action -> buy
        hands = int(cash / one_hand)
        cash = cash - hands * one_hand
        share = hands * 100
    elif (action == 'sell') and (share >= 100):
        buy_list.append(np.nan)
        sell_list.append(cur_price)
        # action -> sell
        cash = cash + share * cur_price
        share = 0
    else:
        sell_list.append(float('nan'))
        buy_list.append(float('nan'))

print("simulation completed:")
print(cash)
print(share)
capital = cur_price * share + cash
print("capital: " + str(capital))

df['buy'] = buy_list
df['sell'] = sell_list

buy_actions = df['buy'].dropna()
sell_actions = df['sell'].dropna()

plt.style.use('dark_background')
fig = plt.figure(figsize=(12, 8))
fig.suptitle('macd strategy', fontsize=60)
axs = fig.subplots(2)

df['adjClose'].plot(ax=axs[0], color='purple',
                    label='price', rot=90, grid=True)
df['ema_long'].plot(ax=axs[0], color='yellow',
                    label='price', rot=90, grid=True)

axs[0].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
axs[0].xaxis.set_major_locator(mdates.DayLocator(interval=5))
axs[0].vlines(x=buy_actions.index, ymin=0,
              ymax=buy_actions.values, color='red', linestyle='--')
axs[0].vlines(x=sell_actions.index, ymin=0,
              ymax=sell_actions.values, color='green', linestyle='--')
axs[0].scatter(df.index, y=df['buy'].values, label='buy',
               marker='^', s=70, color='red')
axs[0].scatter(df.index, y=df['sell'].values, label='sell',
               marker='x', s=70, color='#00ff00')

df['macd'].plot(ax=axs[1], color='green', label='macd', grid=True)
df['macd_signal'].plot(ax=axs[1], color='yellow', label='signal')
axs[1].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
axs[1].xaxis.set_major_locator(mdates.DayLocator(interval=5))
axs[1].axhline(y=0, linestyle='--', color='gray')
axs[1].vlines(x=buy_actions.index, ymin=-1,
              ymax=1, color='red', linestyle='--')
axs[1].vlines(x=sell_actions.index, ymin=-1,
              ymax=1, color='green', linestyle='--')
plt.legend(loc="upper right")
plt.show()

# %%
fig = plt.figure(figsize=(12, 8))
fig.suptitle('macd buy and sell actions', fontsize=60)
axs = fig.subplots(2)

buy_df = buy_actions.reset_index()
buy_df.rename(columns={'index': 'buyDate'}, inplace=True)
sell_df = sell_actions.reset_index()
sell_df.rename(columns={'index': 'sellDate'}, inplace=True)
deal_df = pd.concat([buy_df, sell_df], axis=1)

if (len(deal_df) == 0):
    print("no deal!")
    exit()
color_dict = {'buy': 'red', 'sell': 'green'}
df2 = deal_df.loc[:, ['buy', 'sell']]
df2.plot(ax=axs[0], kind='bar', color=color_dict, rot=90)

# profit
deal_df['profits'] = deal_df['sell'] - deal_df['buy']
colors = np.where(deal_df['profits'].values > 0, 'r', 'g')
deal_df['profits'].plot(
    ax=axs[1], kind='bar', color=colors, title='profit')
plt.show()
# %%
