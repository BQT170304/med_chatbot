import streamlit as st
from components.agent import ChatAgent
from components.prompts import chat_prompt_template
from components.llm import llm

def main():
    st.set_page_config(
        page_title="Medical Screener",
        page_icon='💬',
        layout='wide'
    )

    col1, col2 = st.columns([1, 5])

    # Place the logo in the first column
    with col1:
        st.image('../assets/logo.webp', width=None)

    # In the second column, place text explaining the purpose of the app and some example scientific questions that your user might ask.
    with col2:
        st.title("PubMed Screener")
        st.markdown("""
            PubMed Screener là một công cụ hỗ trợ bởi AI, giúp bạn phân tích và trích xuất thông tin quan trọng từ các tóm tắt nghiên cứu y sinh học. 
            Công cụ này được thiết kế để hỗ trợ các nhà nghiên cứu, bác sĩ và sinh viên trong việc tìm kiếm và hiểu sâu hơn về các chủ đề khoa học phức tạp.
            
            #### Ví dụ một số câu hỏi khoa học về y sinh học:
            - Làm thế nào các kỹ thuật hình ảnh tiên tiến và các dấu ấn sinh học có thể được sử dụng để chẩn đoán sớm và theo dõi sự tiến triển của các rối loạn thoái hóa thần kinh?
            - Các ứng dụng tiềm năng của công nghệ tế bào gốc và y học tái tạo trong điều trị các bệnh thoái hóa thần kinh là gì, và những thách thức liên quan là gì?
            - Vai trò của hệ vi sinh vật đường ruột và trục ruột-não trong cơ chế bệnh sinh của bệnh tiểu đường loại 1 và loại 2 là gì, và làm thế nào để điều chỉnh các tương tác này để mang lại lợi ích điều trị?
            - Các cơ chế phân tử nào dẫn đến sự phát triển của kháng thuốc trong các liệu pháp ung thư nhắm mục tiêu, và làm thế nào để vượt qua các cơ chế kháng thuốc này?
        """)

    # This is the chatbot component
    chat_agent = ChatAgent(prompt=chat_prompt_template, llm=llm)
    chat_agent.start_conversation()

if __name__ == "__main__":
    main()