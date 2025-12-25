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
import { FinalScoreChartProps } from '@/types';
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

export const FinalScoreChart: React.FC<FinalScoreChartProps> = ({ data }) => {
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

  // Prepare chart data
  const chartData = {
    labels: data.map((point) => new Date(point.timestamp)),
    datasets: [
      {
        label: 'Điểm Số Cuối Cùng',
        data: data.map((point) => ({
          x: new Date(point.timestamp),
          y: point.final_score,
        })),
        borderColor: 'rgb(25, 118, 210)',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.1,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: 'rgb(25, 118, 210)',
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
            return `Điểm số: ${(context.parsed.y || 0).toFixed(2)}`;
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
          text: 'Điểm Số',
          font: {
            size: 12,
            weight: 'bold',
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          callback: function (value) {
            return (value as number).toFixed(2);
          },
        },
      },
    },
    elements: {
      point: {
        hoverBackgroundColor: 'rgb(25, 118, 210)',
      },
    },
  };

  return (
    <Box>
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <Button variant="outlined" size="small" onClick={resetZoom}>
          Đặt lại zoom
        </Button>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ alignSelf: 'center' }}
        >
          Sử dụng chuột để zoom và kéo để di chuyển biểu đồ
        </Typography>
      </Stack>
      <Box height={400}>
        {/* @ts-expect-error Chart.js type compatibility issue */}
        <Line ref={chartRef} data={chartData} options={options} />
      </Box>
    </Box>
  );
};
