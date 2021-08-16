#%%

import pandas_datareader as pdr
import matplotlib.pyplot as plt
import os

df = pdr.get_data_tiingo('002032', start='2020-01-01', end='2021-08-11', api_key=os.getenv('TIINGO_API_KEY'))
df.reset_index(level=0, inplace=True)
df.index = df.index.date

df['ma5'] = df['adjClose'].rolling(window=5).mean()
df['ma60'] = df['adjClose'].rolling(window=60).mean()

cash  = 10000
share = 0
buy_list = []
sell_list = []

# trading bot starts
for x in range(len(df)):
    cur_price = df['adjClose'].iloc[x]
    one_hand = cur_price * 100
    ma_short = df['ma5'].iloc[x]
    ma_long  = df['ma60'].iloc[x]

    # buy buy buy, ma_short > ma_long
    if (cash > one_hand) and (ma_short > ma_long):
        # buy signal comes
        buy_list.append(cur_price)
        sell_list.append(float('nan'))
        # action -> buy
        hands = int(cash / one_hand)
        cash = cash - hands * one_hand
        share = hands * 100
    # sell, sell, sell, ma_short < ma_long
    elif (share >= 100) and (ma_short < ma_long):
        # sell signal comes
        sell_list.append(cur_price)
        buy_list.append(float('nan'))
        # action -> sell
        cash = cash + share * cur_price
        share = 0
    else:
        # no signal
        sell_list.append(float('nan'))
        buy_list.append(float('nan'))

print(cash)
print(share)

df['buy'] = buy_list
df['sell'] = sell_list
plt.style.use('dark_background')
ax = plt.gca()

df['adjClose'].plot(ax=ax, figsize=(20,12), color='purple', label='price')
df['ma5'].plot(ax=ax, color='green', label='ma5')
df['ma60'].plot(ax=ax, color='yellow', label='ma60')
ax.scatter(df.index, y=df['buy'].values, label='buy', marker='^', s=70, color='red')
ax.scatter(df.index, y=df['sell'].values, label='sell', marker='x', s=70, color='#00ff00')
plt.legend(loc="upper right")

plt.show()