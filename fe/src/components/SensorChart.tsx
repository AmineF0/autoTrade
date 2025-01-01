import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { SensorData } from '../types';
import { useTheme } from './ThemeProvider';
import annotationPlugin from 'chartjs-plugin-annotation';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  annotationPlugin
);

interface SensorChartProps {
  sensor: SensorData;
  type: 'line' | 'bar';
}

export function SensorChart({ sensor, type }: SensorChartProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const labels = sensor.history.map(h => 
    new Date(h.timestamp).toLocaleTimeString()
  );

  const data = {
    labels,
    datasets: [
      {
        label: sensor.metadata.name,
        data: sensor.history.map(h => Number(h[sensor.metadata.code])),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: isDark ? '#fff' : '#000',
        },
      },
      title: {
        display: true,
        text: `${sensor.metadata.name} (${sensor.metadata.unit})`,
        color: isDark ? '#fff' : '#000',
      },
      annotation: {
        annotations: {
          upperLine: {
            type: 'line',
            yMin: sensor.metadata.upper,
            yMax: sensor.metadata.upper,
            borderColor: 'rgba(255, 99, 132, 0.8)',
            borderWidth: 2,
            borderDash: [5, 5],
            label: {
              display: true,
              content: `Upper Bound: ${sensor.metadata.upper}`,
              position: 'end'
            }
          },
          lowerLine: {
            type: 'line',
            yMin: sensor.metadata.lower,
            yMax: sensor.metadata.lower,
            borderColor: 'rgba(255, 99, 132, 0.8)',
            borderWidth: 2,
            borderDash: [5, 5],
            label: {
              display: true,
              content: `Lower Bound: ${sensor.metadata.lower}`,
              position: 'end'
            }
          }
        }
      }
    },
    scales: {
      y: {
        min: Math.min(sensor.metadata.lower * 0.9, Math.min(...data.datasets[0].data.map(Number))),
        max: Math.max(sensor.metadata.upper * 1.1, Math.max(...data.datasets[0].data.map(Number))),
        ticks: {
          color: isDark ? '#fff' : '#000',
        },
        grid: {
          color: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        },
      },
      x: {
        ticks: {
          color: isDark ? '#fff' : '#000',
        },
        grid: {
          color: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        },
      },
    },
  };

  return type === 'line' ? (
    <Line options={options} data={data} />
  ) : (
    <Bar options={options} data={data} />
  );
}