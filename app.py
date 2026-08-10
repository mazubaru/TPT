import streamlit as st
import streamlit.components.v1 as components
import os

# 1. ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="GridMind Worksheet Studio",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ซ่อนเมนูและ footer เริ่มต้นของ Streamlit (เพื่อให้เว็บดูสะอาดตา)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. โหลดไฟล์ HTML
# ใช้ os.path เพื่อให้หาไฟล์เจอไม่ว่าจะรันจากโฟลเดอร์ไหน
current_dir = os.path.dirname(os.path.abspath(__file__))
html_file_path = os.path.join(current_dir, 'index.html')

try:
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_code = f.read()
    
    # 4. แสดงผล HTML ใน Streamlit
    # height=1200 คือความสูงของ iframe, scrolling=True เพื่อให้เลื่อนหน้าได้
    components.html(html_code, height=1200, scrolling=True)

except FileNotFoundError:
    st.error("❌ **ไม่พบไฟล์ `index.html`**")
    st.warning("กรุณาบันทึกโค้ด HTML เป็นไฟล์ `index.html` แล้ววางไว้ในโฟลเดอร์เดียวกับไฟล์ `app.py` นี้")
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดไฟล์: {e}")
