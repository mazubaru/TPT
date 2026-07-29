import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import Image as RLImage, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont
import io
import json
import zipfile
from datetime import datetime
import random

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================

THEMES = {
    "Clean Classroom": {
        "primary": "#4A90E2",
        "secondary": "#50C878",
        "accent": "#FFD93D",
        "bg": "#FFFFFF",
        "text": "#333333"
    },
    "Soft Pastel": {
        "primary": "#FFB3BA",
        "secondary": "#BAFFC9",
        "accent": "#BAE1FF",
        "bg": "#FFFFFF",
        "text": "#555555"
    },
    "Bright Elementary": {
        "primary": "#FF6B6B",
        "secondary": "#4ECDC4",
        "accent": "#FFE66D",
        "bg": "#FFFFFF",
        "text": "#2C3E50"
    },
    "Space": {
        "primary": "#2C3E50",
        "secondary": "#8E44AD",
        "accent": "#F39C12",
        "bg": "#1A1A2E",
        "text": "#FFFFFF"
    },
    "Ocean": {
        "primary": "#006994",
        "secondary": "#00A8CC",
        "accent": "#F7B538",
        "bg": "#E0F7FA",
        "text": "#006064"
    }
}

WORKSHEET_TYPES = {
    "Math Practice": {
        "icon": "🔢",
        "description": "Addition, subtraction, multiplication, division practice"
    },
    "Reading Comprehension": {
        "icon": "📖",
        "description": "Reading passages with comprehension questions"
    },
    "Phonics": {
        "icon": "🔤",
        "description": "Letter sounds, CVC words, blends, digraphs"
    },
    "Sight Words": {
        "icon": "👁️",
        "description": "High-frequency word recognition and practice"
    },
    "Word Search": {
        "icon": "🔍",
        "description": "Find hidden words in a letter grid"
    },
    "Tracing": {
        "icon": "✏️",
        "description": "Letter and number tracing practice"
    }
}

GRADE_LEVELS = [
    "Pre-K", "Kindergarten", "1st Grade", "2nd Grade", 
    "3rd Grade", "4th Grade", "5th Grade"
]

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def calculate_opportunity_score(w_type, grade):
    """คำนวณโอกาสทางการตลาด"""
    niche_data = {
        "Math Practice": {"competition": 80, "demand": 85},
        "Reading Comprehension": {"competition": 75, "demand": 88},
        "Phonics": {"competition": 70, "demand": 85},
        "Sight Words": {"competition": 90, "demand": 95},
        "Word Search": {"competition": 40, "demand": 60},
        "Tracing": {"competition": 60, "demand": 75},
    }
    data = niche_data.get(w_type, {"competition": 50, "demand": 50})
    score = (data["demand"] * 0.6) + ((100 - data["competition"]) * 0.4)
    return int(score)

def generate_worksheet_content(api_key, w_type, grade, pages, theme):
    """Generate worksheet content using Gemini"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""Create a complete educational worksheet for {grade} students.
Type: {w_type}
Theme: {theme}
Pages: {pages}

Return ONLY valid JSON with this exact structure:
{{
    "title": "Worksheet Title",
    "objective": "Learning objective",
    "description": "Brief description",
    "skills": ["skill1", "skill2", "skill3"],
    "pages": [
        {{
            "page": 1,
            "title": "Page Title",
            "instructions": "Clear student directions",
            "questions": [
                {{
                    "id": 1,
                    "question": "Question text",
                    "answer": "Correct answer",
                    "type": "fill_blank|multiple_choice|short_answer"
                }}
            ],
            "illustration": "Description of illustration (e.g., 'cute cartoon animals')"
        }}
    ],
    "total_questions": 0
}}

Make content age-appropriate, engaging, and educationally valuable.
All content must be in English."""
    
    response = model.generate_content(prompt)
    clean_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_text)

