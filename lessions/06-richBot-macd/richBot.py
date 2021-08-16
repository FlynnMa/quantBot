#%%

import pandas_datareader as pdr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# stock symbol
stock_symbol  = '002032'

# get data
df = pdr.get_data_tiingo(stock_symbol, start='2020-01-01', end='2021-08-11', api_key=os.getenv('TIINGO_API_KEY'))
df.reset_index(level=0, inplace=True)
df.index = df.index.date

# 26 days by default for long term ema
ema_win_long = 26
# 12 days by default for short term ema
ema_win_short = 12
ema_signal_win = 9

df['ema_long'] = df['adjClose'].ewm(span=ema_win_long).mean()
df['ema_short'] = df['adjClose'].ewm(span=ema_win_short).mean()

df['macd'] = df['ema_short'] - df['ema_long']
df['macd_signal'] = df['macd'].ewm(span=ema_signal_win).mean()
df['macd_diff']   = df['macd'] - df['macd_signal']
#%%

cash  = 10000
share = 0
buy_list    = []
sell_list   = []
hold_price  = 0
stop_profit = 0.2
stop_loss   = 0.5
diff_list_buy   = []
diff_list_sell   = []
macd = 100
macd_old = 100

# trading bot starts
for x in range(len(df)):
    cur_price = df['adjClose'].iloc[x]
    one_hand = cur_price * 100
    macd = df['macd'].iloc[x]
    signal  = df['macd_signal'].iloc[x]
    diff    = df['macd_diff'].iloc[x]
 
    if (macd_old == 100):
        macd_old = macd
        sell_list.append(float('nan'))
        buy_list.append(float('nan'))
        continue
    # buy buy buy, macd > signal
    if (cash > one_hand) and (macd > signal):
        # if macd_old > macd, dont buy
        # if macd < 0, the stock is bear
        # if diff > 0.35, should not happen
        if ((macd < 0) or (diff > 0.2) or (macd_old > macd)):
            # no signal
            sell_list.append(float('nan'))
            buy_list.append(float('nan'))
            continue
        diff_list_buy.append(diff)
        # buy signal comes
        buy_list.append(cur_price)
        sell_list.append(float('nan'))
        # action -> buy
        hands = int(cash / one_hand)
        cash = cash - hands * one_hand
        share = hands * 100
    # sell, sell, sell, macd < signal
    elif (share >= 100) and (macd < signal):
        # sell signal comes
        diff_list_sell.append(diff)
        sell_list.append(cur_price)
        buy_list.append(float('nan'))
        # action -> sell
        cash = cash + share * cur_price
        share = 0
    else:
        # no signal
        sell_list.append(float('nan'))
        buy_list.append(float('nan'))
    # back up macd
    macd_old = macd

print(cash)
print(share)
print("last price{}".format(cur_price))
capital = cur_price * share + cash
print("capital" + str(capital))

df['buy'] = buy_list
df['sell'] = sell_list
buy_actions = df['buy'].dropna()
sell_actions = df['sell'].dropna()

plt.style.use('dark_background')
fig = plt.figure(figsize=(24, 20))
fig.suptitle('macd strategy', fontsize=60)

axs = fig.subplots(2)

df['adjClose'].plot(ax=axs[0], color='purple', label='price', rot=90, grid=True)
df['ema_short'].plot(ax=axs[0], color='yellow', label='price', rot=90, grid=True)

axs[0].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
axs[0].xaxis.set_major_locator(mdates.DayLocator(interval=5))
axs[0].vlines(x=buy_actions.index, ymin=0, ymax=buy_actions.values,color='red', linestyle='--')
axs[0].vlines(x=sell_actions.index, ymin=0, ymax=sell_actions.values,color='green', linestyle='--')
axs[0].scatter(df.index, y=df['buy'].values, label='buy', marker='^', s=70, color='red')
axs[0].scatter(df.index, y=df['sell'].values, label='sell', marker='x', s=70, color='#00ff00')

df['macd'].plot(ax=axs[1], color='green', label='macd', grid=True)
df['macd_signal'].plot(ax=axs[1], color='yellow', label='signal')
axs[1].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
axs[1].xaxis.set_major_locator(mdates.DayLocator(interval=5))
axs[1].axhline(y=0, linestyle='--', color='gray');
axs[1].vlines(x=buy_actions.index, ymin=-1, ymax=1,color='red', linestyle='--')
axs[1].vlines(x=sell_actions.index, ymin=-1, ymax=1,color='green', linestyle='--')
plt.legend(loc="upper right")

plt.show()

# %%
td = buy_actions.reset_index().drop('index',  axis='columns')
td['sell'] = sell_actions.reset_index().drop('index', axis='columns')
color_dict = {'buy':'red', 'sell': 'green'}
td.plot(kind='bar', color=color_dict, title='trade actions', figsize=(12,8))
# %%
