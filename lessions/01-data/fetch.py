import os
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader as pdr


df = pdr.get_data_tiingo('601398', start='2021-01-01', end='2021-08-05', api_key=os.getenv('TIINGO_API_KEY'))


fig = plt.figure(figsize=(20, 12))
fig.suptitle("price plotting")
df['adjClose'].plot(rot=90, grid=True)
fig.savefig("price.png")

