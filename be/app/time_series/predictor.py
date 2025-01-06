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
        Format the forecast into a readable string
        
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
        # 'AMZN : \npredictions for the next 7 hours : \nLSTM_univariate : [[232.08105]\n [237.24577]\n [244.15498]\n [251.0774 ]\n [258.96402]\n [266.0733 ]\n [273.50748]] \nMLP_univariate : [[222.33342978]\n [222.71979856]\n [222.68575272]\n [222.56617873]\n [222.54705575]\n [222.56909688]\n [222.01883164]] \npredictions for the next 7 days : \nLSTM_univariate : [[210.34221]\n [205.47612]\n [201.10594]\n [197.62225]\n [194.81113]\n [192.42444]\n [190.49016]] \nMLP_univariate : [[219.84931349]\n [220.15168382]\n [219.16382389]\n [218.13496411]\n [217.02456397]\n [215.94548122]\n [215.5865886 ]] \nMSFT : \npredictions for the next 7 hours : \nLSTM_univariate : [[409.86978]\n [400.50565]\n [393.8884 ]\n [388.7388 ]\n [383.6092 ]\n [378.67697]\n [374.08197]] \nMLP_univariate : [[420.93655296]\n [420.5442382 ]\n [420.34943544]\n [421.11971811]\n [420.87264373]\n [419.87004381]\n [419.45636687]] \npredictions for the next 7 days : \nLSTM_univariate : [[427.4569 ]\n [428.545  ]\n [431.21588]\n [433.5865 ]\n [435.6593 ]\n [437.69772]\n [439.63876]] \nMLP_univariate : [[428.45823775]\n [426.02605841]\n [425.10158646]\n [424.73960604]\n [424.68396656]\n [424.09870004]\n [423.93232838]] \nTSLA : \npredictions for the next 7 hours : \nLSTM_univariate : [[375.88535]\n [364.5968 ]\n [358.27118]\n [351.30838]\n [343.31238]\n [337.6101 ]\n [331.52982]] \nMLP_univariate : [[393.8111922 ]\n [397.16174167]\n [400.79210893]\n [400.08323526]\n [401.19053152]\n [403.62001557]\n [401.44726034]] \npredictions for the next 7 days : \nLSTM_univariate : [[331.3228 ]\n [291.29153]\n [271.21866]\n [260.93265]\n [247.86792]\n [240.3842 ]\n [235.24564]] \nMLP_univariate : [[439.06740289]\n [439.10393466]\n [432.63383035]\n [425.16939226]\n [425.22912083]\n [433.24019423]\n [435.10123965]] \nNVDA : \npredictions for the next 7 hours : \nLSTM_univariate : [[125.46644 ]\n [114.9842  ]\n [107.36872 ]\n [ 99.583275]\n [ 93.55011 ]\n [ 88.394295]\n [ 83.82294 ]] \nMLP_univariate : [[142.80983522]\n [143.6511586 ]\n [143.76391177]\n [144.07591   ]\n [144.55494225]\n [144.21061533]\n [144.05228733]] \npredictions for the next 7 days : \nLSTM_univariate : [[133.74496]\n [132.7733 ]\n [132.10107]\n [131.58794]\n [131.11057]\n [130.69781]\n [130.34663]] \nMLP_univariate : [[138.48776858]\n [137.66448749]\n [137.00579854]\n [136.87360495]\n [137.04094584]\n [137.25226054]\n [137.21530455]] \n'
        # clean this
        
        formatted_forecast = ""
        for stock_name, data in forecast.items():
            formatted_forecast += "\n\n"+ f"{stock_name} : "+"\n"
            for interval, all_predictions in data.items():
                formatted_forecast += f" Predictions for the next {n_instances_hour} hours : "+"\n" if interval == Constants.HOUR else f" Predictions for the next {n_instances_day} days : "+"\n"
                for model, model_predictions in all_predictions.items():
                    formatted_model_predictions = " ".join([str(prediction[0]) for prediction in model_predictions])
                    formatted_forecast += f"{model} : {formatted_model_predictions} "+"\n"
        
        return formatted_forecast
    
    def forcast_and_format(self,n_instances_hour:int=7, n_instances_day:int=7):
        forecast = self.forecast(n_instances_hour, n_instances_day)
        return self.format_forcast(forecast, n_instances_hour, n_instances_day)
    
    def data_and_forcast(self, n_instances_hour:int=7, n_instances_day:int=7):
        data = {}
        for stock in self.predictors.values():
            data[stock[Constants.HOUR].stock_name] = {}
            data[stock[Constants.HOUR].stock_name][Constants.HOUR] = stock[Constants.HOUR].data_and_forcast()
            data[stock[Constants.HOUR].stock_name][Constants.DAY] = stock[Constants.DAY].data_and_forcast()
        return parse_dict_with_numpy_recursive(data)
    
import numpy as np
def parse_dict_with_numpy_recursive(d):
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = parse_dict_with_numpy_recursive(v)
        elif isinstance(v, np.generic):
            d[k] = np.asscalar(v)
        elif isinstance(v, np.ndarray):
            d[k] = v.tolist()
    return d