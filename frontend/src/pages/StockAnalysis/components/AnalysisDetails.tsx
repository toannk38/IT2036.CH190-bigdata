import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Grid,
  Divider,
} from '@mui/material';
import {
  ExpandMore,
  SmartToy,
  Psychology,
  TrendingUp,
  Assessment,
  TrendingDown,
  TrendingFlat,
  ShowChart,
  Timeline,
} from '@mui/icons-material';
import { AnalysisDetailsProps } from '@/types';

const AnalysisDetails: React.FC<AnalysisDetailsProps> = ({
  aiAnalysis,
  llmAnalysis,
}) => {
  // Check if we have any analysis data
  const hasAiAnalysis = aiAnalysis && Object.keys(aiAnalysis).length > 0;
  const hasLlmAnalysis = llmAnalysis && Object.keys(llmAnalysis).length > 0;

  if (!hasAiAnalysis && !hasLlmAnalysis) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Chi Tiết Phân Tích
          </Typography>
          <Alert severity="info">Chưa có dữ liệu phân tích chi tiết</Alert>
        </CardContent>
      </Card>
    );
  }

  // Format AI/ML Analysis Data
  const formatAIAnalysis = (data: any) => {
    if (!data) return null;

    const {
      timestamp,
      trend_prediction,
      risk_score,
      technical_score,
      indicators,
    } = data;

    return {
      timestamp,
      trend_prediction,
      risk_score,
      technical_score,
      indicators,
    };
  };

  // Format LLM Analysis Data
  const formatLLMAnalysis = (data: any) => {
    if (!data) return null;

    const {
      timestamp,
      sentiment,
      summary,
      influence_score,
      articles_analyzed,
    } = data;

    return {
      timestamp,
      sentiment,
      summary,
      influence_score,
      articles_analyzed,
    };
  };

  // Get trend direction icon and color
  const getTrendIcon = (direction: string) => {
    switch (direction?.toLowerCase()) {
      case 'up':
        return { icon: <TrendingUp />, color: '#4caf50' };
      case 'down':
        return { icon: <TrendingDown />, color: '#f44336' };
      default:
        return { icon: <TrendingFlat />, color: '#ff9800' };
    }
  };

  // Get sentiment color and label
  const getSentimentInfo = (sentiment: any) => {
    if (!sentiment) return { label: 'Không xác định', color: '#9e9e9e' };
    
    const sentimentValue = typeof sentiment === 'object' ? sentiment.sentiment : sentiment;
    
    switch (sentimentValue?.toLowerCase()) {
      case 'positive':
        return { label: 'Tích cực', color: '#4caf50' };
      case 'negative':
        return { label: 'Tiêu cực', color: '#f44336' };
      case 'neutral':
        return { label: 'Trung tính', color: '#ff9800' };
      default:
        return { label: sentimentValue || 'Không xác định', color: '#9e9e9e' };
    }
  };

  const aiData = formatAIAnalysis(aiAnalysis);
  const llmData = formatLLMAnalysis(llmAnalysis);

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Assessment sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2">
            Chi Tiết Phân Tích
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* AI/ML Analysis Section */}
          {hasAiAnalysis && aiData && (
            <Accordion defaultExpanded>
              <AccordionSummary
                expandIcon={<ExpandMore />}
                aria-controls="ai-analysis-content"
                id="ai-analysis-header"
              >
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <SmartToy sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                    Dữ liệu phân tích ML/AI đầy đủ
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  {/* Timestamp */}
                  {aiData.timestamp && (
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Thời gian phân tích: {new Date(aiData.timestamp).toLocaleString('vi-VN')}
                      </Typography>
                    </Box>
                  )}

                  {/* Trend Prediction */}
                  {aiData.trend_prediction && (
                    <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                        <ShowChart sx={{ mr: 1, color: 'primary.main' }} />
                        Dự đoán xu hướng
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={4}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getTrendIcon(aiData.trend_prediction.direction).icon}
                            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                              Hướng: {aiData.trend_prediction.direction === 'up' ? 'Tăng' : 
                                     aiData.trend_prediction.direction === 'down' ? 'Giảm' : 'Ngang'}
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Typography variant="body2" color="text.secondary">
                            Độ tin cậy: {(aiData.trend_prediction.confidence * 100).toFixed(2)}%
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Typography variant="body2" color="text.secondary">
                            Giá dự đoán: {aiData.trend_prediction.predicted_price?.toFixed(2)} đ
                          </Typography>
                        </Grid>
                      </Grid>
                    </Box>
                  )}

                  {/* Risk Score and Technical Score */}
                  <Grid container spacing={2}>
                    {aiData.risk_score !== undefined && (
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Điểm rủi ro
                          </Typography>
                          <Typography variant="h5" color="error.main">
                            {(aiData.risk_score * 100).toFixed(2)}%
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Mức độ rủi ro đầu tư
                          </Typography>
                        </Box>
                      </Grid>
                    )}
                    {aiData.technical_score !== undefined && (
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Điểm kỹ thuật
                          </Typography>
                          <Typography variant="h5" color="primary.main">
                            {(aiData.technical_score * 100).toFixed(1)}%
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Đánh giá kỹ thuật tổng thể
                          </Typography>
                        </Box>
                      </Grid>
                    )}
                  </Grid>

                  {/* Technical Indicators */}
                  {aiData.indicators && (
                    <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                        <Timeline sx={{ mr: 1, color: 'primary.main' }} />
                        Chỉ số kỹ thuật
                      </Typography>
                      <Grid container spacing={2}>
                        {aiData.indicators.rsi !== undefined && (
                          <Grid item xs={6} sm={3}>
                            <Typography variant="body2" color="text.secondary">RSI</Typography>
                            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                              {aiData.indicators.rsi.toFixed(2)}
                            </Typography>
                          </Grid>
                        )}
                        {aiData.indicators.macd !== undefined && (
                          <Grid item xs={6} sm={3}>
                            <Typography variant="body2" color="text.secondary">MACD</Typography>
                            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                              {aiData.indicators.macd.toFixed(4)}
                            </Typography>
                          </Grid>
                        )}
                        {aiData.indicators.moving_avg_20 !== undefined && (
                          <Grid item xs={6} sm={3}>
                            <Typography variant="body2" color="text.secondary">MA20</Typography>
                            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                              {aiData.indicators.moving_avg_20.toFixed(2)}
                            </Typography>
                          </Grid>
                        )}
                        {aiData.indicators.moving_avg_50 !== undefined && (
                          <Grid item xs={6} sm={3}>
                            <Typography variant="body2" color="text.secondary">MA50</Typography>
                            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                              {aiData.indicators.moving_avg_50.toFixed(2)}
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    </Box>
                  )}
                </Box>
              </AccordionDetails>
            </Accordion>
          )}

          {/* LLM Analysis Section */}
          {hasLlmAnalysis && llmData && (
            <Accordion defaultExpanded>
              <AccordionSummary
                expandIcon={<ExpandMore />}
                aria-controls="llm-analysis-content"
                id="llm-analysis-header"
              >
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Psychology sx={{ mr: 1, color: 'secondary.main' }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                    Dữ liệu phân tích LLM đầy đủ
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  {/* Timestamp */}
                  {llmData.timestamp && (
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Thời gian phân tích: {new Date(llmData.timestamp).toLocaleString('vi-VN')}
                      </Typography>
                    </Box>
                  )}

                  {/* Sentiment Analysis */}
                  {llmData.sentiment && (
                    <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Phân tích tâm lý thị trường
                      </Typography>
                      <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} sm={4}>
                          <Chip
                            label={getSentimentInfo(llmData.sentiment).label}
                            sx={{
                              backgroundColor: getSentimentInfo(llmData.sentiment).color,
                              color: 'white',
                              fontWeight: 'medium',
                            }}
                          />
                        </Grid>
                        {typeof llmData.sentiment === 'object' && (
                          <>
                            <Grid item xs={6} sm={4}>
                              <Typography variant="body2" color="text.secondary">
                                Điểm số: {llmData.sentiment.score || 0}
                              </Typography>
                            </Grid>
                            <Grid item xs={6} sm={4}>
                              <Typography variant="body2" color="text.secondary">
                                Độ tin cậy: {((llmData.sentiment.confidence || 0) * 100).toFixed(1)}%
                              </Typography>
                            </Grid>
                          </>
                        )}
                      </Grid>
                    </Box>
                  )}

                  {/* Summary */}
                  {llmData.summary && (
                    <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Tóm tắt phân tích
                      </Typography>
                      <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                        {llmData.summary}
                      </Typography>
                    </Box>
                  )}

                  {/* Analysis Stats */}
                  <Grid container spacing={2}>
                    {llmData.influence_score !== undefined && (
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Điểm ảnh hưởng
                          </Typography>
                          <Typography variant="h5" color="secondary.main">
                            {(llmData.influence_score * 100).toFixed(1)}%
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Mức độ ảnh hưởng tin tức
                          </Typography>
                        </Box>
                      </Grid>
                    )}
                    {llmData.articles_analyzed !== undefined && (
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Bài viết phân tích
                          </Typography>
                          <Typography variant="h5" color="info.main">
                            {llmData.articles_analyzed.toLocaleString()}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Số bài viết đã phân tích
                          </Typography>
                        </Box>
                      </Grid>
                    )}
                  </Grid>
                </Box>
              </AccordionDetails>
            </Accordion>
          )}
        </Box>

        {/* Information Note */}
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Lưu ý:</strong> Phân tích AI/ML và LLM được tạo tự động từ
            dữ liệu thị trường và tin tức. Kết quả chỉ mang tính chất tham khảo
            và không phải lời khuyên đầu tư.
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  );
};

export default AnalysisDetails;
