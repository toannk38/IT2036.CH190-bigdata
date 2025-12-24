# Requirements Document

## Introduction

Trang web frontend cho hệ thống Vietnam Stock AI Backend, cung cấp giao diện người dùng để truy cập và hiển thị dữ liệu phân tích cổ phiếu từ các API backend. Hệ thống sẽ cho phép người dùng xem thông tin tổng quan thị trường, phân tích chi tiết từng mã cổ phiếu, theo dõi cảnh báo và xem dữ liệu lịch sử.

## Glossary

- **Frontend_App**: Ứng dụng web React TypeScript
- **API_Backend**: Hệ thống backend Vietnam Stock AI hiện có
- **Stock_Symbol**: Mã cổ phiếu (VD: VIC, VCB)
- **Dashboard**: Trang chủ hiển thị tổng quan
- **Stock_Analysis**: Trang phân tích chi tiết cổ phiếu
- **Alert_System**: Hệ thống cảnh báo
- **Historical_Data**: Dữ liệu phân tích lịch sử
- **User**: Người dùng cuối sử dụng trang web

## Requirements

### Requirement 1: Dashboard Tổng Quan

**User Story:** Là một nhà đầu tư, tôi muốn xem tổng quan thị trường trên trang chủ, để có cái nhìn nhanh về tình hình chung.

#### Acceptance Criteria

1. WHEN User truy cập trang chủ, THE Frontend_App SHALL hiển thị dashboard với thông tin tổng quan
2. THE Frontend_App SHALL hiển thị danh sách các Stock_Symbol đang hoạt động từ API endpoint /symbols
3. WHEN dashboard được tải, THE Frontend_App SHALL hiển thị top 5 cảnh báo có mức độ ưu tiên cao nhất từ API endpoint /alerts
4. THE Frontend_App SHALL hiển thị thời gian cập nhật cuối cùng của dữ liệu
5. WHEN User click vào một Stock_Symbol, THE Frontend_App SHALL chuyển đến trang Stock_Analysis của mã đó

### Requirement 2: Phân Tích Chi Tiết Cổ Phiếu

**User Story:** Là một nhà đầu tư, tôi muốn xem phân tích chi tiết của từng mã cổ phiếu, để đưa ra quyết định đầu tư.

#### Acceptance Criteria

1. WHEN User truy cập trang phân tích với Stock_Symbol, THE Frontend_App SHALL gọi API endpoint /stock/{symbol}/summary
2. THE Frontend_App SHALL hiển thị thông tin giá hiện tại bao gồm open, close, high, low, volume
3. THE Frontend_App SHALL hiển thị kết quả phân tích AI/ML bao gồm trend prediction và technical score
4. THE Frontend_App SHALL hiển thị kết quả phân tích LLM bao gồm sentiment và summary
5. THE Frontend_App SHALL hiển thị final score và recommendation với màu sắc phù hợp (xanh cho BUY, đỏ cho SELL)
6. THE Frontend_App SHALL hiển thị component scores dưới dạng progress bar hoặc gauge chart
7. WHEN có alerts cho Stock_Symbol, THE Frontend_App SHALL hiển thị danh sách alerts với màu sắc theo priority

### Requirement 3: Tìm Kiếm Cổ Phiếu

**User Story:** Là một nhà đầu tư, tôi muốn tìm kiếm mã cổ phiếu cụ thể, để nhanh chóng truy cập thông tin cần thiết.

#### Acceptance Criteria

1. THE Frontend_App SHALL cung cấp search box trên header của trang web
2. WHEN User nhập Stock_Symbol vào search box, THE Frontend_App SHALL hiển thị gợi ý từ danh sách symbols đang hoạt động
3. WHEN User chọn một Stock_Symbol từ gợi ý, THE Frontend_App SHALL chuyển đến trang Stock_Analysis
4. THE Frontend_App SHALL hỗ trợ tìm kiếm theo cả mã cổ phiếu và tên công ty
5. WHEN User nhập mã không tồn tại, THE Frontend_App SHALL hiển thị thông báo "Không tìm thấy mã cổ phiếu"

### Requirement 4: Quản Lý Cảnh Báo

**User Story:** Là một nhà đầu tư, tôi muốn xem tất cả cảnh báo của hệ thống, để không bỏ lỡ thông tin quan trọng.

#### Acceptance Criteria

