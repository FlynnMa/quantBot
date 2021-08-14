# 环境配置

```
python3.9
matplotlib
pandas
pandas_datareader

visual studio code + python插件， jupyter插件
jupyter
```

# 数据

来源于 tiingo.com
注册免费账号，登录以后，在自己的个人账号下面获取API_KEY

然后把你的密钥加到环境变量里面，也可以直接写在代码里
添加环境变量可以把下面的命令加到`.bashrc`
```
export TIINGO_API_KEY='你的API KEY'
```

接口的调用
```
df = pdr.get_data_tiingo('601398', 
    start='2021-01-01',
    end='2021-08-05',
    api_key=os.getenv('TIINGO_API_KEY'))
```

绘制价格走势图:
```
fig = plt.figure(figsize=(20, 12))
fig.suptitle("volume plotting")
df['adjClose'].plot(rot=90, grid=True)
fig.savefig("volume.png")
```


# 交易机器人
初始的现金 - 通过`cash`变量配置
初步的持股数 - 通过`share`变量配置


# 交易策略
待完善
