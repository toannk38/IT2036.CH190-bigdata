/**
 * Utility functions for formatting data in the application
 */

/**
 * Format price from API (in thousands VND) to display format (VND)
 * API returns price in thousands VND, so multiply by 1000 to get actual VND
 * @param price - Price in thousands VND from API
 * @returns Formatted price string in Vietnamese locale
 */
export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price * 1000);
};

/**
 * Format volume with abbreviated notation
 * @param volume - Trading volume
 * @returns Formatted volume string with K/M abbreviations
 */
export const formatVolume = (volume: number): string => {
  if (volume >= 1000000) {
    return `${(volume / 1000000).toFixed(1)}M`;
  } else if (volume >= 1000) {
    return `${(volume / 1000).toFixed(1)}K`;
  }
  return volume.toLocaleString('vi-VN');
};

/**
 * Format timestamp to Vietnamese locale
 * @param timestamp - ISO timestamp string
 * @returns Formatted date/time string
 */
export const formatTimestamp = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (error) {
    return timestamp;
  }
};

/**
 * Format timestamp with extended details (weekday, seconds)
 * @param timestamp - ISO timestamp string
 * @returns Formatted date/time string with extended details
 */
export const formatTimestampExtended = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('vi-VN', {
      weekday: 'long',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch (error) {
    return timestamp;
  }
};

/**
 * Format technical score to percentage
 * @param score - Score value between 0 and 1
 * @returns Formatted percentage string
 */
export const formatTechnicalScore = (score: number): string => {
  return `${(score * 100).toFixed(1)}%`;
};

/**
 * Format price change with sign and color indication
 * @param change - Price change value (in thousands VND from API)
 * @returns Object with formatted change and color indication
 */
export const formatPriceChange = (change: number) => {
  const isPositive = change >= 0;
  const formattedChange = formatPrice(Math.abs(change));
  
  return {
    value: `${isPositive ? '+' : '-'}${formattedChange}`,
    isPositive,
    color: isPositive ? 'success' : 'error',
  };
};

/**
 * Format percentage change
 * @param changePercent - Percentage change value
 * @returns Formatted percentage string with sign
 */
export const formatPercentageChange = (changePercent: number): string => {
  const isPositive = changePercent >= 0;
  return `${isPositive ? '+' : ''}${changePercent.toFixed(2)}%`;
};