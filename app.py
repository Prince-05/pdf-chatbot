# app.py

import streamlit as st
from pdf_reader import build_qa_chain
import tempfile
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="📄 Ask your PDF", layout="wide")
st.title("💬 Ask Anything from Your PDF")
st.write("Upload a PDF, and start chatting!")

# if "chain" not in st.session_state:
#     st.session_state.chain = None

# pdf_file = st.file_uploader("Upload your PDF", type="pdf")
# if pdf_file:
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         tmp.write(pdf_file.read())
#         tmp_path = tmp.name

#     with st.spinner("Processing PDF..."):
#         st.session_state.chain = build_qa_chain(tmp_path)
#         st.success("PDF loaded. Ask away!")

# if st.session_state.chain:
#     query = st.text_input("Ask a question about your PDF:")
#     if st.button("Submit") and query:
#         with st.spinner("Thinking..."):
#             try:
#                 response = st.session_state.chain.invoke(query)
#                 st.markdown(f"**Answer:** {response}")
#             except Exception as e:
#                 st.error(f"Error: {str(e)}")
if "chain" not in st.session_state:
    st.session_state.chain = None
    st.session_state.last_uploaded_file = None  # 👈 to track current file

pdf_file = st.file_uploader("Upload your PDF", type="pdf")

if pdf_file is not None:
    # 👇 Check if it's a *new* PDF, not just re-submitting the same one
    if st.session_state.last_uploaded_file != pdf_file.name:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name

        with st.spinner("Processing PDF..."):
            try:
                st.session_state.chain = build_qa_chain(tmp_path)
                st.session_state.last_uploaded_file = pdf_file.name  # ✅ Save the file name
                st.success("PDF processed! Ask away 👇")
            except Exception as e:
                st.error(f"PDF processing failed: {str(e)}")
    else:
        st.info("PDF already processed. You can keep asking questions!")

# 👇 Use the saved chain
if st.session_state.chain:
    query = st.text_input("Ask a question about your PDF:")
    if st.button("Submit") and query:
        with st.spinner("Thinking..."):
            try:
                answer = st.session_state.chain.invoke(query)
                st.markdown(f"**Answer:** {answer}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

