# Requirements Document

## Introduction

Tạo tài liệu báo cáo môn học cho dự án "Vietnam Stock AI Backend" bao gồm slide thuyết trình và báo cáo chi tiết. Tài liệu sử dụng LaTeX để đảm bảo chất lượng trình bày chuyên nghiệp, kèm theo các sơ đồ kiến trúc dạng Draw.io XML để dễ dàng chỉnh sửa.

## Glossary

- **LaTeX**: Hệ thống soạn thảo tài liệu chất lượng cao
- **Beamer**: Package LaTeX để tạo slide thuyết trình
- **Draw.io**: Công cụ vẽ sơ đồ, xuất ra định dạng XML
- **Placeholder**: Vị trí đánh dấu trong tài liệu để chèn nội dung sau
- **Architecture Diagram**: Sơ đồ kiến trúc hệ thống
- **Data Flow Diagram**: Sơ đồ luồng dữ liệu
- **Component Diagram**: Sơ đồ các thành phần

## Requirements

### Requirement 1

**User Story:** As a student, I want to create a LaTeX Beamer slide presentation, so that I can present my project professionally to the examination board.

#### Acceptance Criteria

1. WHEN creating the slide presentation, THE System SHALL generate a LaTeX Beamer template with approximately 15 slides
2. WHEN organizing slide content, THE System SHALL include sections: Title, Introduction, Problem Statement, Architecture, Components, Implementation, Demo, Results, Conclusion
3. WHEN presenting technical content, THE System SHALL include placeholders for architecture diagrams and data flow diagrams
4. WHEN formatting slides, THE System SHALL use a professional academic theme suitable for university presentations
5. WHEN saving the presentation, THE System SHALL store all files in the report/slide directory

### Requirement 2

**User Story:** As a student, I want to create a detailed LaTeX report document, so that I can submit a comprehensive technical documentation of my project.

#### Acceptance Criteria

1. WHEN creating the report, THE System SHALL generate a LaTeX document with 15-20 A4 pages
2. WHEN organizing report content, THE System SHALL include chapters: Introduction, Literature Review, System Design, Implementation, Testing, Results, Conclusion
3. WHEN documenting architecture, THE System SHALL include placeholders for system architecture, component diagrams, and data flow diagrams
4. WHEN formatting the report, THE System SHALL follow standard academic report format with table of contents, list of figures, and references
5. WHEN saving the report, THE System SHALL store all files in the report/report directory

### Requirement 3

**User Story:** As a student, I want Draw.io XML files for all diagrams, so that I can easily edit and customize the diagrams before including them in my documents.

#### Acceptance Criteria

1. WHEN creating diagrams, THE System SHALL generate Draw.io XML files for each diagram type
2. WHEN designing the architecture diagram, THE System SHALL include all system components: Airflow, Kafka, MongoDB, Collectors, Engines, API
3. WHEN designing the data flow diagram, THE System SHALL show data movement from collection through analysis to API
4. WHEN designing the component diagram, THE System SHALL show relationships between Price Collector, News Collector, AI/ML Engine, LLM Engine, Aggregation Service, and API Service
5. WHEN saving diagrams, THE System SHALL store XML files in report/diagrams directory with descriptive names

### Requirement 4

**User Story:** As a student, I want the documents to accurately reflect my project's technical details, so that the examination board can understand the system implementation.

#### Acceptance Criteria

1. WHEN describing the system, THE documents SHALL accurately describe the microservices architecture using Kafka, MongoDB, and Airflow
2. WHEN explaining data collection, THE documents SHALL describe the Price Collector (5-minute interval) and News Collector (30-minute interval)
3. WHEN explaining analysis, THE documents SHALL describe the AI/ML Engine for quantitative analysis and LLM Engine for sentiment analysis
4. WHEN explaining aggregation, THE documents SHALL describe the weighted scoring system and alert generation
5. WHEN explaining deployment, THE documents SHALL describe the Docker Compose setup and service orchestration

### Requirement 5

**User Story:** As a student, I want Vietnamese language support in my documents, so that I can present in my native language.

#### Acceptance Criteria

1. WHEN creating LaTeX documents, THE System SHALL configure proper Vietnamese language support using appropriate packages
2. WHEN writing content, THE System SHALL use Vietnamese for main content with English for technical terms
3. WHEN formatting text, THE System SHALL ensure proper Vietnamese character encoding (UTF-8)
4. WHEN compiling documents, THE System SHALL use XeLaTeX or LuaLaTeX for proper Vietnamese font rendering
