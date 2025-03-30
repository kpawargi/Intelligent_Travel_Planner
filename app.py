import streamlit as st
import requests
from fpdf import FPDF
import os
from dotenv import load_dotenv
from datetime import datetime
import zipfile
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_community.llms import HuggingFaceHub


# 🔓 Extract .streamlit folder if zipped
if not os.path.exists(".streamlit"):
    with zipfile.ZipFile(".streamlit.zip", 'r') as zip_ref:
        zip_ref.extractall(".")

# ✅ Load .env variables
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# ✅ Initialize LangChain LLM
llm = HuggingFaceHub(
    repo_id="mistralai/Mistral-7B-Instruct-v0.1",
    model_kwargs={"temperature": 0.7, "max_new_tokens": 2048},
    huggingfacehub_api_token=HF_API_TOKEN
)

# ✅ Setup LangChain memory and conversation
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()
if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        verbose=False
    )

# ✅ PDF generation function
def save_trip_plan_as_pdf(text, filename="trip_itinerary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    safe_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, safe_text)
    pdf.output(filename)

# ✅ Streamlit UI
st.set_page_config(page_title="Intelligent Travel Planner", layout="wide")
st.title("🧳 Intelligent Travel Planner Agent")

# 🎯 User inputs
col1, col2 = st.columns(2)
with col1:
    from_location = st.text_input("🏠 Your Current Location", placeholder="e.g., Mumbai")
    destination = st.text_input("🌍 Destination", placeholder="e.g., Manali")
    start_date = st.date_input("📅 Start Date")
with col2:
    end_date = st.date_input("📅 End Date")
    budget = st.text_input("💰 Budget (in INR)", placeholder="e.g., 5000")
    preferences = st.text_input("🎯 Preferences", placeholder="e.g., Adventure, Culture, Beaches")

generate_button = st.button("✈️ Generate Trip Plan")

# ✅ Generate and display AI trip plan
if generate_button:
    if from_location and destination and budget and preferences and start_date and end_date:
        user_prompt = (
            f"Create a detailed,day-wise travel itinerary for a trip from {from_location} to {destination}."
            f"The trip should start on {start_date.strftime('%B %d, %Y')} and end on {end_date.strftime('%B %d, %Y')}, "
            f"with a total budget of ₹{budget} INR. The traveller prefers a trip with the theme:{preferences.lower()}.\n"
            f"Provide a **day-wise breakdown** of the trip including:\n"
            f"- Top tourist attractions\n"
            f"- Recommended local food\n"
            f"- Suggested places to visit(such as markets,museums,temples etc.)\n"
            f"End with final tips for the trip."
        )

        with st.spinner("🧠 Generating trip itinerary..."):
            ai_response = st.session_state.conversation.run(user_prompt)

        st.subheader("📋 Your AI-Generated Trip Itinerary")
        st.write(ai_response)

        save_trip_plan_as_pdf(ai_response)
        with open("trip_itinerary.pdf", "rb") as f:
            st.download_button("📄 Download as PDF", f, file_name="trip_itinerary.pdf")

    else:
        st.warning("🚨 Please fill out all fields above.")

# 🧠 Follow-up Chat Section
st.markdown("---")
st.subheader("💬 Ask Follow-Up Questions")
follow_up = st.text_input("Ask a follow-up about your trip plan")

if follow_up:
    with st.spinner("💡 Thinking..."):
        response = st.session_state.conversation.run(user_prompt+"Also,"+follow_up)
        st.write("Sure,here is your updated travel itinerary: \n"+response)

