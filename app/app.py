import streamlit as st
from metapub import PubMedFetcher
from components.agent import ChatAgent
from components.prompts import chat_prompt_template, qa_template
from components.llm import llm
from components.layout_extension import render_app_info
from backend.retriever import PubMedAbstractRetriever
from backend.data.local_data_store import LocalJSONStore
from backend.rag_pipeline.chromadb import ChromaDbRag
from backend.rag_pipeline.embeddings import GeminiEmbeddingModel
from backend.utils.query_classifier import classify_query
from backend.utils.query_handlers import get_handler_for_query_type
import os
from dotenv import load_dotenv
load_dotenv()

# Instantiate objects
embeddings = GeminiEmbeddingModel(api_key=os.getenv("GOOGLE_API_KEY"))
pubmed_client = PubMedAbstractRetriever(PubMedFetcher())
data_repository = LocalJSONStore(storage_folder_path="backend/data")
rag_client = ChromaDbRag(persist_directory="backend/chromadb_storage", embeddings=embeddings)
chat_agent = ChatAgent(prompt=chat_prompt_template, llm=llm)

def main():
    st.set_page_config(
        page_title="Pubmed Abstract Screener",
        page_icon='💬',
        layout='wide'
    )

    # Define columns - this will make layout split horizontally
    column_logo, column_app_info, column_answer = st.columns([1, 3, 4], gap="medium")

    # Place the logo in the first column
    with column_logo:
        st.image('../assets/chatbot_logo.png', width=150)

    # In the second column, place text explaining the purpose of the app and some example scientific questions that your user might ask.
    with column_app_info:

        # Runder app info including example questions as cues for the user
        render_app_info()

        # Section to enter scientific question
        st.header("Nhập câu hỏi của bạn")
        placeholder_text = "Nhập câu hỏi tại đây..."
        scientist_question = st.text_input("Câu hỏi của bạn là gì?", placeholder_text)
        get_response = st.button('Gửi câu hỏi')

        # Processing user question, fetching data
        if get_response:
            if scientist_question and scientist_question != placeholder_text:
                with st.spinner('Đang xử lý câu hỏi của bạn...'):
                    # Phân loại câu hỏi của người dùng
                    query_type = classify_query(scientist_question)
                    
                    with column_answer:
                        st.markdown(f"##### Trả lời cho câu hỏi: '{scientist_question}'")
                        
                        if query_type == "scientific":
                            # Xử lý câu hỏi khoa học sử dụng RAG pipeline
                            # Normalize query for comparison
                            normalized_query = scientist_question.strip().lower()

                            # Check if the query already exists in the database
                            query_list = data_repository.get_list_of_queries()
                            existing_query_id = next(
                                (qid for qid, qtext in query_list.items() if qtext.strip().lower() == normalized_query),
                                None
                            )

                            if existing_query_id:
                                # Query exists, retrieve vector index and skip fetching abstracts
                                st.write("Đã tìm thấy câu hỏi này trong cơ sở dữ liệu. Đang sử dụng dữ liệu có sẵn...")
                                vector_index = rag_client.get_vector_index_by_user_query(existing_query_id)
                            else:
                                # Query does not exist, fetch data from PubMed
                                with st.spinner('Đang tìm kiếm thông tin từ PubMed...'):
                                    retrieved_abstracts = pubmed_client.get_abstract_data(scientist_question)
                                    if not retrieved_abstracts:
                                        st.write('Không tìm thấy bài báo khoa học liên quan.')
                                        return
                                    # Save abstracts to storage and create vector index
                                    query_id = data_repository.save_dataset(retrieved_abstracts, scientist_question)
                                    documents = data_repository.create_document_list(retrieved_abstracts)
                                    rag_client.create_vector_index_for_user_query(documents, query_id)
                                    vector_index = rag_client.get_vector_index_by_user_query(query_id)

                            # Answer the user question and display the answer on the UI directly
                            retrieved_documents = chat_agent.retrieve_documents(vector_index, scientist_question)
                            chain = qa_template | llm
                            
                            with st.spinner('Đang tạo câu trả lời từ thông tin khoa học...'):
                                response = chain.invoke({
                                    "question": scientist_question,
                                    "retrieved_abstracts": retrieved_documents,
                                }).content
                                st.write(response)
                        else:
                            # Xử lý các loại câu hỏi khác (translation, summarization, general)
                            handler = get_handler_for_query_type(query_type)
                            response = handler(scientist_question)
                            st.write(response)

    # Beginning of the chatbot section
    # Display list of queries to select one to have a conversation about
    query_options = data_repository.get_list_of_queries()

    if query_options:
        st.divider()
        st.header("Lịch sử trò chuyện")
        selected_query = st.selectbox('Chọn câu hỏi đã hỏi trước đây', options=list(query_options.values()), key='selected_query')
        
        # Initialize chat about some query from the history of user questions
        if selected_query:
            selected_query_id = next(key for key, val in query_options.items() if val == selected_query)
            vector_index = rag_client.get_vector_index_by_user_query(selected_query_id)

            # Clear chat history when switching query to chat about
            if 'prev_selected_query' in st.session_state and st.session_state.prev_selected_query != selected_query:
                chat_agent.reset_history()

            st.session_state.prev_selected_query = selected_query

            # Start chat session
            chat_agent.start_conversation(vector_index, selected_query)


if __name__ == "__main__":
    main()