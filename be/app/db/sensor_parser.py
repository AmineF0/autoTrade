import pandas as pd
import os

def convert_df_type_to_sql_type(df_type):
    """Convert pandas data type to SQL data type"""
    """if string text , if number real"""
    if df_type == "object":
        return "TEXT"
    else:
        return "REAL"
        

def get_sensor_metadata():
    """Get sensor metadata"""
    print(os.getcwd())
    df = pd.read_excel("data/sensors.xlsx")
    df.fillna("", inplace=True)
    
    columns = df.columns
  
    columns_sql = [
      f"{column} {convert_df_type_to_sql_type(type)}" if column != "code " 
      else "code TEXT PRIMARY KEY UNIQUE NOT NULL"
      for column, type in zip(columns, df.dtypes)
    ]
    data = df.values.tolist()
        
    return columns_sql, data
  
get_sensor_metadata()