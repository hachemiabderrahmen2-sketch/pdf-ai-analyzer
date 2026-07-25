import streamlit as st 
from google import genai
from pypdf import PdfReader

st.set_page_config (page_title ="AI Document Analyzer",page_icon = "https://cdn-icons-png.flaticon.com/512/2814/2814668.png",layout = "centered")

st.title("📁 AI Contract & Document Analyzer")
st.write("Upload any PDF document (contract, guide, report) and ask questions to get instant, accurate answers!")
import os

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("Gemini API Key is missing! Please configure it in Streamlit Secrets.")
else:
    client = genai.Client(api_key=api_key)

uploaded_file = st.file_uploader ("choose a PDF file", type = ["PDF"])

if uploaded_file is not None :
    pdf_reader = PdfReader(uploaded_file)
    extracted_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    st.success(f"File processed successfully! Total Pages: {len(pdf_reader.pages)}")

    user_query = st.text_input("What would you like to know from this document?",placeholder = "e.g., What are the cancellation terms? Summarize main points...")        

    if st.button("Analyze & Answer"):
        if user_query: 
            with st.spinner("Analyzing document and generating response..."): 
                try:
    
                    prompt =f"""You are an expert document analysis assistant. Based ONLY on the provided document text below, answer the user's question accurately and concisely. If the answer is not contained within the text, explicitly state: " This information is not available in the provided document."
                    --- START DOCUMENT TEXT ---
                    {extracted_text[:10000]}
                    --- END DOCUMENT TEXT --- 
                    User Question: {user_query}"""
                    response =client.models.generate_content(model='gemini-2.5-flash', contents=prompt,)
                    st.markdown("### 🤖 response:")
                    st.write(response.text)

                except Exception as e:
                    st.error(f"An error occurred while communicating with the service: {e}")    
        else: 
            st.warning("Please enter a question first.")            
            