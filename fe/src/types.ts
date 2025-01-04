export interface SensorData {
  metadata: {
    code: string;
    name: string;
    description: string;
    upper: number;
    lower: number;
    unit: string;
    departement: string;
  };
  statistics: {
    sensor_code: string;
    average: number;
    minimum: number;
    maximum: number;
  };
  history: {
    timestamp: string;
    [key: string]: string | number;
  }[];
}

export interface Stats {
  [key: string]: SensorData | number | { timestamp: string; [key: string]: string | number };
  count: number;
  latest: {
    timestamp: string;
    [key: string]: string | number;
  };
}

export type Role = 'CEO' | 'manager' | 'worker' | 'auditor';