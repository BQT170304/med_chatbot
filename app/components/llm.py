import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Gemini API with the API key
gemini_api_key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("GEMINI_MODEL")

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)

llm = ChatGoogleGenerativeAI(
    model=model,
    temperature=0,
    max_tokens=None,
    timeout=None,
    api_key=gemini_api_key,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)

if __name__ == "__main__":
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that translates {input_language} to {output_language}.",
            ),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm
    response = chain.invoke(
        {
            "input_language": "English",
            "output_language": "Vietnamese",
            "input": "I love programming.",
        }
    )
    print(response.content)