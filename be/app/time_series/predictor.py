from .stock_predictor import StockPredictor

class Predictor:
    def __init__(self,interval="1h",period="2y",stocks=['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']):
        self.stocks = stocks
        self.predictors = {}
        for stock in stocks:
            self.predictors[stock] = StockPredictor(stock_name=stock,interval=interval,period=period)
        
    def train(self, force=False):
        for stock in self.predictors.values():
            stock.train(force)
    
    def forecast_nhours(self,n_hours:int=7):
        forecast = {}
        for stock in self.predictors.values():
            forecast[stock.stock_name] = stock.forecast_nhours(n_hours)
        return forecast
    
    def get_current_prices(self):
        prices = {}
        for stock in self.predictors.values():
            prices[stock.stock_name] = stock.get_current_price()
        return prices
    