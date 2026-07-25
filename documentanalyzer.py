import time
import streamlit as st
from google import genai
from pypdf import PdfReader

# 1. Page Configuration
st.set_page_config(
    page_title="AI Document Analyzer", 
    page_icon="https://cdn-icons-png.flaticon.com/512/2814/2814668.png", 
    layout="centered"
)

st.title("📄 AI Contract & Document Analyzer")
st.write("Upload any PDF document and ask questions to get instant, accurate answers!")

# 2. Get API Key from Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("Gemini API Key is missing! Please configure it in Streamlit Secrets.")
else:
    # Initialize the Gemini Client
    client = genai.Client(api_key=api_key)

    # 3. File Uploader Component
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Read and extract text from PDF
        pdf_reader = PdfReader(uploaded_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
                
        st.success(f"File processed successfully! Total Pages: {len(pdf_reader.pages)}")
        
        # User Input Field
        user_query = st.text_input("What would you like to know from this document?", 
                                   placeholder="e.g., What are the main terms?")
        
        if st.button("Analyze & Answer"):
            if user_query:
                with st.spinner("Analyzing document and generating response..."):
                    prompt = f"""
                    You are an expert document analysis assistant. Based ONLY on the provided document text below, answer the user's question accurately and concisely.
                    If the answer is not contained within the text, explicitly state: "This information is not available in the provided document."

                    --- START DOCUMENT TEXT ---
                    {extracted_text[:10000]}
                    --- END DOCUMENT TEXT ---

                    User Question: {user_query}
                    """
                    
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            # API Request
                            response = client.models.generate_content(
                                model='gemini-2.0-flash',
                                contents=prompt,
                            )
                            st.markdown("### 🤖 Response:")
                            st.write(response.text)
                            break  # Success, exit loop
                            
                        except Exception as e:
                            error_msg = str(e)
                            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                                if attempt < max_retries - 1:
                                    st.warning("Rate limit reached. Retrying automatically in 15 seconds...")
                                    time.sleep(15)
                                else:
                                    st.error("Free quota limit reached. Please wait 1 minute before trying again.")
                            else:
                                st.error(f"An error occurred: {e}")
                                break
            else:
                st.warning("Please enter a question first.")