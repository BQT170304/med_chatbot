# PubMed Screener

PubMed Screener là một ứng dụng hỗ trợ bởi AI, giúp người dùng phân tích và trích xuất thông tin quan trọng từ các tóm tắt nghiên cứu y sinh học. Công cụ này được thiết kế để hỗ trợ các nhà nghiên cứu, bác sĩ và sinh viên trong việc tìm kiếm và hiểu sâu hơn về các chủ đề khoa học phức tạp.

## Tính năng chính
- **Chatbot AI**: Trả lời các câu hỏi khoa học y sinh học.
- **Tóm tắt nghiên cứu**: Trích xuất thông tin từ PubMed.
- **Đơn giản hóa truy vấn**: Biến đổi các câu hỏi phức tạp thành truy vấn ngắn gọn.

## Cách cài đặt
1. Clone repository:
   ```bash
   git clone <repository-url>
   cd med-chatbot
   ```
2. Tạo và kích hoạt môi trường ảo:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Linux/MacOS
   venv\Scripts\activate     # Trên Windows
   ```
3. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

4. Tạo file .env và thêm các biến môi trường:
   ```bash
   GOOGLE_API_KEY="your-google-api-key"
   GEMINI_MODEL="your-model"
   ```


## Cách sử dụng
1. Chạy ứng dụng:
   ```bash
   cd app
   streamlit run app.py
   ```
