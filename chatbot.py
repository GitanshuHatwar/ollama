from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

# Initialize model and prompt (singleton pattern)
model = OllamaLLM(model="deepseek-r1")

template = """
You are a Government Chatbot 
build an LLM-Powered multilingual chatbot that provides real time query resolutions for citizens,
covering government scheme eligibility.

Here are some list of schemes: {scheme}
here are some questions to answer: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model


def get_chatbot_response(question: str) -> dict:
    """
    Get chatbot response for a given question
    
    Args:
        question (str): User's question about government schemes
        
    Returns:
        dict: {
            "answer": str,      # LLM generated response
            "schemes": list     # List of relevant scheme names
        }
    """
    try:
        # Retrieve relevant schemes
        docs = retriever.invoke(question)
        
        # Extract context and scheme names
        context = "\n".join([doc.page_content for doc in docs])
        
        # Extract scheme names (first few words from each document)
        scheme_names = []
        for doc in docs:
            # Try to extract scheme name (usually first 3-6 words)
            words = doc.page_content.split()
            if len(words) > 0:
                # Look for common scheme keywords
                scheme_name_parts = []
                for word in words[:7]:  # Check first 7 words
                    scheme_name_parts.append(word)
                    # Stop at common separators
                    if word.lower() in ['yojana', 'scheme', 'mission', 'abhiyan']:
                        break
                scheme_names.append(" ".join(scheme_name_parts))
        
        # Run the RAG chain
        answer = chain.invoke({"scheme": context, "question": question})
        
        return {
            "answer": answer,
            "schemes": scheme_names[:4]  # Return top 4 schemes
        }
        
    except Exception as e:
        print(f"Error in get_chatbot_response: {str(e)}")
        return {
            "answer": "Sorry, I encountered an error processing your question. Please try again.",
            "schemes": []
        }


# For testing this module independently
if __name__ == "__main__":
    print("Testing chatbot module...")
    
    test_questions = [
        "What schemes are available for women?",
        "List farmer schemes",
        "Which schemes support senior citizens?"
    ]
    
    for q in test_questions:
        print(f"\nQ: {q}")
        response = get_chatbot_response(q)
        print(f"A: {response['answer'][:200]}...")
        print(f"Schemes: {response['schemes']}")