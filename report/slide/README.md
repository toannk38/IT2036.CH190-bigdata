# Vietnam Stock AI Backend - Presentation Slides

## Hướng dẫn sử dụng trên Overleaf

### 1. Upload files lên Overleaf
- Upload tất cả files trong thư mục `report/slide/` lên Overleaf project
- Đảm bảo cấu trúc thư mục được giữ nguyên:
  ```
  main.tex
  sections/
    ├── 01-title.tex
    ├── 02-introduction.tex
    ├── 03-problem.tex
    ├── 04-architecture.tex
    ├── 05-components.tex
    ├── 06-implementation.tex
    ├── 07-demo.tex
    ├── 08-results.tex
    └── 09-conclusion.tex
  images/ (thư mục trống, có thể thêm hình ảnh sau)
  ```

### 2. Cấu hình Overleaf
- **Compiler**: Sử dụng pdfLaTeX (mặc định)
- **Main document**: `main.tex`
- Không cần thay đổi compiler vì đã được tối ưu cho pdfLaTeX

### 3. Tùy chỉnh thông tin cá nhân
Chỉnh sửa trong file `main.tex`:
```latex
\title{Vietnam Stock AI Backend}
\subtitle{Hệ thống phân tích chứng khoán Việt Nam sử dụng AI/ML}
\author{[Thay bằng tên của bạn]\\[Thay bằng mã số sinh viên]}
\institute{[Tên khoa - Chuyên ngành]\\[Tên trường đại học]}
```

### 4. Các tính năng đã được sửa
- ✅ Tương thích với pdfLaTeX (Overleaf default)
- ✅ Hỗ trợ tiếng Việt với babel package
- ✅ Giữ nguyên placeholders cho diagrams
- ✅ Cấu trúc slide chuyên nghiệp
- ✅ Code syntax highlighting
- ✅ Responsive layout với columns

### 5. Nội dung slide
1. **Title & TOC** - Trang bìa và mục lục
2. **Introduction** - Giới thiệu dự án
3. **Problem Statement** - Vấn đề nghiên cứu
4. **Architecture** - Kiến trúc hệ thống với TikZ diagrams
5. **Components** - Các thành phần chi tiết
6. **Implementation** - Triển khai và Airflow
7. **Demo** - Screenshots và API examples
8. **Results** - Kết quả đạt được
9. **Conclusion** - Kết luận và hướng phát triển

### 6. Thêm hình ảnh
- Tạo thư mục `images/` trong Overleaf
- Upload screenshots thực tế của hệ thống
- Thay thế placeholders bằng hình ảnh thực:
  ```latex
  % Thay thế placeholder
  % \textbf{[Placeholder for System Architecture Diagram]}
  % bằng:
  \includegraphics[width=0.8\textwidth]{images/architecture.png}
  ```

### 7. Compile và kiểm tra
- Click "Recompile" trong Overleaf
- Kiểm tra PDF output
- Sửa lỗi nếu có (thường là missing packages)

## Troubleshooting

### Lỗi thường gặp:
1. **Package not found**: Overleaf thường có sẵn các packages cần thiết
2. **Vietnamese characters**: Đảm bảo file được save với UTF-8 encoding
3. **TikZ errors**: Kiểm tra syntax của TikZ diagrams

### Liên hệ hỗ trợ:
- Kiểm tra Overleaf documentation
- Sử dụng Overleaf's built-in help system