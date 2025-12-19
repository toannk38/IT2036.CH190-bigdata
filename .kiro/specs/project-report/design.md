# Design Document

## Overview

Tài liệu báo cáo môn học cho dự án "Vietnam Stock AI Backend" bao gồm 2 sản phẩm chính:

1. **Slide Beamer** (~15 slides): Thuyết trình tổng quan dự án với LaTeX Beamer template
2. **Báo cáo chi tiết** (15-20 trang A4): Tài liệu kỹ thuật đầy đủ với LaTeX article/report class
3. **Draw.io Diagrams**: Các sơ đồ kiến trúc dạng XML để dễ chỉnh sửa

## Architecture

### File Structure

```
report/
├── slide/
│   ├── main.tex              # Main slide file
│   ├── sections/
│   │   ├── 01-title.tex
│   │   ├── 02-introduction.tex
│   │   ├── 03-problem.tex
│   │   ├── 04-architecture.tex
│   │   ├── 05-components.tex
│   │   ├── 06-implementation.tex
│   │   ├── 07-demo.tex
│   │   ├── 08-results.tex
│   │   └── 09-conclusion.tex
│   └── images/               # Placeholder for exported diagrams
│
├── report/
│   ├── main.tex              # Main report file
│   ├── chapters/
│   │   ├── 01-introduction.tex
│   │   ├── 02-literature.tex
│   │   ├── 03-design.tex
│   │   ├── 04-implementation.tex
│   │   ├── 05-testing.tex
│   │   ├── 06-results.tex
│   │   └── 07-conclusion.tex
│   ├── appendices/
│   │   └── code-snippets.tex
│   └── images/               # Placeholder for exported diagrams
│
└── diagrams/
    ├── system-architecture.drawio.xml
    ├── data-flow.drawio.xml
    ├── component-diagram.drawio.xml
    ├── airflow-dags.drawio.xml
    └── kafka-flow.drawio.xml
```

## Components and Interfaces

### 1. Slide Beamer Template

**Theme**: Madrid hoặc Warsaw (professional academic theme)
**Color scheme**: Blue/Navy (phù hợp với chủ đề công nghệ)

**Slide Structure**:
| Slide | Nội dung |
|-------|----------|
| 1 | Title: Tên dự án, tên sinh viên, giảng viên, trường |
| 2 | Mục lục/Agenda |
| 3 | Giới thiệu vấn đề - Thị trường chứng khoán VN |
| 4 | Mục tiêu dự án |
| 5-6 | Kiến trúc tổng quan hệ thống |
| 7 | Data Collection Layer (Price & News) |
| 8 | Message Streaming (Kafka) |
| 9 | Analysis Layer (AI/ML + LLM) |
| 10 | Aggregation & API |
| 11 | Airflow Orchestration |
| 12 | Demo/Screenshots |
| 13 | Kết quả đạt được |
| 14 | Hạn chế và hướng phát triển |
| 15 | Q&A |

### 2. Report Document Structure

**Document class**: report hoặc article
**Page format**: A4, margins 2.5cm

**Chapter Structure**:

| Chapter | Nội dung | Số trang |
|---------|----------|----------|
| 1. Giới thiệu | Bối cảnh, mục tiêu, phạm vi | 2 |
| 2. Cơ sở lý thuyết | Kafka, MongoDB, Airflow, AI/ML, LLM | 3 |
| 3. Thiết kế hệ thống | Kiến trúc, components, data models | 4 |
| 4. Triển khai | Code structure, Docker, configuration | 4 |
| 5. Kiểm thử | Unit tests, property-based tests | 2 |
| 6. Kết quả | Demo, performance, screenshots | 2 |
| 7. Kết luận | Tổng kết, hạn chế, hướng phát triển | 2 |
| Phụ lục | Code snippets, references | 1-2 |

### 3. Draw.io Diagrams

#### 3.1 System Architecture Diagram
Hiển thị toàn bộ hệ thống với các layer:
- Orchestration Layer (Airflow)
- Collection Layer (Price/News Collectors)
- Streaming Layer (Kafka)
- Storage Layer (MongoDB)
- Analysis Layer (AI/ML + LLM Engines)
- Service Layer (Aggregation + API)

#### 3.2 Data Flow Diagram
Luồng dữ liệu từ nguồn đến API:
```
vnstock API → Collectors → Kafka → Consumers → MongoDB → Engines → Aggregation → API → Clients
```

#### 3.3 Component Diagram
Quan hệ giữa các components:
- SymbolManager
- PriceCollector
- NewsCollector
- KafkaConsumer
- AIMLEngine
- LLMEngine
- AggregationService
- APIService

#### 3.4 Airflow DAGs Diagram
3 DAGs độc lập:
- price_collection (*/5 * * * *)
- news_collection (*/30 * * * *)
- analysis_pipeline (@hourly)

#### 3.5 Kafka Flow Diagram
Topics và message flow:
- stock_prices_raw
- stock_news_raw

## Data Models

### LaTeX Packages Required

**Slide (Beamer)**:
```latex
\usepackage[utf8]{inputenc}
\usepackage[vietnamese]{babel}
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{listings}
\usepackage{hyperref}
```

**Report**:
```latex
\usepackage[utf8]{inputenc}
\usepackage[vietnamese]{babel}
\usepackage{graphicx}
\usepackage{float}
\usepackage{listings}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{tocloft}
\usepackage{caption}
\usepackage{subcaption}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

**Property 1: LaTeX compilation success**
*For any* generated LaTeX file, compiling with XeLaTeX or pdfLaTeX should produce a valid PDF without errors
**Validates: Requirements 1.1, 2.1**

**Property 2: Vietnamese character rendering**
*For any* Vietnamese text in the documents, all characters should render correctly in the compiled PDF
**Validates: Requirements 5.1, 5.3**

**Property 3: Draw.io XML validity**
*For any* generated Draw.io XML file, opening in Draw.io should display the diagram correctly without parsing errors
**Validates: Requirements 3.1**

**Property 4: Content accuracy**
*For any* technical description in the documents, the content should accurately reflect the actual implementation in the codebase
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

**Property 5: Document structure completeness**
*For any* generated document (slide or report), all required sections/chapters should be present
**Validates: Requirements 1.2, 2.2**

## Error Handling

### LaTeX Compilation Errors
- Ensure UTF-8 encoding for all .tex files
- Use XeLaTeX for Vietnamese support if pdfLaTeX fails
- Check for missing packages and install via tlmgr

### Draw.io Import Errors
- Validate XML structure before saving
- Use standard Draw.io shapes and connectors

## Testing Strategy

### Manual Testing
1. Compile LaTeX files and verify PDF output
2. Open Draw.io XML files and verify diagram rendering
3. Check Vietnamese text rendering
4. Verify all placeholders are clearly marked

### Checklist
- [ ] Slide compiles without errors
- [ ] Report compiles without errors
- [ ] All diagrams open in Draw.io
- [ ] Vietnamese characters display correctly
- [ ] All sections/chapters present
- [ ] Placeholders clearly marked for images
