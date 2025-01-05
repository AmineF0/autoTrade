import yfinance as yf
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout,SimpleRNN,BatchNormalization,GRU
from tensorflow.keras.optimizers import Adam
import datetime as dt
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
import pickle
import os
import json
import warnings

warnings.filterwarnings("ignore")


class StockPredictor:
    def __init__(self,stock_name='AAPL',interval="1h",period="2y",split_ratio=1,window_size=6):
        self.stock_name = stock_name
        self.split_ratio = split_ratio
        self.period = period
        self.interval = interval
        self.window_size = window_size
        self.data = yf.download(self.stock_name, period=self.period,interval=self.interval)
        self.data = self.data.dropna()
        self.data.columns = self.data.columns.droplevel(1) 
    
    def get_stock_data(self):
        stock_data = yf.download(self.stock_name, period=self.period,interval=self.interval)
        stock_data = stock_data.dropna()
        cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        stock_data.columns = cols
        return stock_data
    
    def window_data_univariate(self,data, window_size):
        X = []
        y = []
        
        for i in range(len(data) - window_size - 1):
            X.append(data[i:(i + window_size)])
            y.append(data[i + window_size])
        return np.array(X), np.array(y).reshape(-1, 1)
    
    def window_data_multivariate(self,data,close_data, window_size):
        X = []
        y = []
        
        for i in range(len(data) - window_size - 1):
            # Window includes all features
            X.append(data[i:(i + window_size), :])
            # Target is next day's closing price
            y.append(close_data[i + window_size])  # Closing price is first column
            
        return np.array(X), np.array(y).reshape(-1, 1)
    
    def build_lstm_model(self,X_train):
        model = Sequential([
            LSTM(units=128, 
            return_sequences=True, 
            input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2),
        
        LSTM(units=64),
        Dropout(0.2),
        
        Dense(32, activation='relu'),
        Dense(1)
        ])
        optimizer = Adam(learning_rate=0.01)
        model.compile(optimizer=optimizer, loss='mean_squared_error')
        return model
    
    def build_mlp_model(self):
        model_mlp = MLPRegressor(hidden_layer_sizes=(128, 64), max_iter=100, verbose=False)
        return model_mlp
    
    def get_current_price(self):
        stock_data = yf.download(self.stock_name, period='2y',interval='1h')
        return stock_data['Close'].to_numpy()[-1]
    
    def train_lstm_univariate(self):
        scaler = MinMaxScaler()
        data_close = self.data['Close']
        df_windowed,df_target = self.window_data_univariate(data_close.to_numpy().reshape(-1,1),self.window_size)
        df_windowed_reshaped = df_windowed.reshape(df_windowed.shape[0], -1)
        x_scaler = scaler.fit(df_windowed_reshaped)
        df_windowed_reshaped = x_scaler.transform(df_windowed_reshaped)
        df_windowed = df_windowed_reshaped.reshape(df_windowed.shape[0], df_windowed.shape[1], df_windowed.shape[2])
        y_scaler = scaler.fit(df_target)
        df_target = y_scaler.transform(df_target)
        train_size = int(self.split_ratio*len(df_windowed))
        X_train = df_windowed[:train_size]
        y_train = df_target[:train_size]
        X_test = df_windowed[train_size:]
        y_test = df_target[train_size:]
        model = self.build_lstm_model(X_train)
        model.fit(X_train, y_train, epochs=100,batch_size=32,    
            validation_split=0.1,
            verbose=0)

        model.save(f'models/{self.stock_name}/LSTM_univariate.h5')
     
    def train_lstm_multivariante(self):
        scaler = MinMaxScaler()
        data = self.data[['Close', 'High', 'Low', 'Volume']]
        data_close = self.data['Close']
        df_windowed,df_target = self.window_data_multivariate(data.to_numpy(),data_close.to_numpy().reshape(-1,1),self.window_size)
        df_windowed_reshaped = df_windowed.reshape(df_windowed.shape[0], -1)
        x_scaler = scaler.fit(df_windowed_reshaped)
        df_windowed_reshaped = x_scaler.transform(df_windowed_reshaped)
        df_windowed = df_windowed_reshaped.reshape(df_windowed.shape[0], df_windowed.shape[1], df_windowed.shape[2])
        y_scaler = scaler.fit(df_target)
        df_target = y_scaler.transform(df_target)
        train_size = int(self.split_ratio*len(df_windowed))
        X_train = df_windowed[:train_size]
        y_train = df_target[:train_size]
        X_test = df_windowed[train_size:]
        y_test = df_target[train_size:]
        model = self.build_lstm_model(X_train)
        model.fit(X_train, y_train, epochs=100,batch_size=32,    
            validation_split=0.1,
            verbose=0)

        model.save(f'models/{self.stock_name}/LSTM_multivariate.h5')   
        
    def train_mlp_univariante(self):
        scaler = MinMaxScaler()
        data_close = self.data['Close']
        df_windowed,df_target = self.window_data_univariate(data_close.to_numpy().reshape(-1,1),self.window_size)
        df_windowed_reshaped = df_windowed.reshape(df_windowed.shape[0], -1)
        x_scaler = scaler.fit(df_windowed_reshaped)
        df_windowed_reshaped = x_scaler.transform(df_windowed_reshaped)
        df_windowed = df_windowed_reshaped.reshape(df_windowed.shape[0], df_windowed.shape[1], df_windowed.shape[2])
        y_scaler = scaler.fit(df_target)
        df_target = y_scaler.transform(df_target)
        train_size = int(self.split_ratio*len(df_windowed))
        X_train = df_windowed[:train_size]
        y_train = df_target[:train_size]
        X_test = df_windowed[train_size:]
        y_test = df_target[train_size:]
        model = self.build_mlp_model()
        model.fit(X_train.reshape(X_train.shape[0],-1), y_train)
        output_dir = f'models/{self.stock_name}'
        os.makedirs(output_dir, exist_ok=True)
        with open(f'models/{self.stock_name}/MLP_univaraite.pkl', 'wb') as file:
            pickle.dump(model, file)
    
    def model_expiry(self):
        EXPIRY_CST = 2*60*60
        models = ["MLP_univaraite","LSTM_univariate","LSTM_multivariate"]
        # check if json file with name models_manager exist in models folder 
        if not os.path.exists(f'models/{self.stock_name}/models_manager.json'):
            return True
        with open(f'models/{self.stock_name}/models_manager.json', 'r') as file:
            data = json.load(file)
            for model in models:
                if model not in data:
                    return True
                else:
                    creation_date = data[model]['creation_date']
                    creation_date = dt.datetime.fromtimestamp(creation_date)
                    now = dt.datetime.now()
                    diff = (now - creation_date).total_seconds()
                    return diff > EXPIRY_CST
                
    
    def train(self, force: bool = False):
        
        # TODO : detect the expiry of the model using the json file, json create name path of the model
        # diff( now - created ) > cst train else skip
        # if force is True, train the model
        if force or self.model_expiry():
            self.train_lstm_univariate()
            self.train_lstm_multivariante()
            self.train_mlp_univariante()
            data = {
                    "MLP_univaraite":{
                        'path':f'models/{self.stock_name}/MLP_univaraite.pkl',
                        "creation_date":dt.datetime.now().timestamp()
                    },
                    "LSTM_univariate":{
                        'path':f'models/{self.stock_name}/LSTM_univariate.h5',
                        "creation_date":dt.datetime.now().timestamp()
                    },
                    "LSTM_multivariate":{
                        'path':f'models/{self.stock_name}/LSTM_multivariate.h5',
                        "creation_date":dt.datetime.now().timestamp()
                    }
                }
            with open(f'models/{self.stock_name}/models_manager.json', 'w') as file:
                json.dump(data, file)
            
    
    def forecast_lstm_univariante(self,n_hours:int=7):
        model_dir = f'models/{self.stock_name}/LSTM_univariate.h5'
        model = tf.keras.models.load_model(model_dir)
        forecast = []
        data_close = self.data['Close']
        df_windowed,df_target = self.window_data_univariate(data_close.to_numpy().reshape(-1,1),self.window_size)
        df_windowed_reshaped = df_windowed.reshape(df_windowed.shape[0], -1)
        x_scaler = MinMaxScaler()
        x_scaler.fit(df_windowed_reshaped)
        df_windowed_reshaped = x_scaler.transform(df_windowed_reshaped)
        df_windowed = df_windowed_reshaped.reshape(df_windowed.shape[0], df_windowed.shape[1], df_windowed.shape[2])
        y_scaler = MinMaxScaler()
        y_scaler.fit(df_target)
        df_target = y_scaler.transform(df_target)
        X = df_windowed[-1]
        for i in range(n_hours):
            X = X.reshape(1, X.shape[0], X.shape[1])
            y_pred = model.predict(X)
            forecast.append(y_pred)
            X = np.concatenate((X[0][1:], y_pred))
        return y_scaler.inverse_transform(np.array(forecast).reshape(-1, 1))
    
    def forecast_lstm_multivariante(self,n_hours:int=7):
        model_dir = f'models/{self.stock_name}/LSTM_multivariate.h5'
        model = tf.keras.models.load_model(model_dir)
        ## forecast for n hours
        forecast = []
        data = self.data[['Close', 'High', 'Low', 'Volume']]
        data_close = self.data['Close']
        df_windowed,df_target = self.window_data_multivariate(data.to_numpy(),data_close.to_numpy().reshape(-1,1),self.window_size)
        df_windowed_reshaped = df_windowed.reshape(df_windowed.shape[0], -1)
        x_scaler = MinMaxScaler()
        x_scaler.fit(df_windowed_reshaped)
        df_windowed_reshaped = x_scaler.transform(df_windowed_reshaped)
        df_windowed = df_windowed_reshaped.reshape(df_windowed.shape[0], df_windowed.shape[1], df_windowed.shape[2])
        y_scaler = MinMaxScaler()
        y_scaler.fit(df_target)
        df_target = y_scaler.transform(df_target)
        X = df_windowed[-1]
        for i in range(n_hours):
            X = X.reshape(1, X.shape[0], X.shape[1])
            y_pred = model.predict(X)
            forecast.append(y_pred)
            y_pred_expanded = X[-1].copy()  # Use the last timestep as a template
            y_pred_expanded[0] = y_pred[0, 0]  # Update the 'Close' feature with the prediction
            X = np.concatenate((X[0][1:], y_pred_expanded), axis=0)
        return y_scaler.inverse_transform(np.array(forecast).reshape(-1, 1))
    
    def forecast_mlp_univariate(self,n_hours):
        model_dir = f'models/{self.stock_name}/MLP_univaraite.pkl'
        with open(model_dir, 'rb') as file:
            model = pickle.load(file)
        data_close = self.data['Close']
        df_windowed,df_target = self.window_data_univariate(data_close.to_numpy().reshape(-1,1),self.window_size)
        df_windowed_reshaped = df_windowed.reshape(df_windowed.shape[0], -1)
        x_scaler = MinMaxScaler()
        x_scaler.fit(df_windowed_reshaped)
        df_windowed_reshaped = x_scaler.transform(df_windowed_reshaped)
        df_windowed = df_windowed_reshaped.reshape(df_windowed.shape[0], df_windowed.shape[1], df_windowed.shape[2])
        y_scaler = MinMaxScaler()
        y_scaler.fit(df_target)
        df_target = y_scaler.transform(df_target)
        X = df_windowed[-1]
        forecast = []
        for i in range(n_hours):
            y_pred = model.predict(X.reshape(1, -1)).reshape(-1, 1)
            forecast.append(y_pred)
            X = np.concatenate((X[1:], y_pred))
        return y_scaler.inverse_transform(np.array(forecast).reshape(-1, 1))
    
    
    def forecast_nhours(self,n_hours:int=7):
        return {
            'LSTM_univariate':self.forecast_lstm_univariante(n_hours),
            'LSTM_multivariate':self.forecast_lstm_multivariante(n_hours),
            'MLP_univariate':self.forecast_mlp_univariate(n_hours)
        }
    

        
        
            
            
