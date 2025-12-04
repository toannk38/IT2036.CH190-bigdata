Hãy giúp tôi tạo một file markdown tên là `plan.md`, mô tả toàn bộ thiết kế hệ thống backend cho một nền tảng AI gợi ý và cảnh báo cổ phiếu Việt Nam.

Yêu cầu về nội dung trong plan.md:

# 1. Kiến trúc tổng thể hệ thống
- Mô tả kiến trúc tổng quan dạng “high-level system architecture”.
- Bao gồm các thành phần chính:
  - Data Pipeline
  - Kho dữ liệu (MongoDB)
  - AI/ML Analysis Engine
  - LLM News Analysis Engine
  - Aggregation & Scoring Service
  - API Service layer
  - Dashboard Client (chỉ mô tả nhẹ)

# 2. Data Pipeline (ETL + Streaming)
Mô tả chi tiết:

## 2.1 Source Data
- Giá cổ phiếu, khối lượng giao dịch
- Tin tức thị trường, tin tức theo từng mã
- Tất cả dữ liệu được crawl từ thư viện **vnstock**

## 2.2 Collector / Producer Services
- Service 1: Crawl **giá cổ phiếu** từ vnstock  
  - Chuẩn hoá dữ liệu, chuẩn format timestamp
  - Emit vào Kafka topic: `stock_prices_raw`

- Service 2: Crawl **tin tức** theo từng mã từ vnstock  
  - Làm sạch, remove trùng
  - Emit vào Kafka topic: `stock_news_raw`

## 2.3 Kafka Pipeline
- Chạy 2 topic chính:
  - `stock_prices_raw`
  - `stock_news_raw`
- Thiết kế consumer groups tương ứng cho từng loại dữ liệu

## 2.4 Consumer Services → MongoDB
- Consumer service đọc dữ liệu giá → lưu vào collections:
  - `price_history`
  - `stocks` (metadata)
- Consumer service đọc dữ liệu tin tức → lưu vào `news`
- Thiết kế schema chi tiết cho:
  - stocks
  - price_history
  - news
  - ai_analysis
  - llm_analysis
  - final_scores

# 3. AI/ML Analysis Engine (Phân tích dữ liệu lịch sử)
Bao gồm:
- Xử lý dữ liệu time-series từ `price_history`
- Feature engineering:
  - candle patterns
  - MA, RSI, MACD
  - volatility
  - volume anomalies
- Hướng mô hình:
  - ARIMA
  - LSTM
  - Transformer Time-Series
  - Catboost
- Output model:
  - Xu hướng (trend prediction)
  - Đánh giá rủi ro (risk score)
  - Điểm sức mạnh cổ phiếu (technical score)
- Lưu kết quả vào MongoDB collection `ai_analysis`
- Lên lịch chạy định kỳ (Airflow)

# 4. LLM News Analysis Engine
- Crawl tin tức từ vnstock (đã có ở pipeline)
- Làm sạch nội dung
- Gọi API LLM để:
  - Tóm tắt tin
  - Xác định sentiment (pos / neg / neutral)
  - Đánh giá độ ảnh hưởng đến mã cổ phiếu
  - Gợi ý insight quan trọng về doanh nghiệp
- Lưu kết quả vào `llm_analysis`

# 5. Aggregation & Scoring Service
- Kết hợp phân tích AI/ML (định lượng)
- Kết hợp phân tích LLM (định tính)
- Tính ra các chỉ số:
  - sentiment_score
  - technical_score
  - risk_score
  - final_score
- Sinh alerts:
  - BUY / WATCH / RISK
  - Cảnh báo biến động theo thời gian thực

# 6. API Layer
Thiết kế REST API:
- /stock/{symbol}/summary
- /stock/{symbol}/ai-analysis
- /stock/{symbol}/llm-analysis
- /stock/{symbol}/scores
- /alert/list
- /news/latest
- Mô tả input/output JSON mẫu

# 7. Non-functional Requirements
- Mở rộng (scaling): Kafka partition, sharding MongoDB
- Logging (ELK Stack)
- Monitoring (Prometheus + Grafana)
- Bảo mật API key, rate limit, RBAC

# 8. Deployment Plan
- Docker Compose
- Quản lý secrets (Vault hoặc .env + Docker secrets)

# 9. Roadmap phát triển 3 tháng
- Phase 1: Data Pipeline từ vnstock (prices + news)
- Phase 2: AI/ML Analysis
- Phase 3: LLM Analysis
- Phase 4: Aggregation & API
- Phase 5: Dashboard & alert system
 