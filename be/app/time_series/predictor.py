from .stock_predictor import StockPredictor


class Constants:
    DAY= "1d"
    HOUR= "1h"
class Predictor:
    def __init__(self,interval="1h",period="2y",stocks=['AMZN', 'MSFT', 'TSLA', 'NVDA']):
        self.stocks = stocks
        self.predictors = {}
        for stock in stocks:
            self.predictors[stock] = {}
            self.predictors[stock][Constants.HOUR] = StockPredictor(stock_name=stock,interval=Constants.HOUR,period=period)
            self.predictors[stock][Constants.DAY] = StockPredictor(stock_name=stock,interval=Constants.DAY,period=period)
        
    def train(self, force=False):
        for stock in self.predictors.values():
            stock[Constants.HOUR].train(force)
            stock[Constants.DAY].train(force)
    
    def forecast(self,n_instances_hour:int=24, n_instances_day:int=7):
        forecast = {}
        
        for stock in self.predictors.values():
            forecast[stock[Constants.HOUR].stock_name] = {}
            forecast[stock[Constants.HOUR].stock_name][Constants.HOUR] = stock[Constants.HOUR].forecast(n_instances_hour)
            forecast[stock[Constants.HOUR].stock_name][Constants.DAY] = stock[Constants.DAY].forecast(n_instances_day)
        
        return forecast
    
    def get_current_prices(self):
        prices = {}
        for stock in self.predictors.values():
            prices[stock[Constants.HOUR].stock_name] = stock[Constants.HOUR].get_current_price()
        return prices
    
    def format_forcast(self, forecast, n_instances_hour:int=24, n_instances_day:int=7):
        """

        Args:
            forecast (dict): a dictionary containing the forecast for each stock

        Returns:
            str: a summary of the forecast
                STOCK NAME : X
                    predictions for the next 24 hours :
                        model1 : predictions
                        model2 : predictions
                        ...
                    predictions for the next 7 days :
                        model1 : predictions
                        model2 : predictions
                        ...
        """
        
        formatted_forecast = ""
        for stock in forecast.values():
            formatted_forecast += f"{stock.stock_name} : \n"
            for interval, all_predictions in stock.items():
                formatted_forecast += f"predictions for the next {n_instances_hour} hours : \n" if interval == Constants.HOUR else f"predictions for the next {n_instances_day} days : \n"
                for model, model_predictions in all_predictions.items():
                    formatted_forecast += f"{model} : {model_predictions} \n"
        
        return forecast
    
    def forcast_and_format(self,n_instances_hour:int=7, n_instances_day:int=7):
        forecast = self.forecast(n_instances_hour, n_instances_day)
        return self.format_forcast(forecast, n_instances_hour, n_instances_day)