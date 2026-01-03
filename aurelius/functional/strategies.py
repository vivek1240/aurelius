"""
Custom Trading Strategies for Backtesting
These strategies can be used with BackTraderUtils.back_test()
"""

import backtrader as bt


class RSI_Strategy(bt.Strategy):
    """
    RSI Overbought/Oversold Strategy
    
    - Buy when RSI drops below oversold level (default 30)
    - Sell when RSI rises above overbought level (default 70)
    """
    params = (
        ('period', 14),       # RSI period
        ('oversold', 30),     # Buy signal threshold
        ('overbought', 70),   # Sell signal threshold
    )
    
    def __init__(self):
        self.rsi = bt.indicators.RSI(
            self.data.close,
            period=self.p.period
        )
        self.order = None
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print(f'{dt.isoformat()} {txt}')  # Uncomment for debugging
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        if not self.position:
            # Not in market - look for buy signal
            if self.rsi < self.p.oversold:
                self.log(f'RSI oversold ({self.rsi[0]:.1f}), BUY CREATE')
                self.order = self.buy()
        else:
            # In market - look for sell signal
            if self.rsi > self.p.overbought:
                self.log(f'RSI overbought ({self.rsi[0]:.1f}), SELL CREATE')
                self.order = self.sell()


class MACD_Strategy(bt.Strategy):
    """
    MACD Crossover Strategy
    
    - Buy when MACD line crosses above the signal line
    - Sell when MACD line crosses below the signal line
    """
    params = (
        ('fast_period', 12),    # Fast EMA period
        ('slow_period', 26),    # Slow EMA period
        ('signal_period', 9),   # Signal line period
    )
    
    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.fast_period,
            period_me2=self.p.slow_period,
            period_signal=self.p.signal_period
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.order = None
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print(f'{dt.isoformat()} {txt}')  # Uncomment for debugging
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        if not self.position:
            # Not in market - look for bullish crossover
            if self.crossover > 0:
                self.log('MACD bullish crossover, BUY CREATE')
                self.order = self.buy()
        else:
            # In market - look for bearish crossover
            if self.crossover < 0:
                self.log('MACD bearish crossover, SELL CREATE')
                self.order = self.sell()


class BollingerBands_Strategy(bt.Strategy):
    """
    Bollinger Bands Mean Reversion Strategy
    
    - Buy when price touches or goes below the lower band
    - Sell when price touches or goes above the upper band
    """
    params = (
        ('period', 20),       # Moving average period
        ('devfactor', 2.0),   # Standard deviation multiplier
    )
    
    def __init__(self):
        self.boll = bt.indicators.BollingerBands(
            self.data.close,
            period=self.p.period,
            devfactor=self.p.devfactor
        )
        self.order = None
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print(f'{dt.isoformat()} {txt}')  # Uncomment for debugging
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        if not self.position:
            # Not in market - buy when price touches lower band
            if self.data.close[0] <= self.boll.lines.bot[0]:
                self.log(f'Price at lower band, BUY CREATE')
                self.order = self.buy()
        else:
            # In market - sell when price touches upper band
            if self.data.close[0] >= self.boll.lines.top[0]:
                self.log(f'Price at upper band, SELL CREATE')
                self.order = self.sell()


class MovingAverageRibbon_Strategy(bt.Strategy):
    """
    Moving Average Ribbon Strategy
    
    Uses multiple EMAs (10, 20, 50, 100) to determine trend
    - Buy when all EMAs are stacked bullishly (shortest on top)
    - Sell when EMAs start to compress or invert
    """
    params = (
        ('ema_periods', [10, 20, 50, 100]),
    )
    
    def __init__(self):
        self.emas = []
        for period in self.p.ema_periods:
            self.emas.append(bt.indicators.EMA(self.data.close, period=period))
        self.order = None
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print(f'{dt.isoformat()} {txt}')  # Uncomment for debugging
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
        self.order = None
    
    def is_bullish_stack(self):
        """Check if EMAs are in bullish order (shortest > longest)"""
        for i in range(len(self.emas) - 1):
            if self.emas[i][0] <= self.emas[i + 1][0]:
                return False
        return True
    
    def is_bearish_signal(self):
        """Check if shortest EMA crosses below second shortest"""
        return self.emas[0][0] < self.emas[1][0]
    
    def next(self):
        if self.order:
            return
        
        if not self.position:
            if self.is_bullish_stack():
                self.log('Bullish EMA ribbon, BUY CREATE')
                self.order = self.buy()
        else:
            if self.is_bearish_signal():
                self.log('EMA ribbon breaking down, SELL CREATE')
                self.order = self.sell()


# Strategy registry for easy access
STRATEGY_REGISTRY = {
    'SMA_CrossOver': 'SMA_CrossOver',  # Built-in backtrader strategy
    'RSI': 'aurelius.functional.strategies:RSI_Strategy',
    'MACD': 'aurelius.functional.strategies:MACD_Strategy',
    'BollingerBands': 'aurelius.functional.strategies:BollingerBands_Strategy',
    'MA_Ribbon': 'aurelius.functional.strategies:MovingAverageRibbon_Strategy',
}

# Strategy descriptions for UI
STRATEGY_INFO = {
    'SMA_CrossOver': {
        'name': 'SMA Crossover',
        'description': 'Classic dual moving average crossover. Buy when fast MA crosses above slow MA.',
        'params': {'fast': 10, 'slow': 30},
        'param_labels': {'fast': 'Fast MA Period', 'slow': 'Slow MA Period'}
    },
    'RSI': {
        'name': 'RSI Overbought/Oversold',
        'description': 'Buy when RSI drops below oversold level, sell when above overbought level.',
        'params': {'period': 14, 'oversold': 30, 'overbought': 70},
        'param_labels': {'period': 'RSI Period', 'oversold': 'Oversold Level', 'overbought': 'Overbought Level'}
    },
    'MACD': {
        'name': 'MACD Crossover',
        'description': 'Trade MACD and signal line crossovers. Buy on bullish cross, sell on bearish.',
        'params': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
        'param_labels': {'fast_period': 'Fast EMA', 'slow_period': 'Slow EMA', 'signal_period': 'Signal Period'}
    },
    'BollingerBands': {
        'name': 'Bollinger Bands',
        'description': 'Mean reversion strategy. Buy at lower band, sell at upper band.',
        'params': {'period': 20, 'devfactor': 2.0},
        'param_labels': {'period': 'MA Period', 'devfactor': 'Std Dev Factor'}
    },
    'MA_Ribbon': {
        'name': 'MA Ribbon',
        'description': 'Trend following using multiple EMAs. Buy when EMAs are bullishly stacked.',
        'params': {},
        'param_labels': {}
    }
}

