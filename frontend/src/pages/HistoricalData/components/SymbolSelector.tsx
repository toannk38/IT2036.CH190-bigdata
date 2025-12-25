import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Box,
} from '@mui/material';
import { useActiveSymbols } from '@/hooks/useActiveSymbols';
import { SymbolSelectorProps } from '@/types';

export const SymbolSelector: React.FC<SymbolSelectorProps> = ({
  value,
  onChange,
}) => {
  const { data: symbolsResponse, isLoading, error } = useActiveSymbols();

  const handleChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    onChange(event.target.value as string);
  };

  if (error) {
    return <Alert severity="error">Không thể tải danh sách mã cổ phiếu</Alert>;
  }

  return (
    <FormControl fullWidth>
      <InputLabel id="symbol-selector-label">Chọn mã cổ phiếu</InputLabel>
      <Select
        labelId="symbol-selector-label"
        id="symbol-selector"
        value={value}
        label="Chọn mã cổ phiếu"
        // @ts-expect-error MUI Select onChange type compatibility
        onChange={handleChange}
        disabled={isLoading}
        endAdornment={
          isLoading ? (
            <Box sx={{ display: 'flex', alignItems: 'center', pr: 2 }}>
              <CircularProgress size={20} />
            </Box>
          ) : null
        }
      >
        <MenuItem value="">
          <em>-- Chọn mã cổ phiếu --</em>
        </MenuItem>
        {symbolsResponse?.symbols?.map((symbol) => (
          <MenuItem key={symbol.symbol} value={symbol.symbol}>
            {symbol.symbol} - {symbol.organ_name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};
