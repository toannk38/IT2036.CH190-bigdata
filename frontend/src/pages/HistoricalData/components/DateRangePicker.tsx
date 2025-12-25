import React from 'react';
import { TextField, Alert, Box } from '@mui/material';
import { DateRangePickerProps } from '@/types';

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  value,
  onChange,
}) => {
  const handleStartDateChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const newStartDate = event.target.value;
    onChange({
      ...value,
      start: newStartDate,
    });
  };

  const handleEndDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newEndDate = event.target.value;
    onChange({
      ...value,
      end: newEndDate,
    });
  };

  // Validation logic
  const isValidDateRange = () => {
    if (!value.start || !value.end) return true; // Allow empty values

    const startDate = new Date(value.start);
    const endDate = new Date(value.end);
    const today = new Date();

    // Check if start date is before end date
    if (startDate >= endDate) return false;

    // Check if dates are not in the future
    if (startDate > today || endDate > today) return false;

    // Check if date range is not too long (max 2 years)
    const maxRangeMs = 2 * 365 * 24 * 60 * 60 * 1000; // 2 years in milliseconds
    if (endDate.getTime() - startDate.getTime() > maxRangeMs) return false;

    return true;
  };

  const getValidationMessage = () => {
    if (!value.start || !value.end) return null;

    const startDate = new Date(value.start);
    const endDate = new Date(value.end);
    const today = new Date();

    if (startDate >= endDate) {
      return 'Ngày bắt đầu phải trước ngày kết thúc';
    }

    if (startDate > today || endDate > today) {
      return 'Không thể chọn ngày trong tương lai';
    }

    const maxRangeMs = 2 * 365 * 24 * 60 * 60 * 1000;
    if (endDate.getTime() - startDate.getTime() > maxRangeMs) {
      return 'Khoảng thời gian không được vượt quá 2 năm';
    }

    return null;
  };

  const validationMessage = getValidationMessage();
  const isValid = isValidDateRange();

  // Calculate max date (today)
  const today = new Date().toISOString().split('T')[0];

  // Calculate min date (2 years ago)
  const twoYearsAgo = new Date();
  twoYearsAgo.setFullYear(twoYearsAgo.getFullYear() - 2);
  const minDate = twoYearsAgo.toISOString().split('T')[0];

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          gap: 2,
        }}
      >
        <Box sx={{ flex: 1 }}>
          <TextField
            fullWidth
            type="date"
            label="Ngày bắt đầu"
            value={value.start}
            onChange={handleStartDateChange}
            InputLabelProps={{
              shrink: true,
            }}
            inputProps={{
              min: minDate,
              max: value.end || today,
            }}
            error={!isValid && !!value.start}
          />
        </Box>

        <Box sx={{ flex: 1 }}>
          <TextField
            fullWidth
            type="date"
            label="Ngày kết thúc"
            value={value.end}
            onChange={handleEndDateChange}
            InputLabelProps={{
              shrink: true,
            }}
            inputProps={{
              min: value.start || minDate,
              max: today,
            }}
            error={!isValid && !!value.end}
          />
        </Box>
      </Box>

      {validationMessage && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {validationMessage}
        </Alert>
      )}

      {isValid && value.start && value.end && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Khoảng thời gian: {new Date(value.start).toLocaleDateString('vi-VN')}{' '}
          - {new Date(value.end).toLocaleDateString('vi-VN')}
        </Alert>
      )}
    </Box>
  );
};
