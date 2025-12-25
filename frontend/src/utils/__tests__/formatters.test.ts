import {
  formatPrice,
  formatVolume,
  formatTimestamp,
  formatTechnicalScore,
  formatPriceChange,
  formatPercentageChange,
} from '../formatters';

describe('formatters', () => {
  describe('formatPrice', () => {
    it('should format price correctly by multiplying by 1000', () => {
      // API returns price in thousands VND, so 50 means 50,000 VND
      expect(formatPrice(50)).toBe('50.000 ₫');
      expect(formatPrice(100.5)).toBe('100.500 ₫');
      expect(formatPrice(1000)).toBe('1.000.000 ₫');
    });

    it('should handle zero and negative values', () => {
      expect(formatPrice(0)).toBe('0 ₫');
      expect(formatPrice(-50)).toBe('-50.000 ₫');
    });
  });

  describe('formatVolume', () => {
    it('should format volume with K/M abbreviations', () => {
      expect(formatVolume(500)).toBe('500');
      expect(formatVolume(1500)).toBe('1.5K');
      expect(formatVolume(1500000)).toBe('1.5M');
      expect(formatVolume(2500000)).toBe('2.5M');
    });

    it('should use Vietnamese locale for numbers below 1000', () => {
      expect(formatVolume(999)).toBe('999');
    });
  });

  describe('formatTimestamp', () => {
    it('should format timestamp in Vietnamese locale', () => {
      const timestamp = '2023-12-25T10:30:00Z';
      const result = formatTimestamp(timestamp);
      
      // Should contain Vietnamese date format
      expect(result).toMatch(/\d{2}\/\d{2}\/\d{4}/);
      expect(result).toMatch(/\d{2}:\d{2}/);
    });

    it('should return original string for invalid timestamp', () => {
      const invalidTimestamp = 'invalid-date';
      expect(formatTimestamp(invalidTimestamp)).toBe(invalidTimestamp);
    });
  });

  describe('formatTechnicalScore', () => {
    it('should convert score to percentage', () => {
      expect(formatTechnicalScore(0.75)).toBe('75.0%');
      expect(formatTechnicalScore(0.123)).toBe('12.3%');
      expect(formatTechnicalScore(1)).toBe('100.0%');
      expect(formatTechnicalScore(0)).toBe('0.0%');
    });
  });

  describe('formatPriceChange', () => {
    it('should format positive price change', () => {
      const result = formatPriceChange(10);
      expect(result.value).toBe('+10.000 ₫');
      expect(result.isPositive).toBe(true);
      expect(result.color).toBe('success');
    });

    it('should format negative price change', () => {
      const result = formatPriceChange(-5);
      expect(result.value).toBe('-5.000 ₫');
      expect(result.isPositive).toBe(false);
      expect(result.color).toBe('error');
    });

    it('should handle zero change', () => {
      const result = formatPriceChange(0);
      expect(result.value).toBe('+0 ₫');
      expect(result.isPositive).toBe(true);
      expect(result.color).toBe('success');
    });
  });

  describe('formatPercentageChange', () => {
    it('should format positive percentage change', () => {
      expect(formatPercentageChange(5.67)).toBe('+5.67%');
      expect(formatPercentageChange(0.1)).toBe('+0.10%');
    });

    it('should format negative percentage change', () => {
      expect(formatPercentageChange(-3.45)).toBe('-3.45%');
    });

    it('should handle zero percentage change', () => {
      expect(formatPercentageChange(0)).toBe('+0.00%');
    });
  });
});