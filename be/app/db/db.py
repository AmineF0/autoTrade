import sqlite3
from db.sensor_parser import get_sensor_metadata
import logging
from db.data_gen import get_initial_record, get_next_record
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, Union


db_name = 'data/db.sqlite3'

class DB:
  def __init__(self):
    # create db if it doesn't
    
    self.conn = sqlite3.connect(db_name)
    self.cursor = self.conn.cursor()
    
    logging.info("DB connection established")
    
    self.cursor.execute("DROP TABLE IF EXISTS sensors_metadata")
    
    try:
      self.cursor.execute("SELECT * FROM sensors_metadata")
      logging.info("Table sensors_metadata exists")
    except sqlite3.OperationalError:
      logging.info("Table sensors_metadata doesn't exist")
      self.create_sensors_metadata()
      self.create_sensor_data_table(self.get_sensor_codes())
    
  def create_sensors_metadata(self):
    columns_sql, data = get_sensor_metadata()
    
    logging.info("Creating sensors_metadata table")
    logging.info(columns_sql)
    
    self.cursor.execute("CREATE TABLE sensors_metadata (" + ", ".join(columns_sql) + ")")
    
    for record in data:
      formatted_values = [
          f"'{r}'" if isinstance(r, str) else str(r) for r in record
      ]
      sql = "INSERT INTO sensors_metadata VALUES (" + ", ".join(formatted_values) + ")"

      self.cursor.execute(sql)  
        
    self.conn.commit()
    
  def get_sensor_codes(self):
    self.cursor.execute("SELECT code FROM sensors_metadata")
    codes = self.cursor.fetchall()
    return [code[0] for code in codes]
    
  def create_sensor_data_table(self, codes):
    self.cursor.execute("DROP TABLE IF EXISTS sensor_data")
    
    logging.info("Creating sensor_data table")
    logging.info(codes)
    
    columns_sql = [
        f"'{code}' REAL" for code in codes
    ]

    
    self.cursor.execute("CREATE TABLE sensor_data (timestamp TEXT PRIMARY KEY UNIQUE NOT NULL, " + ", ".join(columns_sql) + ")")
    
    self.conn.commit()
    
  def analyse_sensor_compliance(self, query):
    compliance_query_template = """
      SELECT 
        m.code, 
        m.name, 
        m.lower, 
        m.upper, 
        AVG(d.[{code}]) as avg_value,
        MIN(d.[{code}]) as min_value,
        MAX(d.[{code}]) as max_value,
        CASE 
          WHEN AVG(d.[{code}]) < m.lower OR AVG(d.[{code}]) > m.upper THEN 'Non-Compliant'
          ELSE 'Compliant'
        END as compliance_status
      FROM 
        sensors_metadata m
        JOIN sensor_data d ON 1=1
      WHERE 
        d.timestamp = (
          SELECT timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 1
        ) AND m.code = '{code}'
      GROUP BY m.code
    """
    
    try:
      sensor_codes = self.get_sensor_codes()
      compliance_query = "\nUNION ALL\n".join(
          [compliance_query_template.format(code=code) for code in sensor_codes]
      )
      self.cursor.execute(compliance_query)
      records = self.cursor.fetchall()
      
      column_names = [desc[0] for desc in self.cursor.description]
      
      return [dict(zip(column_names, record)) for record in records]
    except sqlite3.Error as e:
      logging.error(f"Error analysing sensor compliance: {e}")
      return []

  def add_record(self):
    
    timestamp = datetime.now().isoformat()
    codes = self.get_sensor_codes()
    last_record = self.get_last_record()
    
    if last_record is None:
      record = get_initial_record(codes)
    else:
      record = get_next_record(codes, last_record)
    
    formatted_columns = [
        f"'{code}'" for code in codes
    ]
    
    formatted_values = [
        f"'{record[code]}'" if isinstance(record[code], str) else str(record[code]) for code in codes
    ]
    
    sql = f"INSERT INTO sensor_data (timestamp, {", ".join(formatted_columns)}) VALUES ('{timestamp}', {", ".join(formatted_values)} )"
    
    # keep only the last 1000 records and delete the rest
    self.cursor.execute("SELECT COUNT(*) FROM sensor_data")
    count = self.cursor.fetchone()[0]
    
    if count >= 1000:
      self.cursor.execute("DELETE FROM sensor_data WHERE timestamp NOT IN (SELECT timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 1000)")
    
    self.cursor.execute(sql)
    self.conn.commit()
  
  def get_last_record(self):
    self.cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
    record = self.cursor.fetchone()
    
    if record:
        column_names = [desc[0] for desc in self.cursor.description]
        row_dict = dict(zip(column_names, record))
        return row_dict
    
    return record
  
  def get_records_in_timeframe(self, start: str, end: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve sensor data records within a specific timeframe.

        :param start: Start timestamp in ISO format.
        :param end: End timestamp in ISO format. Defaults to current time if None.
        :return: List of dictionaries containing sensor data records.
        """
        try:
            if end is None:
                end = datetime.now().isoformat()
            query = """
                SELECT * FROM sensor_data 
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp DESC
            """
            self.cursor.execute(query, (start, end))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error fetching records from {start} to {end}: {e}")
            return []

  def get_records_by_sensors(
        self,
        sensor_codes: Union[str, List[str]],
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
        order: str = "DESC",
    ) -> List[Dict[str, Any]]:
        """
        Retrieve sensor data records for specific sensor(s), optionally within a timeframe.

        :param sensor_codes: Single sensor code or list of sensor codes to filter.
        :param start: Start timestamp in ISO format.
        :param end: End timestamp in ISO format.
        :param limit: Maximum number of records to retrieve.
        :param order: Order of the results ('ASC' or 'DESC'). Default is 'DESC'.
        :return: List of dictionaries containing sensor data records.
        """
        try:
            params: List[Any] = []

            if isinstance(sensor_codes, str):
                sensor_codes = [sensor_codes]

            selected_columns = ", ".join(
                f'"{column}"' for column in sensor_codes  
            ) if sensor_codes else "*"

            query = f"""
                SELECT timestamp, {selected_columns} FROM sensor_data 
                WHERE 1=1
            """

            if start and end:
                query += " AND timestamp BETWEEN ? AND ?"
                params.extend([start, end])
            elif start:
                query += " AND timestamp >= ?"
                params.append(start)
            elif end:
                query += " AND timestamp <= ?"
                params.append(end)

            query += f" ORDER BY timestamp {order}"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            self.cursor.execute(query, tuple(params))
            rows = self.cursor.fetchall()
            
            if rows:
              column_names = [desc[0] for desc in self.cursor.description]
              return  [dict(zip(column_names, row)) for row in rows]
            return []
        except sqlite3.Error as e:
            logging.error(f"Error fetching records for sensors {sensor_codes}: {e}")
            return []
        except Exception as e:
            logging.error(f"Error fetching records for sensors {sensor_codes}: {e}")
            return []

  def get_sensor_statistics(
        self,
        sensor_code: str,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Compute statistics (average, min, max) for a specific sensor within a timeframe.

        :param sensor_code: Sensor code to compute statistics for.
        :param start: Start timestamp in ISO format.
        :param end: End timestamp in ISO format.
        :return: Dictionary containing statistics or None if no data exists.
        """
        try:
            query = f"""
                SELECT 
                    AVG( "{sensor_code}" ) as average, 
                    MIN( "{sensor_code}" ) as minimum, 
                    MAX( "{sensor_code}" ) as maximum 
                FROM sensor_data
                where 1 = 1
            """
            params: List[Any] = []

            if start and end:
                query += " AND timestamp BETWEEN ? AND ?"
                params.extend([start, end])
            elif start:
                query += " AND timestamp >= ?"
                params.append(start)
            elif end:
                query += " AND timestamp <= ?"
                params.append(end)

            self.cursor.execute(query, tuple(params))
            result = self.cursor.fetchone()
            
            if result:
                column_names = [desc[0] for desc in self.cursor.description]
                row_dict = dict(zip(column_names, result))
                result = row_dict
            
            if result and result["average"] is not None:
                return {
                    "sensor_code": sensor_code,
                    "average": result["average"],
                    "minimum": result["minimum"],
                    "maximum": result["maximum"]
                }
            return None
        except sqlite3.Error as e:
            logging.error(f"Error computing statistics for sensor {sensor_code}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error computing statistics for sensor {sensor_code}: {e}")
            return None

  def get_general_statistics(self, start: Optional[str] = None, end: Optional[str] = None) -> Dict[str, Any]:
      """
      Compute general statistics (average, min, max) for all sensors within a timeframe.

      :param start: Start timestamp in ISO format.
      :param end: End timestamp in ISO format.
      :return: Dictionary containing general statistics for all sensors.
      """
      try:
        sensor_codes = self.get_sensor_codes()
        general_stats = {}

        for sensor_code in sensor_codes:
          stats = self.get_sensor_statistics(sensor_code, start, end)
          if stats:
            general_stats[sensor_code] = stats

        return general_stats
      except sqlite3.Error as e:
        logging.error(f"Error computing general statistics: {e}")
        return {}
      except Exception as e:
        logging.error(f"Error computing general statistics: {e}")
        return {}

  def count_records(
        self, 
        start: Optional[str] = None, 
        end: Optional[str] = None
    ) -> int:
        """
        Count the number of sensor data records, optionally filtered by sensor codes and timeframe.

        :param sensor_code: Single sensor code or list of sensor codes to filter (optional).
        :param start: Start timestamp in ISO format (optional).
        :param end: End timestamp in ISO format (optional).
        :return: Count of records matching the criteria.
        """
        try:
            query = "SELECT COUNT(*) as count FROM sensor_data WHERE 1=1"
            params: List[Any] = []

            if start and end:
                query += " AND timestamp BETWEEN ? AND ?"
                params.extend([start, end])
            elif start:
                query += " AND timestamp >= ?"
                params.append(start)
            elif end:
                query += " AND timestamp <= ?"
                params.append(end)

            self.cursor.execute(query, tuple(params))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logging.error(f"Error counting records: {e}")
            return 0
        except Exception as e:
            logging.error(f"Error counting records: {e}")
            return 0

  def get_sensors_metadata(self):
    self.cursor.execute("SELECT * FROM sensors_metadata")
    records = self.cursor.fetchall()
    
    column_names = [desc[0] for desc in self.cursor.description]
    
    return [dict(zip(column_names, record)) for record in records]
  
  def get_summary(
    self,
    sensor_codes: Union[str, List[str], None] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: Optional[int] = 20
  ) -> Dict[str, Any]:
    """
    Retrieve summary statistics for specific sensor(s) within a timeframe. if source_codes is None, return summary statistics for all sensors.
    
    The summary contains for each sensor :
      the metadata
      statistics (average, min, max) within the timeframe if available
      the number of records within the timeframe 
      the latest record 
      history of the sensor
    """
    try:
      summary = {}
      sensors_metadata = self.get_sensors_metadata()
      
      if sensor_codes is None:
        sensor_codes = [sensor["code"] for sensor in sensors_metadata]
      
      for sensor_code in sensor_codes:
        sensor_summary = {"metadata": None, "statistics": None, "history": []}
        
        for sensor in sensors_metadata:
          if sensor["code"] == sensor_code:
            sensor_summary["metadata"] = sensor
            break
          
        
        sensor_summary["statistics"] = self.get_sensor_statistics(sensor_code, start, end)
        sensor_summary["history"] = self.get_records_by_sensors(sensor_code, start, end, limit=limit)
        summary[sensor_code] = sensor_summary
      
      summary["count"] = self.count_records(start, end)
      summary["latest"] = self.get_last_record()
      return summary
    except sqlite3.Error as e:
      logging.error(f"Error fetching summary statistics: {e}")
      return {}
  
  def close(self):
    self.conn.close()
    logging.info("DB connection closed")
  
  
  
  
  