1. THE Frontend_App SHALL cung cấp trang Alerts hiển thị danh sách tất cả cảnh báo
2. WHEN trang Alerts được tải, THE Frontend_App SHALL gọi API endpoint /alerts với pagination
3. THE Frontend_App SHALL hiển thị alerts được sắp xếp theo priority (high > medium > low) và timestamp
4. THE Frontend_App SHALL hiển thị mỗi alert với symbol, message, priority và timestamp
5. THE Frontend_App SHALL sử dụng màu sắc khác nhau cho từng mức priority (đỏ cho high, vàng cho medium, xanh cho low)
6. THE Frontend_App SHALL cung cấp pagination controls để xem thêm alerts
7. WHEN User click vào symbol trong alert, THE Frontend_App SHALL chuyển đến trang Stock_Analysis

### Requirement 5: Dữ Liệu Lịch Sử

**User Story:** Là một nhà đầu tư, tôi muốn xem dữ liệu phân tích lịch sử của cổ phiếu, để hiểu xu hướng dài hạn.

#### Acceptance Criteria

1. THE Frontend_App SHALL cung cấp trang Historical Data với form chọn Stock_Symbol và khoảng thời gian
2. WHEN User chọn Stock_Symbol và date range, THE Frontend_App SHALL gọi API endpoint /stock/{symbol}/history
3. THE Frontend_App SHALL hiển thị dữ liệu lịch sử dưới dạng line chart cho final_score theo thời gian
4. THE Frontend_App SHALL hiển thị component_scores (technical, risk, sentiment) trên cùng một biểu đồ với các màu khác nhau
5. THE Frontend_App SHALL hiển thị recommendation history dưới dạng color-coded timeline
6. THE Frontend_App SHALL cho phép User zoom và pan trên biểu đồ để xem chi tiết
7. WHEN không có dữ liệu cho khoảng thời gian được chọn, THE Frontend_App SHALL hiển thị thông báo phù hợp

### Requirement 6: Giao Diện Responsive

**User Story:** Là một nhà đầu tư, tôi muốn sử dụng trang web trên các thiết bị khác nhau, để có thể theo dõi thị trường mọi lúc mọi nơi.

#### Acceptance Criteria

1. THE Frontend_App SHALL hiển thị chính xác trên desktop với độ phân giải từ 1024px trở lên
2. THE Frontend_App SHALL hiển thị chính xác trên tablet với độ phân giải từ 768px đến 1023px
3. THE Frontend_App SHALL hiển thị chính xác trên mobile với độ phân giải dưới 768px
4. WHEN hiển thị trên mobile, THE Frontend_App SHALL sử dụng hamburger menu cho navigation
5. THE Frontend_App SHALL đảm bảo tất cả text có thể đọc được trên màn hình nhỏ
6. THE Frontend_App SHALL đảm bảo tất cả buttons và links có kích thước phù hợp cho touch interface

### Requirement 7: Xử Lý Lỗi và Loading

**User Story:** Là một nhà đầu tư, tôi muốn được thông báo rõ ràng khi có lỗi hoặc đang tải dữ liệu, để hiểu tình trạng của hệ thống.

#### Acceptance Criteria

1. WHEN Frontend_App đang gọi API, THE Frontend_App SHALL hiển thị loading indicator phù hợp
2. WHEN API trả về lỗi 404 (symbol not found), THE Frontend_App SHALL hiển thị thông báo "Không tìm thấy mã cổ phiếu"
3. WHEN API trả về lỗi 500 (server error), THE Frontend_App SHALL hiển thị thông báo "Lỗi hệ thống, vui lòng thử lại sau"
4. WHEN không có kết nối internet, THE Frontend_App SHALL hiển thị thông báo "Không có kết nối mạng"
5. THE Frontend_App SHALL cung cấp nút "Thử lại" khi có lỗi
6. THE Frontend_App SHALL tự động retry API calls khi có lỗi network tạm thời
7. WHEN dữ liệu tải thành công, THE Frontend_App SHALL ẩn loading indicator và hiển thị dữ liệu

### Requirement 8: Navigation và Layout

**User Story:** Là một nhà đầu tư, tôi muốn dễ dàng điều hướng giữa các trang, để truy cập nhanh chóng các chức năng khác nhau.

#### Acceptance Criteria

1. THE Frontend_App SHALL cung cấp navigation bar với các menu: Dashboard, Alerts, Historical Data
2. THE Frontend_App SHALL hiển thị logo hoặc tên ứng dụng ở góc trái navigation bar
3. THE Frontend_App SHALL hiển thị search box ở góc phải navigation bar
4. THE Frontend_App SHALL highlight menu item hiện tại đang được xem
5. WHEN User click vào menu item, THE Frontend_App SHALL chuyển đến trang tương ứng
6. THE Frontend_App SHALL sử dụng React Router để quản lý routing
7. THE Frontend_App SHALL hiển thị breadcrumb navigation khi cần thiết
8. THE Frontend_App SHALL cung cấp footer với thông tin về ứng dụng và thời gian cập nhật