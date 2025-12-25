import React, { useState, useMemo } from 'react';
import {
  Autocomplete,
  TextField,
  Box,
  Typography,
  CircularProgress,
  Paper,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { useActiveSymbols } from '../../hooks/useActiveSymbols';
import { SymbolInfo } from '../../types';
import { touchTargets } from '../../utils/responsive';

interface SearchBoxProps {
  onSearch: (symbol: string) => void;
}

const SearchBox: React.FC<SearchBoxProps> = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const { data: symbols, isLoading } = useActiveSymbols();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const filteredSuggestions = useMemo(() => {
    if (!symbols?.symbols || !query.trim()) return [];

    const searchTerm = query.toLowerCase().trim();
    return symbols.symbols
      .filter(
        (symbol: SymbolInfo) =>
          symbol.symbol.toLowerCase().includes(searchTerm) ||
          symbol.organ_name.toLowerCase().includes(searchTerm)
      )
      .slice(0, 10); // Limit to 10 suggestions for performance
  }, [query, symbols]);

  const handleInputChange = (_: React.SyntheticEvent, value: string) => {
    setQuery(value);
    setOpen(value.length > 0);
  };

  const handleSelection = (
    _: React.SyntheticEvent,
    value: SymbolInfo | null
  ) => {
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

  const renderOption = (
    props: React.HTMLAttributes<HTMLLIElement>,
    option: SymbolInfo
  ) => (
    <Box 
      component="li" 
      {...props} 
      key={option.symbol}
      sx={{
        minHeight: touchTargets.minimum,
        py: 1,
        px: 2,
      }}
    >
      <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
        <Typography 
          variant="body1" 
          sx={{ 
            fontWeight: 'bold',
            fontSize: { xs: '0.875rem', sm: '1rem' },
          }}
        >
          {option.symbol}
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ 
            fontSize: { xs: '0.75rem', sm: '0.875rem' },
            lineHeight: 1.2,
          }}
        >
          {option.organ_name}
        </Typography>
        {option.icb_name2 && !isMobile && (
          <Typography 
            variant="caption" 
            color="text.secondary"
            sx={{ fontSize: '0.75rem' }}
          >
            {option.icb_name2}
          </Typography>
        )}
      </Box>
    </Box>
  );

  const renderNoOptions = () => (
    <Paper sx={{ p: 2 }}>
      <Typography 
        variant="body2" 
        color="text.secondary"
        sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }}
      >
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
      getOptionLabel={(option) =>
        typeof option === 'string'
          ? option
          : `${option.symbol} - ${option.organ_name}`
      }
      renderOption={renderOption}
      noOptionsText={renderNoOptions()}
      loading={isLoading}
      filterOptions={(x) => x} // We handle filtering manually
      onInputChange={handleInputChange}
      onChange={handleSelection}
      inputValue={query}
      sx={{
        width: { 
          xs: '160px', 
          sm: '200px', 
          md: '250px',
          lg: '300px',
        },
        '& .MuiOutlinedInput-root': {
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          minHeight: touchTargets.minimum,
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
          fontSize: { xs: '0.875rem', sm: '1rem' },
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
        '& .MuiAutocomplete-popupIndicator': {
          minWidth: touchTargets.minimum,
          minHeight: touchTargets.minimum,
        },
      }}
      ListboxProps={{
        sx: {
          maxHeight: { xs: '200px', sm: '300px' },
          '& .MuiAutocomplete-option': {
            minHeight: touchTargets.minimum,
          },
        },
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          placeholder={isMobile ? "Tìm mã..." : "Tìm mã cổ phiếu..."}
          variant="outlined"
          size={isMobile ? "small" : "medium"}
          onKeyPress={handleKeyPress}
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <SearchIcon 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.7)', 
                  mr: 1,
                  fontSize: { xs: '1.25rem', sm: '1.5rem' },
                }} 
              />
            ),
            endAdornment: (
              <>
                {isLoading ? (
                  <CircularProgress 
                    color="inherit" 
                    size={isMobile ? 16 : 20} 
                  />
                ) : null}
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
