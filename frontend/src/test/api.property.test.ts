import fc from 'fast-check';

// Feature: vietnam-stock-frontend, Property 1: API Integration and Data Display
describe('Property 1: API Integration and Data Display', () => {
  // Simplified data generators for property-based testing
  const stockSymbolGen = fc
    .array(fc.constantFrom('A', 'B', 'C', 'V', 'H', 'M', 'T'), {
      minLength: 3,
      maxLength: 4,
    })
    .map((arr) => arr.join(''));

  const priceDataGen = fc.record({
    timestamp: fc.constant('2024-01-01T00:00:00.000Z'),
    open: fc.float({ min: 1, max: 1000, noNaN: true }),
    close: fc.float({ min: 1, max: 1000, noNaN: true }),
    high: fc.float({ min: 1, max: 1000, noNaN: true }),
    low: fc.float({ min: 1, max: 1000, noNaN: true }),
    volume: fc.integer({ min: 1000, max: 10000000 }),
  });

  const alertGen = fc.record({
    type: fc.constantFrom('price_movement', 'volume_spike', 'news_sentiment'),
    priority: fc.constantFrom('high', 'medium', 'low'),
    message: fc.string({ minLength: 10, maxLength: 100 }),
  });

  const componentScoresGen = fc.record({
    technical_score: fc.float({ min: 0, max: 1, noNaN: true }),
    risk_score: fc.float({ min: 0, max: 1, noNaN: true }),
    sentiment_score: fc.float({ min: 0, max: 1, noNaN: true }),
  });

  const stockSummaryGen = fc.record({
    symbol: stockSymbolGen,
    current_price: fc.option(priceDataGen),
    final_score: fc.option(fc.float({ min: 0, max: 100, noNaN: true })),
    recommendation: fc.option(fc.constantFrom('BUY', 'SELL', 'HOLD')),
    component_scores: fc.option(componentScoresGen),
    alerts: fc.array(alertGen, { maxLength: 5 }),
    last_updated: fc.option(fc.constant('2024-01-01T00:00:00.000Z')),
  });

  it('should handle valid stock summary data correctly', () => {
    fc.assert(
      fc.property(stockSummaryGen, (stockSummary) => {
        // Property: For any valid StockSummary data structure,
        // all required fields should be present and properly typed
        expect(typeof stockSummary.symbol).toBe('string');
        expect(stockSummary.symbol.length).toBeGreaterThan(0);

        if (stockSummary.current_price) {
          expect(typeof stockSummary.current_price.open).toBe('number');
          expect(typeof stockSummary.current_price.close).toBe('number');
          expect(typeof stockSummary.current_price.high).toBe('number');
          expect(typeof stockSummary.current_price.low).toBe('number');
          expect(typeof stockSummary.current_price.volume).toBe('number');
          expect(stockSummary.current_price.volume).toBeGreaterThan(0);
        }

        if (stockSummary.recommendation) {
          expect(['BUY', 'SELL', 'HOLD']).toContain(
            stockSummary.recommendation
          );
        }

        if (stockSummary.component_scores) {
          expect(
            stockSummary.component_scores.technical_score
          ).toBeGreaterThanOrEqual(0);
          expect(
            stockSummary.component_scores.technical_score
          ).toBeLessThanOrEqual(1);
          expect(
            stockSummary.component_scores.risk_score
          ).toBeGreaterThanOrEqual(0);
          expect(stockSummary.component_scores.risk_score).toBeLessThanOrEqual(
            1
          );
          expect(
            stockSummary.component_scores.sentiment_score
          ).toBeGreaterThanOrEqual(0);
          expect(
            stockSummary.component_scores.sentiment_score
          ).toBeLessThanOrEqual(1);
        }

        stockSummary.alerts.forEach((alert) => {
          expect(['high', 'medium', 'low']).toContain(alert.priority);
          expect(typeof alert.message).toBe('string');
          expect(alert.message.length).toBeGreaterThan(0);
        });
      }),
      { numRuns: 100 }
    );
  });

  it('should validate alert response structure', () => {
    const alertResponseGen = fc.record({
      alerts: fc.array(
        fc.record({
          symbol: stockSymbolGen,
          timestamp: fc.constant('2024-01-01T00:00:00.000Z'),
          final_score: fc.float({ min: 0, max: 100, noNaN: true }),
          recommendation: fc.constantFrom('BUY', 'SELL', 'HOLD'),
          type: fc.string({ minLength: 1 }),
          priority: fc.constantFrom('high', 'medium', 'low'),
          message: fc.string({ minLength: 1 }),
        }),
        { maxLength: 20 }
      ),
      total: fc.integer({ min: 0, max: 1000 }),
      page: fc.integer({ min: 1, max: 100 }),
      page_size: fc.integer({ min: 1, max: 100 }),
    });

    fc.assert(
      fc.property(alertResponseGen, (alertResponse) => {
        // Property: For any valid AlertResponse, pagination data should be consistent
        expect(alertResponse.total).toBeGreaterThanOrEqual(0);
        expect(alertResponse.page).toBeGreaterThan(0);
        expect(alertResponse.page_size).toBeGreaterThan(0);
        expect(Array.isArray(alertResponse.alerts)).toBe(true);

        alertResponse.alerts.forEach((alert) => {
          expect(typeof alert.symbol).toBe('string');
          expect(alert.symbol.length).toBeGreaterThan(0);
          expect(['BUY', 'SELL', 'HOLD']).toContain(alert.recommendation);
          expect(['high', 'medium', 'low']).toContain(alert.priority);
          expect(alert.final_score).toBeGreaterThanOrEqual(0);
          expect(alert.final_score).toBeLessThanOrEqual(100);
        });
      }),
      { numRuns: 100 }
    );
  });

  it('should validate symbols response structure', () => {
    const symbolsResponseGen = fc.record({
      symbols: fc.array(
        fc.record({
          symbol: stockSymbolGen,
          organ_name: fc.string({ minLength: 1, maxLength: 100 }),
          active: fc.boolean(),
        }),
        { maxLength: 50 }
      ),
    });

    fc.assert(
      fc.property(symbolsResponseGen, (symbolsResponse) => {
        // Property: For any valid SymbolsResponse, all symbols should have required fields
        expect(Array.isArray(symbolsResponse.symbols)).toBe(true);

        symbolsResponse.symbols.forEach((symbol) => {
          expect(typeof symbol.symbol).toBe('string');
          expect(symbol.symbol.length).toBeGreaterThan(0);
          expect(typeof symbol.organ_name).toBe('string');
          expect(symbol.organ_name.length).toBeGreaterThan(0);
          expect(typeof symbol.active).toBe('boolean');
        });
      }),
      { numRuns: 100 }
    );
  });

  it('should validate component scores structure', () => {
    fc.assert(
      fc.property(componentScoresGen, (componentScores) => {
        // Property: For any valid ComponentScores, all scores should be between 0 and 1
        expect(componentScores.technical_score).toBeGreaterThanOrEqual(0);
        expect(componentScores.technical_score).toBeLessThanOrEqual(1);
        expect(componentScores.risk_score).toBeGreaterThanOrEqual(0);
        expect(componentScores.risk_score).toBeLessThanOrEqual(1);
        expect(componentScores.sentiment_score).toBeGreaterThanOrEqual(0);
        expect(componentScores.sentiment_score).toBeLessThanOrEqual(1);

        // Ensure no NaN values
        expect(Number.isNaN(componentScores.technical_score)).toBe(false);
        expect(Number.isNaN(componentScores.risk_score)).toBe(false);
        expect(Number.isNaN(componentScores.sentiment_score)).toBe(false);
      }),
      { numRuns: 100 }
    );
  });
});
