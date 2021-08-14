# MACD策略
MACD - moving average convergence divergence
是趋势和震荡的交易指标，


用2个EMA价格相减， 
EMA12 -  EMA26
EMA - exponential 
moving average， 
计算方法可以理解成， MA是EMA的一种特殊形式
MA的计算：

$$S_n = \dfrac{x_0 + x_1 + ... x_n} {n}$$


对它改变形式写成：
$$S_{n} = (1-\dfrac{1}{n})S_{n-1} + \dfrac{1}{n}x_{n}$$

设：$$\alpha = \dfrac{1}{n}$$ , 


进一步把$$S_n$$的计算写成： $$S_n = S_{n-1} + \alpha(x_n - S_{n-1})$$


这个公式就是EMA了
wiki里面也解释了为什么叫指数滑动平均
https://en.wikipedia.org/wiki/Exponential_smoothing


接下来的问题是:
设多少更好呢?
大多数情况是设置成2/n，由此增加最近几天的权重

# 交易策略
股票牛熊的判定：
• MACD在0以上的时候，认为是股票转牛
• MACD在1以下的时候，认为是股票转熊
判定交易的买入点和卖出点:
• 买入 = 信号向上交叉 
• 卖出 = 信号向下交叉
• 有时交叉时的信号速度也被作为参考指标