def generate_listing(api_key, worksheet_data, grade, w_type, pages):
    """Generate TPT listing using Gemini"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""Create a professional TPT product listing for this worksheet:
Title: {worksheet_data.get('title', '')}
Grade: {grade}
Subject: {w_type}
Pages: {pages}
Objective: {worksheet_data.get('objective', '')}
Skills: {', '.join(worksheet_data.get('skills', []))}

Return ONLY valid JSON:
{{
    "title": "SEO-optimized title (Primary Skill + Grade + Resource Type + Feature)",
    "description": "Professional description with: opening, what's included, skills, how to use, differentiation, file info",
    "categories": ["Grade X", "Subject", "Resource Type"],
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "standards": ["CCSS.X.X.X"],
    "price": 3.50,
    "teaching_duration": "1 week",
    "total_pages": {pages + 2}
}}

Write in natural American English. Focus on buyer search intent."""
    
    response = model.generate_content(prompt)
    clean_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_text)

def create_cartoon_illustration(prompt, theme_colors, size=(800, 600)):
    """สร้างภาพประกอบการ์ตูนแบบง่ายๆ ด้วย shapes"""
    img = Image.new('RGB', size, color=theme_colors['bg'])
    draw = ImageDraw.Draw(img)
    
    # สร้างภาพประกอบแบบ simple cartoon ด้วย shapes
    # (ใน production ควรใช้ image generation API จริง)
    
    # วาด background pattern
    for i in range(0, size[0], 50):
        for j in range(0, size[1], 50):
            if random.random() > 0.7:
                draw.ellipse([i, j, i+20, j+20], fill=theme_colors['accent'])
    
    # วาดตัวละครหลัก (simple cartoon)
    # ตัว
    draw.ellipse([300, 200, 500, 450], fill=theme_colors['primary'])
    # หัว
    draw.ellipse([350, 100, 450, 200], fill=theme_colors['primary'])
    # ตา
    draw.ellipse([370, 130, 390, 150], fill='white')
    draw.ellipse([410, 130, 430, 150], fill='white')
    draw.ellipse([375, 135, 385, 145], fill='black')
    draw.ellipse([415, 135, 425, 145], fill='black')
    # ปาก
    draw.arc([380, 160, 420, 180], 0, 180, fill='black', width=2)
    
    # เพิ่ม text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # เพิ่ม caption
    caption = prompt[:50] if len(prompt) > 50 else prompt
    draw.text((size[0]//2, size[1] - 50), caption, fill=theme_colors['text'], 
              font=font, anchor="mm")
    
    return img

def create_thumbnail(worksheet_data, theme_colors, thumbnail_type, size=(1500, 1500)):
    """สร้าง Thumbnail สำหรับ TPT"""
    img = Image.new('RGB', size, color=theme_colors['primary'])
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    
    if thumbnail_type == 1:  # Main Cover
        # Background
        draw.rectangle([0, 0, size[0], size[1]], fill=theme_colors['primary'])
        
        # Title
        title = worksheet_data.get('title', 'Worksheet')
        draw.text((size[0]//2, 300), title, fill='white', font=title_font, anchor="mm")
        
        # Grade
        grade = worksheet_data.get('grade', 'Grade Level')
        draw.text((size[0]//2, 500), grade, fill='white', font=body_font, anchor="mm")
        
        # Type
        w_type = worksheet_data.get('type', 'Worksheet')
        draw.text((size[0]//2, 700), w_type, fill='white', font=body_font, anchor="mm")
        
        # Decorative elements
        draw.ellipse([100, 100, 300, 300], fill=theme_colors['accent'])
        draw.ellipse([1200, 100, 1400, 300], fill=theme_colors['secondary'])
        
    elif thumbnail_type == 2:  # What's Included
        draw.rectangle([0, 0, size[0], size[1]], fill=theme_colors['secondary'])
        
        draw.text((size[0]//2, 200), "What's Included:", fill='white', 
                 font=title_font, anchor="mm")
        
        pages = worksheet_data.get('total_pages', 10)
        draw.text((size[0]//2, 400), f"✓ {pages} Student Pages", fill='white', 
                 font=body_font, anchor="mm")
        draw.text((size[0]//2, 550), "✓ Answer Key", fill='white', 
                 font=body_font, anchor="mm")
        draw.text((size[0]//2, 700), "✓ No Prep Required", fill='white', 
                 font=body_font, anchor="mm")
        
    elif thumbnail_type == 3:  # Skills
        draw.rectangle([0, 0, size[0], size[1]], fill=theme_colors['accent'])
        
        draw.text((size[0]//2, 200), "Skills Covered:", fill='black', 
                 font=title_font, anchor="mm")
        
        skills = worksheet_data.get('skills', ['Skill 1', 'Skill 2', 'Skill 3'])
        y_pos = 400
        for skill in skills[:3]:
            draw.text((size[0]//2, y_pos), f"• {skill}", fill='black', 
                     font=body_font, anchor="mm")
            y_pos += 150
            
    elif thumbnail_type == 4:  # Features
        draw.rectangle([0, 0, size[0], size[1]], fill=theme_colors['bg'])
        
        draw.text((size[0]//2, 200), "Features:", fill=theme_colors['text'], 
                 font=title_font, anchor="mm")
        
        features = [
            "✓ Print & Go",
            "✓ Answer Key Included",
            "✓ Standards Aligned",
            "✓ Differentiated"
        ]
        
        y_pos = 400
        for feature in features:
            draw.text((size[0]//2, y_pos), feature, fill=theme_colors['text'], 
                     font=body_font, anchor="mm")
            y_pos += 150
    
    return img

def generate_pdf(worksheet_data, theme_colors, paper_size="letter", include_answer_key=True):
    """Generate professional PDF with illustrations"""
    buffer = io.BytesIO()
    
    if paper_size == "letter":
        size = letter
    else:
        size = A4
    
    c = canvas.Canvas(buffer, pagesize=size)
    width, height = size
    
    # สร้างแต่ละหน้า
    for i, page in enumerate(worksheet_data.get('pages', [])):
        # Background
        c.setFillColor(HexColor(theme_colors['bg']))
        c.rect(0, 0, width, height, fill=1)
        
        # Header with color
        c.setFillColor(HexColor(theme_colors['primary']))
        c.rect(0, height - 1.5*inch, width, 1.5*inch, fill=1)
        
        # Title
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont("Helvetica-Bold", 24)
        c.drawString(0.75*inch, height - 1*inch, page.get('title', f'Page {i+1}'))
        
        # Instructions
        c.setFillColor(HexColor(theme_colors['text']))
        c.setFont("Helvetica", 12)
        y_pos = height - 2*inch
        c.drawString(0.75*inch, y_pos, page.get('instructions', ''))
        
        # Illustration (ถ้ามี)
        if 'illustration' in page:
            try:
                illustration = create_cartoon_illustration(
                    page['illustration'], 
                    theme_colors,
                    size=(400, 300)
                )
                img_buffer = io.BytesIO()
                illustration.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                img = RLImage(img_buffer, width=3*inch, height=2.25*inch)
                img.drawOn(c, 0.75*inch, y_pos - 2.5*inch)
                y_pos -= 3*inch
            except:
                pass
        
        # Questions
        c.setFont("Helvetica", 11)
        c.setFillColor(HexColor(theme_colors['text']))
        
        for q in page.get('questions', []):
            q_text = f"{q.get('id')}. {q.get('question', '')}"
            
            # Wrap text if too long
            if len(q_text) > 80:
                lines = [q_text[i:i+80] for i in range(0, len(q_text), 80)]
                for line in lines:
                    c.drawString(0.75*inch, y_pos, line)
                    y_pos -= 0.2*inch
            else:
                c.drawString(0.75*inch, y_pos, q_text)
            
            y_pos -= 0.3*inch
            
            # Answer space
            c.setStrokeColor(HexColor(theme_colors['secondary']))
            c.setLineWidth(1)
            c.line(1*inch, y_pos, 7*inch, y_pos)
            y_pos -= 0.5*inch
            
            # New page if needed
            if y_pos < 1*inch:
                c.showPage()
                y_pos = height - 1*inch
                c.setFont("Helvetica", 11)
                c.setFillColor(HexColor(theme_colors['text']))
        
        # Footer
        c.setFillColor(HexColor('#999999'))
        c.setFont("Helvetica", 8)
        c.drawString(0.75*inch, 0.5*inch, f"Page {i+1}")
        
        c.showPage()
    
    # Answer Key
    if include_answer_key and 'pages' in worksheet_data:
        c.setFillColor(HexColor(theme_colors['bg']))
        c.rect(0, 0, width, height, fill=1)
        
        c.setFillColor(HexColor(theme_colors['primary']))
        c.setFont("Helvetica-Bold", 20)
        c.drawString(0.75*inch, height - 1*inch, "Answer Key")
        
        c.setFillColor(HexColor(theme_colors['text']))
        c.setFont("Helvetica", 11)
        y_pos = height - 1.5*inch
        
        for page in worksheet_data.get('pages', []):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(0.75*inch, y_pos, f"Page {page.get('page', '')}")
            y_pos -= 0.3*inch
            
            c.setFont("Helvetica", 10)
            for q in page.get('questions', []):
                answer_text = f"{q.get('id')}. {q.get('answer', '')}"
                
                # Wrap text
                if len(answer_text) > 80:
                    lines = [answer_text[i:i+80] for i in range(0, len(answer_text), 80)]
                    for line in lines:
                        c.drawString(1*inch, y_pos, line)
                        y_pos -= 0.2*inch
                else:
                    c.drawString(1*inch, y_pos, answer_text)
                    y_pos -= 0.25*inch
                
                if y_pos < 1*inch:
                    c.showPage()
                    y_pos = height - 1*inch
                    c.setFont("Helvetica", 10)
            
            y_pos -= 0.2*inch
        
        c.showPage()
    
    c.save()
    buffer.seek(0)
    return buffer

def create_preview_pdf(worksheet_data, theme_colors):
    """สร้าง Preview PDF สำหรับ TPT"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Cover page
    c.setFillColor(HexColor(theme_colors['primary']))
    c.rect(0, 0, width, height, fill=1)
    
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height - 3*inch, worksheet_data.get('title', 'Worksheet'))
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height - 4*inch, worksheet_data.get('objective', ''))
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 6*inch, "PREVIEW")
    
    c.showPage()
    
    # What's included page
    c.setFillColor(HexColor(theme_colors['bg']))
    c.rect(0, 0, width, height, fill=1)
    
    c.setFillColor(HexColor(theme_colors['primary']))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(0.75*inch, height - 1*inch, "What's Included:")
    
    c.setFillColor(HexColor(theme_colors['text']))
    c.setFont("Helvetica", 14)
    y_pos = height - 1.8*inch
    
    pages = len(worksheet_data.get('pages', []))
    c.drawString(0.75*inch, y_pos, f"✓ {pages} Student Activity Pages")
    y_pos -= 0.4*inch
    c.drawString(0.75*inch, y_pos, "✓ Complete Answer Key")
    y_pos -= 0.4*inch
    c.drawString(0.75*inch, y_pos, "✓ No Prep Required")
    y_pos -= 0.4*inch
    c.drawString(0.75*inch, y_pos, "✓ Print & Go Format")
    
    c.showPage()
    
    # Sample pages (แสดงแค่ 2 หน้าแรก)
    for i, page in enumerate(worksheet_data.get('pages', [])[:2]):
        c.setFillColor(HexColor(theme_colors['bg']))
        c.rect(0, 0, width, height, fill=1)
        
        # Header
        c.setFillColor(HexColor(theme_colors['primary']))
        c.rect(0, height - 1.5*inch, width, 1.5*inch, fill=1)
        
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont("Helvetica-Bold", 20)
        c.drawString(0.75*inch, height - 1*inch, page.get('title', f'Sample Page {i+1}'))
        
        # Watermark
        c.setFillColor(HexColor('#CCCCCC'))
        c.setFont("Helvetica-Bold", 72)
        c.drawCentredString(width/2, height/2, "PREVIEW")
        
        # Content
        c.setFillColor(HexColor(theme_colors['text']))
        c.setFont("Helvetica", 12)
        y_pos = height - 2*inch
        c.drawString(0.75*inch, y_pos, page.get('instructions', ''))
        
        c.showPage()
    
    c.save()
    buffer.seek(0)
    return buffer

def create_complete_package(worksheet_data, listing_data, theme_colors, paper_size):
    """สร้าง ZIP package สมบูรณ์"""
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Student worksheets PDF
        pdf_buffer = generate_pdf(worksheet_data, theme_colors, paper_size, include_answer_key=True)
        zip_file.writestr("Student_Worksheets_with_Answer_Key.pdf", pdf_buffer.getvalue())
        
        # Preview PDF
        preview_buffer = create_preview_pdf(worksheet_data, theme_colors)
        zip_file.writestr("Product_Preview.pdf", preview_buffer.getvalue())
        
        # Thumbnails
        for i in range(1, 5):
            thumb = create_thumbnail(worksheet_data, theme_colors, i)
            img_buffer = io.BytesIO()
            thumb.save(img_buffer, format='JPEG', quality=95)
            zip_file.writestr(f"Thumbnail_{i:02d}.jpg", img_buffer.getvalue())
        
        # Listing information
        listing_text = f"""TITLE:
{listing_data.get('title', '')}

DESCRIPTION:
{listing_data.get('description', '')}

CATEGORIES:
{', '.join(listing_data.get('categories', []))}

TAGS:
{', '.join(listing_data.get('tags', []))}

STANDARDS:
{chr(10).join(listing_data.get('standards', []))}

PRICE: ${listing_data.get('price', 3.50)}

TEACHING DURATION: {listing_data.get('teaching_duration', 'N/A')}

TOTAL PAGES: {listing_data.get('total_pages', 0)}
"""
        zip_file.writestr("Listing_Information.txt", listing_text)
        
        # Project metadata
        metadata = {
            "created": datetime.now().isoformat(),
            "worksheet_data": worksheet_data,
            "listing_data": listing_data,
            "theme": theme_colors
        }
        zip_file.writestr("Project_Metadata.json", json.dumps(metadata, indent=2))
    
    buffer.seek(0)
    return buffer

# ==========================================
# 3. STREAMLIT UI
# ==========================================

st.set_page_config(
    page_title="TPT Worksheet Generator Pro",
    page_icon="📚",
    layout="wide"
)

st.title("📚 TPT Worksheet Generator Pro")
st.markdown("**สร้างใบงานพร้อมภาพประกอบสวยงาม สำหรับขายบน Teachers Pay Teachers**")
st.markdown("✅ AI สร้างเนื้อหาทั้งหมด | ✅ ภาพประกอบอัตโนมัติ | ✅ PDF สวยงาม | ✅ Thumbnail 4 แบบ | ✅ Export ZIP สมบูรณ์")

# Sidebar
with st.sidebar:
    st.header("⚙️ ตั้งค่า")
    api_key = st.text_input(
        "Gemini API Key", 
        type="password",
        help="ใส่ API Key ของคุณจาก https://aistudio.google.com/app/apikey"
    )
    
    st.divider()
    
    worksheet_type = st.selectbox(
        "ประเภทใบงาน",
        list(WORKSHEET_TYPES.keys()),
        format_func=lambda x: f"{WORKSHEET_TYPES[x]['icon']} {x}"
    )
    
    grade_level = st.selectbox("ระดับชั้น", GRADE_LEVELS)
    
    num_pages = st.number_input("จำนวนหน้า", min_value=1, max_value=30, value=5)
    
    theme = st.selectbox("ธีมการออกแบบ", list(THEMES.keys()))
    
    paper_size = st.radio("ขนาดกระดาษ", ["US Letter", "A4"])
    
    include_answer_key = st.checkbox("รวม Answer Key", value=True)
    
    st.divider()
    
    if st.button("🎯 คำนวณคะแนนโอกาส"):
        score = calculate_opportunity_score(worksheet_type, grade_level)
        st.metric("Opportunity Score", f"{score}/100")
        
        if score >= 80:
            st.success("โอกาสดีเยี่ยม! แนะนำให้ทำ")
        elif score >= 65:
            st.info("น่าสนใจ ต้องมีจุดเด่นที่แตกต่าง")
        else:
            st.warning("การแข่งขันสูง พิจารณาหาจุดเด่นเพิ่มเติม")

# Main Content
if "worksheet_data" not in st.session_state:
    st.session_state.worksheet_data = None

if "listing_data" not in st.session_state:
    st.session_state.listing_data = None

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 สร้างเนื้อหา",
    "🎨 ตัวอย่างและ Preview",
    "📊 TPT Listing",
    "🖼️ Thumbnails",
    "💾 Export Package"
])

with tab1:
    st.header("1. สร้างเนื้อหาใบงาน")
    
    if st.button("🚀 สร้างใบงานเลย!", type="primary"):
        if not api_key:
            st.error("กรุณาใส่ Gemini API Key ในแถบด้านซ้าย")
        else:
            with st.spinner("🤖 AI กำลังสร้างเนื้อหา... (อาจใช้เวลา 30-60 วินาที)"):
                try:
                    data = generate_worksheet_content(
                        api_key, worksheet_type, grade_level, num_pages, theme
                    )
                    data['grade'] = grade_level
                    data['type'] = worksheet_type
                    st.session_state.worksheet_data = data
                    st.success("✅ สร้างเนื้อหาสำเร็จ!")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
                    st.info("ลองใหม่อีกครั้ง หรือตรวจสอบ API Key")
    
    if st.session_state.worksheet_data:
        st.subheader("📝 เนื้อหาที่สร้างได้")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Title:** {st.session_state.worksheet_data.get('title', '')}")
            st.write(f"**Grade:** {st.session_state.worksheet_data.get('grade', '')}")
            st.write(f"**Type:** {st.session_state.worksheet_data.get('type', '')}")
        
        with col2:
            st.write(f"**Objective:** {st.session_state.worksheet_data.get('objective', '')}")
            st.write(f"**Total Questions:** {st.session_state.worksheet_data.get('total_questions', 0)}")
        
        st.write(f"**Skills:** {', '.join(st.session_state.worksheet_data.get('skills', []))}")
        
        with st.expander("ดูเนื้อหาทั้งหมด (JSON)"):
            st.json(st.session_state.worksheet_data)

with tab2:
    st.header("2. ตัวอย่างและ Preview")
    
    if st.session_state.worksheet_data:
        theme_colors = THEMES.get(theme, THEMES["Clean Classroom"])
        
        st.info("สร้าง PDF ตัวอย่างพร้อมภาพประกอบ")
        
        if st.button("📄 สร้าง PDF ตัวอย่าง", type="primary"):
            with st.spinner("กำลังสร้าง PDF..."):
                try:
                    pdf_buffer = generate_pdf(
                        st.session_state.worksheet_data,
                        theme_colors,
                        paper_size.lower().replace(' ', ''),
                        include_answer_key
                    )
                    
                    st.download_button(
                        "📥 ดาวน์โหลด PDF",
                        pdf_buffer,
                        f"TPT_{worksheet_type.replace(' ', '_')}_{grade_level.replace(' ', '_')}.pdf",
                        "application/pdf"
                    )
                    st.success("✅ สร้าง PDF สำเร็จ!")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
    else:
        st.warning("กรุณาสร้างเนื้อหาในแท็บแรกก่อน")

with tab3:
    st.header("3. TPT Listing Generator")
    
    if st.session_state.worksheet_data:
        if st.button("📊 สร้าง Listing", type="primary"):
            if not api_key:
                st.error("กรุณาใส่ Gemini API Key")
            else:
                with st.spinner("กำลังสร้าง Listing..."):
                    try:
                        listing = generate_listing(
                            api_key,
                            st.session_state.worksheet_data,
                            grade_level,
                            worksheet_type,
                            num_pages
                        )
                        st.session_state.listing_data = listing
                        st.success("✅ สร้าง Listing สำเร็จ!")
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {e}")
        
        if st.session_state.listing_data:
            st.subheader("📌 Product Title")
            st.text_area("Recommended Title", st.session_state.listing_data.get('title', ''), height=100)
            
            st.subheader("📝 Description")
            st.text_area("Description", st.session_state.listing_data.get('description', ''), height=400)
            
            st.subheader("🏷️ Categories & Tags")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Categories:**")
                st.write(", ".join(st.session_state.listing_data.get('categories', [])))
                st.write("**Standards:**")
                st.write(", ".join(st.session_state.listing_data.get('standards', [])))
            
            with col2:
                st.write("**Tags:**")
                st.write(", ".join(st.session_state.listing_data.get('tags', [])))
            
            st.subheader("💰 Pricing")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Suggested Price", f"${st.session_state.listing_data.get('price', 3.50)}")
            with col2:
                st.metric("Teaching Duration", st.session_state.listing_data.get('teaching_duration', 'N/A'))
            with col3:
                st.metric("Total Pages", st.session_state.listing_data.get('total_pages', 0))
    else:
        st.warning("กรุณาสร้างเนื้อหาในแท็บแรกก่อน")

with tab4:
    st.header("4. Thumbnails")
    
    if st.session_state.worksheet_data:
        theme_colors = THEMES.get(theme, THEMES["Clean Classroom"])
        
        st.info("สร้าง Thumbnail 4 แบบสำหรับ TPT")
        
        if st.button("🖼️ สร้าง Thumbnails", type="primary"):
            with st.spinner("กำลังสร้าง Thumbnails..."):
                try:
                    thumbnails = []
                    for i in range(1, 5):
                        thumb = create_thumbnail(
                            st.session_state.worksheet_data,
                            theme_colors,
                            i
                        )
                        thumbnails.append(thumb)
                    
                    cols = st.columns(2)
                    for i, thumb in enumerate(thumbnails):
                        with cols[i % 2]:
                            st.image(thumb, caption=f"Thumbnail {i+1}", use_column_width=True)
                            
                            # Download button
                            img_buffer = io.BytesIO()
                            thumb.save(img_buffer, format='JPEG', quality=95)
                            img_buffer.seek(0)
                            
                            st.download_button(
                                f"📥 Download Thumbnail {i+1}",
                                img_buffer.getvalue(),
                                f"Thumbnail_{i+1:02d}.jpg",
                                "image/jpeg",
                                key=f"thumb_{i}"
                            )
                    
                    st.success("✅ สร้าง Thumbnails สำเร็จ!")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
    else:
        st.warning("กรุณาสร้างเนื้อหาในแท็บแรกก่อน")

with tab5:
    st.header("5. Export Complete Package")
    
    if st.session_state.worksheet_data and st.session_state.listing_data:
        st.write("**ระบบจะสร้างไฟล์ทั้งหมดใน ZIP package:**")
        st.write("- ✅ Student Worksheets PDF (พร้อม Answer Key)")
        st.write("- ✅ Product Preview PDF")
        st.write("- ✅ 4 Thumbnails (JPG)")
        st.write("- ✅ Listing Information (TXT)")
        st.write("- ✅ Project Metadata (JSON)")
        
        if st.button("💾 Export Everything", type="primary"):
            with st.spinner("กำลังสร้าง package..."):
                try:
                    theme_colors = THEMES.get(theme, THEMES["Clean Classroom"])
                    
                    package = create_complete_package(
                        st.session_state.worksheet_data,
                        st.session_state.listing_data,
                        theme_colors,
                        paper_size.lower().replace(' ', '')
                    )
                    
                    st.download_button(
                        "📥 Download Complete Package (ZIP)",
                        package,
                        f"TPT_{worksheet_type.replace(' ', '_')}_{grade_level.replace(' ', '_')}_Package.zip",
                        "application/zip"
                    )
                    
                    st.success("✅ สร้าง Package สำเร็จ! พร้อมอัปโหลดขึ้น TPT")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
    else:
        st.warning("กรุณาสร้างเนื้อหาและ Listing ก่อน")

# Footer
st.divider()
st.caption("TPT Worksheet Generator Pro | Built with Streamlit & Gemini AI | AI-Generated Content")
