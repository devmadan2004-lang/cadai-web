import streamlit as st
import pandas as pd

# ---------------------------
# STREAMLIT SETUP
# ---------------------------
st.set_page_config(page_title="CADAi Estimator", page_icon="🤖")
st.title("🤖 CADAi – Interactive Conveyor Cost Estimator")

# ---------------------------
# SESSION STATE INITIALIZATION
# ---------------------------
if "modules" not in st.session_state:
    st.session_state.modules = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "module_prices" not in st.session_state:
    st.session_state.module_prices = {}
if "excel_uploaded" not in st.session_state:
    st.session_state.excel_uploaded = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{"role":"ai","text":"Hi! Upload your technical Excel and I will ask for part prices one by one."}]

# ---------------------------
# DISPLAY CHAT
# ---------------------------
for msg in st.session_state.chat_messages:
    if msg["role"] == "ai":
        st.markdown(f"**CADAi:** {msg['text']}")
    else:
        st.markdown(f"**You:** {msg['text']}")

# ---------------------------
# EXCEL UPLOADER
# ---------------------------
uploaded_file = st.file_uploader("Upload your technical Excel file", type=["xlsx"])
if uploaded_file and not st.session_state.excel_uploaded:
    df = pd.read_excel(uploaded_file)

    # Extract module names from 'Item' column
    if "Item" not in df.columns:
        st.session_state.chat_messages.append({"role":"ai","text":"❌ Excel must have a column named 'Item'!"})
    else:
        modules_list = df["Item"].dropna().unique().tolist()
        st.session_state.modules = modules_list
        st.session_state.excel_uploaded = True
        st.session_state.chat_messages.append({"role":"ai","text":f"✅ Excel received. I found {len(modules_list)} modules: {', '.join(modules_list)}"})
        st.session_state.chat_messages.append({"role":"ai","text":f"Let's start! What is the price of '{st.session_state.modules[0]}'?"})

    st.experimental_rerun()

# ---------------------------
# USER INPUT
# ---------------------------
user_input = st.text_input("Type here...", key="chat_input")

if user_input:
    # Save user message
    st.session_state.chat_messages.append({"role":"user","text":user_input})

    # If we are in the module price flow
    if st.session_state.excel_uploaded and st.session_state.current_index < len(st.session_state.modules):
        module_name = st.session_state.modules[st.session_state.current_index]
        try:
            price = float(user_input.strip())
        except ValueError:
            st.session_state.chat_messages.append({"role":"ai","text":"⚠️ Please enter a numeric price."})
            st.experimental_rerun()

        # Save price
        st.session_state.module_prices[module_name] = price
        st.session_state.current_index += 1

        # Ask next module or finish
        if st.session_state.current_index < len(st.session_state.modules):
            next_module = st.session_state.modules[st.session_state.current_index]
            st.session_state.chat_messages.append({"role":"ai","text":f"Next, what is the price of '{next_module}'?"})
        else:
            total = sum(st.session_state.module_prices.values())
            summary_text = "**✅ All module prices entered!**\n\n"
            for mod, pr in st.session_state.module_prices.items():
                summary_text += f"- {mod}: ₹{pr:.2f}\n"
            summary_text += f"\n**Total Project Cost: ₹{total:.2f}**"
            st.session_state.chat_messages.append({"role":"ai","text":summary_text})

    else:
        st.session_state.chat_messages.append({"role":"ai","text":"Upload Excel first and I will guide you through the modules."})

    # Clear input and rerun to refresh chat
    st.session_state.chat_input = ""
    st.experimental_rerun()