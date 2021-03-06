# 源码地址

### github
https://github.com/FlynnMa/quantBot

### coding.net
https://flynnbot.coding.net/public/quantBot/quantBot/git

### gitee
https://gitee.com/flynnma/quantBot

# 环境配置

```
python3.9
matplotlib
pandas
pandas_datareader

visual studio code + python插件， jupyter插件
or 
jupyter
```

安装python3
```
https://www.python.org/downloads/
```

# 数据

目前的数据采用的是 tiingo.com免费提供的

获取数据需要注册免费账号，登录以后，在自己的个人账号下面获取API_KEY


然后把你的密钥加到环境变量里面，也可以直接写在代码里

添加密钥到环境变量可以把下面的命令加到`.bashrc`
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
06-macd-strategy - 基于MACD的交易策略

# 开发者

### 单元测试

```
python3 setup.py pytest
or
pytest -s
```

### 编译

```
python3 setup.py clean --all
python3 setup.py bdist_wheel
```

### 卸载和安装flynnBot机器人
```
python3 -m pip uninstall -y flynnBot
python3 -m pip install dist/flynnBot-0.1.1-py3-none-any.whl
```

```
python3 setup.py install
```

# 沪深300官网
http://www.csindex.com.cn/zh-CN/indices/index-detail/000300

