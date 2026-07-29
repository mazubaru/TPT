import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io
import json

# ==========================================
# 1. Helper Functions (กำหนดไว้บนสุดกัน Error)
# ==========================================

def calculate_opportunity_score(w_type, grade):
    """คำนวณโอกาสทางการตลาด"""
    niche_data = {
        "Math Practice": {"competition": 80, "demand": 85},
        "Reading Comprehension": {"competition": 75, "demand": 88},
        "Phonics": {"competition": 70, "demand": 85},
        "Sight Words": {"competition": 90, "demand": 95},
        "Word Search": {"competition": 40, "demand": 60},
    }
    data = niche_data.get(w_type, {"competition": 50, "demand": 50})
    score = (data["demand"] * 0.6) + ((100 - data["competition"]) * 0.4)
    return int(score)

def generate_worksheet_content(api_key, w_type, grade, pages):
    """Generate worksheet content using Gemini"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""Create a simple JSON for a {grade} {w_type} worksheet with {pages} pages. 
    Return ONLY valid JSON with this structure:
    {{
        "title": "Worksheet Title",
        "objective": "Learning objective",
        "pages": [
            {{"page": 1, "questions": ["Question 1", "Question 2"]}}
        ]
    }}"""
    response = model.generate_content(prompt)
    clean_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_text)

# ==========================================
# 2. Streamlit UI Setup
# ==========================================

st.set_page_config(page_title="TPT Generator", page_icon="📚", layout="wide")
st.title("📚 TPT Worksheet Generator")
st.markdown("สร้างใบงานและข้อมูลสำหรับขายบน Teachers Pay Teachers แบบอัตโนมัติ")

# Sidebar
with st.sidebar:
    st.header("⚙️ ตั้งค่า")
    api_key = st.text_input("Gemini API Key", type="password", help="ใส่ API Key หรือเว้นว่างเพื่อใช้โหมดทดสอบ")
    
    st.divider()
    worksheet_type = st.selectbox("ประเภทใบงาน", ["Math Practice", "Reading Comprehension", "Phonics", "Sight Words", "Word Search"])
    grade_level = st.selectbox("ระดับชั้น", ["Kindergarten", "1st Grade", "2nd Grade", "3rd Grade"])
    num_pages = st.number_input("จำนวนหน้า", min_value=1, max_value=20, value=5)
    
    st.divider()
    if st.button("🎯 คำนวณคะแนนโอกาสทางการตลาด"):
        score = calculate_opportunity_score(worksheet_type, grade_level)
        st.metric("Opportunity Score", f"{score}/100")
        if score >= 80:
            st.success("โอกาสดีเยี่ยม! แนะนำให้ทำ")
        elif score >= 65:
            st.info("น่าสนใจ แต่ต้องมีจุดเด่นที่แตกต่าง")
        else:
            st.warning("การแข่งขันสูง พิจารณาหาจุดเด่นเพิ่มเติม")

# Main Content
if "worksheet_data" not in st.session_state:
    st.session_state.worksheet_data = None

tab1, tab2, tab3 = st.tabs(["📝 สร้างเนื้อหา", "🖼️ ตัวอย่างและ Export", "📊 ข้อมูลลงขาย TPT"])

with tab1:
    st.header("1. สร้างเนื้อหาใบงาน")
    if st.button("🚀 สร้างใบงานเลย!", type="primary"):
        with st.spinner("AI กำลังสร้างเนื้อหา..."):
            if not api_key:
                # โหมดทดสอบ (Demo Mode)
                st.session_state.worksheet_data = {
                    "title": f"{grade_level} {worksheet_type} Pack (Demo)",
                    "objective": "Practice core skills.",
                    "pages": [{"page": i+1, "questions": [f"Question {j} for page {i+1}" for j in range(1, 4)]} for i in range(num_pages)]
                }
                st.success("สร้างข้อมูลจำลองสำเร็จ! (ใส่ API Key เพื่อใช้ AI จริง)")
            else:
                try:
                    data = generate_worksheet_content(api_key, worksheet_type, grade_level, num_pages)
                    st.session_state.worksheet_data = data
                    st.success("✅ AI สร้างเนื้อหาสำเร็จ!")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")

    if st.session_state.worksheet_data:
        st.subheader("📝 เนื้อหาที่สร้างได้")
        st.json(st.session_state.worksheet_data)

with tab2:
    st.header("2. ตัวอย่างและ Export ไฟล์")
    if st.session_state.worksheet_data:
        st.info("ระบบจะสร้างไฟล์ PDF ตัวอย่างให้ทันที")
        
        pdf_buf = io.BytesIO()
        c = canvas.Canvas(pdf_buf, pagesize=letter)
        width, height = letter
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height - 1*inch, st.session_state.worksheet_data.get("title", "Worksheet"))
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, height - 1.3*inch, f"Objective: {st.session_state.worksheet_data.get('objective', '')}")
        
        y_pos = height - 1.8*inch
        for page in st.session_state.worksheet_data.get("pages", [])[:3]:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, y_pos, f"Page {page.get('page', '')}")
            y_pos -= 0.3*inch
            c.setFont("Helvetica", 12)
            for q in page.get("questions", []):
                c.drawString(1*inch, y_pos, f"• {q}")
                y_pos -= 0.25*inch
            y_pos -= 0.3*inch
            if y_pos < 1*inch:
                c.showPage()
                y_pos = height - 1*inch
        
        c.save()
        pdf_buf.seek(0)
        
        st.download_button("📥 ดาวน์โหลดไฟล์ PDF", pdf_buf, "TPT_Worksheet.pdf", "application/pdf")
    else:
        st.warning("กรุณาสร้างเนื้อหาในแท็บแรกก่อน")

with tab3:
    st.header("3. ข้อมูลสำหรับลงขาย TPT (SEO Optimized)")
    if st.session_state.worksheet_data:
        title = st.session_state.worksheet_data.get("title", "Worksheet")
        st.subheader("📌 Product Title")
        st.text_input("แนะนำ", f"{title} | No Prep {grade_level} Activities & Answer Key")
        
        st.subheader("🏷️ Categories & Tags")
        cols = st.columns(2)
        with cols[0]:
            st.write("**Grade:**", grade_level)
            st.write("**Subject:**", worksheet_type)
        with cols[1]:
            st.write("**Resource Type:**", "Worksheets, Printables")
            st.write("**Tags:**", f"{grade_level.lower()} {worksheet_type.lower()}, no prep, morning work")
            
        st.subheader("💰 Pricing Suggestion")
        price = 2.50 + (num_pages * 0.15)
        st.metric("ราคาที่แนะนำ", f"${price:.2f} USD")
    else:
        st.warning("กรุณาสร้างเนื้อหาในแท็บแรกก่อน")
