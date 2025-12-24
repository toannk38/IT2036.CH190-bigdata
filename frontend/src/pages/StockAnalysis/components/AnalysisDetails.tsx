import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
} from '@mui/material';
import {
  ExpandMore,
  SmartToy,
  Psychology,
  TrendingUp,
  Assessment,
} from '@mui/icons-material';
import { AnalysisDetailsProps } from '@/types';

const AnalysisDetails: React.FC<AnalysisDetailsProps> = ({
  aiAnalysis,
  llmAnalysis,
}) => {
  // Check if we have any analysis data
  const hasAiAnalysis = aiAnalysis && (aiAnalysis.trend_prediction || aiAnalysis.technical_score !== undefined);
  const hasLlmAnalysis = llmAnalysis && (llmAnalysis.sentiment || llmAnalysis.summary);

  if (!hasAiAnalysis && !hasLlmAnalysis) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Chi Tiết Phân Tích
          </Typography>
          <Alert severity="info">
            Chưa có dữ liệu phân tích chi tiết
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Format technical score
  const formatTechnicalScore = (score?: number): string => {
    if (score === undefined || score === null) return 'N/A';
    return (score * 100).toFixed(1) + '%';
  };

  // Get sentiment color
  const getSentimentColor = (sentiment?: string): string => {
    if (!sentiment) return '#9e9e9e';
    const lowerSentiment = sentiment.toLowerCase();
    if (lowerSentiment.includes('positive') || lowerSentiment.includes('tích cực')) {
      return '#4caf50';
    }
    if (lowerSentiment.includes('negative') || lowerSentiment.includes('tiêu cực')) {
      return '#f44336';
    }
    return '#ff9800';
  };

  // Get sentiment label
  const getSentimentLabel = (sentiment?: string): string => {
    if (!sentiment) return 'Không xác định';
    const lowerSentiment = sentiment.toLowerCase();
    if (lowerSentiment.includes('positive') || lowerSentiment.includes('tích cực')) {
      return 'Tích cực';
    }
    if (lowerSentiment.includes('negative') || lowerSentiment.includes('tiêu cực')) {
      return 'Tiêu cực';
    }
    if (lowerSentiment.includes('neutral') || lowerSentiment.includes('trung tính')) {
      return 'Trung tính';
    }
    return sentiment;
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Assessment sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            Chi Tiết Phân Tích
          </Typography>
        </Box>

        <Grid container spacing={2}>
          {/* AI/ML Analysis Section */}
          {hasAiAnalysis && (
            <Grid item xs={12}>
              <Accordion defaultExpanded>
                <AccordionSummary
                  expandIcon={<ExpandMore />}
                  aria-controls="ai-analysis-content"
                  id="ai-analysis-header"
                >
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <SmartToy sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                      Phân Tích AI/ML
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {/* Technical Score */}
                    {aiAnalysis?.technical_score !== undefined && (
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <TrendingUp sx={{ mr: 1, color: 'primary.main' }} />
                            <Typography variant="subtitle2">
                              Điểm Kỹ Thuật
                            </Typography>
                          </Box>
                          <Typography variant="h5" color="primary.main">
                            {formatTechnicalScore(aiAnalysis.technical_score)}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Đánh giá dựa trên các chỉ số kỹ thuật
                          </Typography>
                        </Box>
                      </Grid>
                    )}

                    {/* Trend Prediction */}
                    {aiAnalysis?.trend_prediction && (
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Dự Đoán Xu Hướng
                          </Typography>
                          <Typography variant="body1" sx={{ mb: 1 }}>
                            {aiAnalysis.trend_prediction}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Dự đoán từ mô hình machine learning
                          </Typography>
                        </Box>
                      </Grid>
                    )}

                    {/* Full AI Analysis Display */}
                    <Grid item xs={12}>
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Dữ liệu phân tích AI/ML đầy đủ:
                        </Typography>
                        <Box
                          component="pre"
                          sx={{
                            p: 2,
                            bgcolor: 'grey.100',
                            borderRadius: 1,
                            fontSize: '0.875rem',
                            overflow: 'auto',
                            maxHeight: 200,
                          }}
                        >
                          {JSON.stringify(aiAnalysis, null, 2)}
                        </Box>
                      </Box>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
          )}

          {/* LLM Analysis Section */}
          {hasLlmAnalysis && (
            <Grid item xs={12}>
              <Accordion defaultExpanded>
                <AccordionSummary
                  expandIcon={<ExpandMore />}
                  aria-controls="llm-analysis-content"
                  id="llm-analysis-header"
                >
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Psychology sx={{ mr: 1, color: 'secondary.main' }} />
                    <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                      Phân Tích LLM
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {/* Sentiment */}
                    {llmAnalysis?.sentiment && (
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Tâm Lý Thị Trường
                          </Typography>
                          <Chip
                            label={getSentimentLabel(llmAnalysis.sentiment)}
                            sx={{
                              backgroundColor: getSentimentColor(llmAnalysis.sentiment),
                              color: 'white',
                              fontWeight: 'medium',
                              mb: 1,
                            }}
                          />
                          <Typography variant="body2" color="text.secondary">
                            Phân tích từ tin tức và dữ liệu thị trường
                          </Typography>
                        </Box>
                      </Grid>
                    )}

                    {/* Summary */}
                    {llmAnalysis?.summary && (
                      <Grid item xs={12} sm={llmAnalysis?.sentiment ? 6 : 12}>
                        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Tóm Tắt Phân Tích
                          </Typography>
                          <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                            {llmAnalysis.summary}
                          </Typography>
                        </Box>
                      </Grid>
                    )}

                    {/* Full LLM Analysis Display */}
                    <Grid item xs={12}>
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Dữ liệu phân tích LLM đầy đủ:
                        </Typography>
                        <Box
                          component="pre"
                          sx={{
                            p: 2,
                            bgcolor: 'grey.100',
                            borderRadius: 1,
                            fontSize: '0.875rem',
                            overflow: 'auto',
                            maxHeight: 200,
                          }}
                        >
                          {JSON.stringify(llmAnalysis, null, 2)}
                        </Box>
                      </Box>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
          )}
        </Grid>

        {/* Information Note */}
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Lưu ý:</strong> Phân tích AI/ML và LLM được tạo tự động từ dữ liệu thị trường 
            và tin tức. Kết quả chỉ mang tính chất tham khảo và không phải lời khuyên đầu tư.
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );
};

export default AnalysisDetails;