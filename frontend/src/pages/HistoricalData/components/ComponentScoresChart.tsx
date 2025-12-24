import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  ChartOptions,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import zoomPlugin from 'chartjs-plugin-zoom';
import 'chartjs-adapter-date-fns';
import { HistoricalDataPoint } from '@/types';
import { Box, Typography, Button, Stack } from '@mui/material';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  zoomPlugin
);

interface ComponentScoresChartProps {
  data: HistoricalDataPoint[];
}

export const ComponentScoresChart: React.FC<ComponentScoresChartProps> = ({ data }) => {
  const chartRef = React.useRef<ChartJS<'line'>>(null);

  if (!data || data.length === 0) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height={400}
        bgcolor="grey.50"
        borderRadius={1}
      >
        <Typography variant="body1" color="text.secondary">
          Không có dữ liệu để hiển thị biểu đồ
        </Typography>
      </Box>
    );
  }

  const resetZoom = () => {
    if (chartRef.current) {
      chartRef.current.resetZoom();
    }
  };

  // Prepare chart data with multiple lines for each component score
  const chartData = {
    labels: data.map(point => new Date(point.timestamp)),
    datasets: [
      {
        label: 'Điểm Kỹ Thuật',
        data: data.map(point => ({
          x: new Date(point.timestamp),
          y: point.components.technical_score,
        })),
        borderColor: 'rgb(76, 175, 80)', // Green
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.1,
        pointRadius: 3,
        pointHoverRadius: 5,
        pointBackgroundColor: 'rgb(76, 175, 80)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
      {
        label: 'Điểm Rủi Ro',
        data: data.map(point => ({
          x: new Date(point.timestamp),
          y: point.components.risk_score,
        })),
        borderColor: 'rgb(255, 152, 0)', // Orange
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.1,
        pointRadius: 3,
        pointHoverRadius: 5,
        pointBackgroundColor: 'rgb(255, 152, 0)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
      {
        label: 'Điểm Tâm Lý',
        data: data.map(point => ({
          x: new Date(point.timestamp),
          y: point.components.sentiment_score,
        })),
        borderColor: 'rgb(156, 39, 176)', // Purple
        backgroundColor: 'rgba(156, 39, 176, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.1,
        pointRadius: 3,
        pointHoverRadius: 5,
        pointBackgroundColor: 'rgb(156, 39, 176)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
    ],
  };

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          generateLabels: (chart) => {
            const original = ChartJS.defaults.plugins.legend.labels.generateLabels;
            const labels = original.call(this, chart);
            
            // Add custom styling to legend labels
            labels.forEach((label) => {
              label.pointStyle = 'circle';
            });
            
            return labels;
          },
        },
      },
      title: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(25, 118, 210, 0.8)',
        borderWidth: 1,
        callbacks: {
          title: (context) => {
            const date = new Date(context[0].parsed.x || 0);
            return date.toLocaleDateString('vi-VN', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            });
          },
          label: (context) => {
            const datasetLabel = context.dataset.label || '';
            const value = (context.parsed.y || 0).toFixed(3);
            return `${datasetLabel}: ${value}`;
          },
        },
      },
      zoom: {
        zoom: {
          wheel: {
            enabled: true,
          },
          pinch: {
            enabled: true,
          },
          mode: 'x',
        },
        pan: {
          enabled: true,
          mode: 'x',
        },
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          displayFormats: {
            day: 'dd/MM',
            week: 'dd/MM',
            month: 'MM/yyyy',
          },
        },
        title: {
          display: true,
          text: 'Thời gian',
          font: {
            size: 12,
            weight: 'bold',
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
      y: {
        beginAtZero: true,
        max: 1,
        title: {
          display: true,
          text: 'Điểm Số Thành Phần',
          font: {
            size: 12,
            weight: 'bold',
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          callback: function(value) {
            return (value as number).toFixed(2);
          },
        },
      },
    },
    elements: {
      point: {
        hoverRadius: 6,
      },
    },
  };

  return (
    <Box>
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <Button 
          variant="outlined" 
          size="small" 
          onClick={resetZoom}
        >
          Đặt lại zoom
        </Button>
        <Typography variant="body2" color="text.secondary" sx={{ alignSelf: 'center' }}>
          Sử dụng chuột để zoom và kéo để di chuyển biểu đồ
        </Typography>
      </Stack>
      <Box height={400}>
        <Line ref={chartRef as any} data={chartData} options={options} />
      </Box>
    </Box>
  );
};