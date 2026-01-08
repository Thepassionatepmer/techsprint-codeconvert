import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# 1. Configuration
st.set_page_config(page_title="CodeConvert | TechSprint 2.0", layout="wide")

# Sidebar for API Key (Safety first!)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg", width=150)
    api_key = st.text_input("Enter Google API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    
    selected_model = st.selectbox("Select Model", ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-2.5-flash"], index=0)

st.title("⚡ CodeConvert")
st.subheader("Modernize Legacy Code & Debug Screenshots Instantly")

# 2. Tabs for different features
tab1, tab2 = st.tabs(["🔀 Language Converter", "📸 Debug from Screenshot"])

# --- FEATURE 1: CODE CONVERTER ---
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        source_lang = st.selectbox("From", ["Java", "C++", "C", "JavaScript"])
        code_input = st.text_area("Paste Legacy Code Here", height=300)
    
    with col2:
        target_lang = st.selectbox("To", ["Python", "Go", "Rust", "Modern JS"])
        if st.button("🚀 Convert Code"):
            if not api_key:
                st.error("Please enter API Key in sidebar.")
            else:
                # The "Secret Sauce" Prompt
                prompt = f"""
                Act as a Senior Developer. Convert the following {source_lang} code to {target_lang}.
                Rules:
                1. Make the new code Pythonic/Modern.
                2. Do not add any comments.
                3. If there are bugs in the original, fix them in the new version.
                4. Output raw code only. Do not wrap in markdown code blocks.
                
                Code:
                {code_input}
                """
                with st.spinner("Converting logic..."):
                    try:
                        model = genai.GenerativeModel(selected_model)
                        response = model.generate_content(prompt)
                        
                        # Clean up markdown formatting if the model includes it
                        clean_text = response.text.strip()
                        match = re.search(r"```(?:\w+)?\n(.*?)```", clean_text, re.DOTALL)
                        if match:
                            clean_text = match.group(1).strip()
                            
                        st.code(clean_text, language="javascript" if target_lang == "Modern JS" else target_lang.lower())
                        st.success("Conversion Complete!")
                    except Exception as e:
                        error_str = str(e)
                        if "429" in error_str:
                            st.error(f"Quota exceeded for '{selected_model}'. Please switch to another model in the sidebar or wait a minute.")
                            st.markdown("[Check Usage & Quotas](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas)")
                        elif "404" in error_str:
                            st.error(f"Model not found: '{selected_model}'. It may not be available for your API key. Please select another model.")
                        else:
                            st.error(f"An error occurred with '{selected_model}': {e}")

# --- FEATURE 2: SCREENSHOT DEBUGGER (The "Wow" Factor) ---
with tab2:
    st.write("Upload a screenshot of a terminal error or a code snippet from a YouTube tutorial.")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Snippet", use_column_width=True)
        
        if st.button("🔍 Analyze & Fix"):
            if not api_key:
                st.error("Please enter API Key.")
            else:
                model = genai.GenerativeModel(selected_model)
                # Multimodal Prompt (Image + Text)
                prompt = "Analyze this image. If it's code, transcribe and refactor it. If it's an error message, explain the solution step-by-step."
                
                with st.spinner("Scanning pixels..."):
                    try:
                        response = model.generate_content([prompt, image])
                        st.markdown(response.text)
                    except Exception as e:
                        error_str = str(e)
                        if "429" in error_str:
                            st.error(f"Quota exceeded for '{selected_model}'. Please switch to another model in the sidebar or wait a minute.")
                            st.markdown("[Check Usage & Quotas](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas)")
                        elif "404" in error_str:
                            st.error(f"Model not found: '{selected_model}'. It may not be available for your API key. Please select another model.")
                        else:
                            st.error(f"An error occurred with '{selected_model}': {e}")