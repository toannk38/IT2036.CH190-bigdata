import React, { useState, useMemo } from 'react';
import {
  Autocomplete,
  TextField,
  Box,
  Typography,
  CircularProgress,
  Paper,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { useActiveSymbols } from '../../hooks/useActiveSymbols';
import { SymbolInfo } from '../../types';

interface SearchBoxProps {
  onSearch: (symbol: string) => void;
}

const SearchBox: React.FC<SearchBoxProps> = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const { data: symbols, isLoading } = useActiveSymbols();

  const filteredSuggestions = useMemo(() => {
    if (!symbols?.symbols || !query.trim()) return [];
    
    const searchTerm = query.toLowerCase().trim();
    return symbols.symbols
      .filter((symbol: SymbolInfo) => 
        symbol.symbol.toLowerCase().includes(searchTerm) ||
        symbol.organ_name.toLowerCase().includes(searchTerm)
      )
      .slice(0, 10); // Limit to 10 suggestions for performance
  }, [query, symbols]);

  const handleInputChange = (_: any, value: string) => {
    setQuery(value);
    setOpen(value.length > 0);
  };

  const handleSelection = (_: any, value: SymbolInfo | null) => {
    if (value) {
      onSearch(value.symbol);
      setQuery('');
      setOpen(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && query.trim()) {
      // If user presses Enter, search for the exact query
      const exactMatch = symbols?.symbols?.find(
        (symbol: SymbolInfo) => 
          symbol.symbol.toLowerCase() === query.toLowerCase().trim()
      );
      
      if (exactMatch) {
        onSearch(exactMatch.symbol);
      } else if (filteredSuggestions.length > 0) {
        // Use the first suggestion if no exact match
        onSearch(filteredSuggestions[0].symbol);
      }
      
      setQuery('');
      setOpen(false);
    }
  };

  const renderOption = (props: any, option: SymbolInfo) => (
    <Box component="li" {...props} key={option.symbol}>
      <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
          {option.symbol}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
          {option.organ_name}
        </Typography>
        {option.icb_name2 && (
          <Typography variant="caption" color="text.secondary">
            {option.icb_name2}
          </Typography>
        )}
      </Box>
    </Box>
  );

  const renderNoOptions = () => (
    <Paper sx={{ p: 2 }}>
      <Typography variant="body2" color="text.secondary">
        Không tìm thấy mã cổ phiếu
      </Typography>
    </Paper>
  );

  return (
    <Autocomplete
      open={open}
      onOpen={() => setOpen(query.length > 0)}
      onClose={() => setOpen(false)}
      options={filteredSuggestions}
      getOptionLabel={(option) => typeof option === 'string' ? option : `${option.symbol} - ${option.organ_name}`}
      renderOption={renderOption}
      noOptionsText={renderNoOptions()}
      loading={isLoading}
      filterOptions={(x) => x} // We handle filtering manually
      onInputChange={handleInputChange}
      onChange={handleSelection}
      inputValue={query}
      sx={{
        width: { xs: 200, sm: 300 },
        '& .MuiOutlinedInput-root': {
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          '& fieldset': {
            borderColor: 'rgba(255, 255, 255, 0.3)',
          },
          '&:hover fieldset': {
            borderColor: 'rgba(255, 255, 255, 0.5)',
          },
          '&.Mui-focused fieldset': {
            borderColor: 'rgba(255, 255, 255, 0.7)',
          },
        },
        '& .MuiInputBase-input': {
          color: 'white',
          '&::placeholder': {
            color: 'rgba(255, 255, 255, 0.7)',
            opacity: 1,
          },
        },
        '& .MuiAutocomplete-endAdornment': {
          '& .MuiSvgIcon-root': {
            color: 'rgba(255, 255, 255, 0.7)',
          },
        },
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          placeholder="Tìm mã cổ phiếu..."
          variant="outlined"
          size="small"
          onKeyPress={handleKeyPress}
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <SearchIcon sx={{ color: 'rgba(255, 255, 255, 0.7)', mr: 1 }} />
            ),
            endAdornment: (
              <>
                {isLoading ? <CircularProgress color="inherit" size={20} /> : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
    />
  );
};

export default SearchBox;