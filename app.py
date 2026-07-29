# app.py - โครงสร้างหลัก
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont
import json
import os
from datetime import datetime
import io

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="TPT Worksheet Generator",
    page_icon="📚",
    layout="wide"
)

# Sidebar - การตั้งค่า
with st.sidebar:
    st.title("⚙️ Settings")
    
    gemini_api_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    
    # เลือกประเภทใบงาน
    worksheet_type = st.selectbox(
        "Worksheet Type",
        ["Math Practice", "Reading Comprehension", "Phonics", 
         "Sight Words", "Word Search", "Sudoku", "Tracing",
         "Multiple Choice", "Fill in the Blank", "Matching"]
    )
    
    grade_level = st.selectbox(
        "Grade Level",
        ["Pre-K", "Kindergarten", "1st Grade", "2nd Grade", 
         "3rd Grade", "4th Grade", "5th Grade", "Special Education"]
    )
    
    difficulty = st.select_slider(
    "Difficulty",
    options=["Beginner", "Easy", "Grade Level", "Challenging", "Advanced"],
    value="Grade Level"  # <--- แก้เป็นข้อความตามนี้ครับ
)
    
    num_pages = st.number_input("Number of Pages", min_value=1, max_value=50, value=10)
    
    theme = st.selectbox(
        "Theme",
        ["Clean Classroom", "Minimal B&W", "Soft Pastel", "Bright Elementary",
         "Space", "Ocean", "Farm", "Dinosaur", "Seasonal"]
    )
    
    paper_size = st.radio("Paper Size", ["US Letter", "A4"])
    
    include_answer_key = st.checkbox("Include Answer Key", value=True)
    
    st.divider()
    
    if st.button("🎯 Generate Opportunity Score", type="primary"):
        # คำนวณโอกาสทางการตลาด
        score = calculate_opportunity_score(worksheet_type, grade_level)
        st.metric("Opportunity Score", f"{score}/100")
        
        if score >= 80:
            st.success("Strong opportunity! Good to proceed.")
        elif score >= 65:
            st.info("Promising with clear differentiation needed.")
        else:
            st.warning("Competitive niche. Consider unique angle.")

# Main content
st.title("📚 TPT Worksheet Generator")
st.markdown("Create professional educational worksheets for Teachers Pay Teachers")

if "worksheet_data" not in st.session_state:
    st.session_state.worksheet_data = None

# Tab layout
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Content", " Design", "📊 Listing", "🖼️ Preview", " Export"
])

with tab1:
    st.header("Worksheet Content")
    
    if st.button("Generate Worksheet Content", type="primary"):
        if not gemini_api_key:
            st.error("Please enter Gemini API Key in sidebar")
        else:
            with st.spinner("Generating worksheet content..."):
                # Configure Gemini
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # สร้าง prompt
                prompt = create_worksheet_prompt(
                    worksheet_type, grade_level, difficulty, 
                    num_pages, theme
                )
                
                # Generate content
                response = model.generate_content(prompt)
                
                # Parse response
                try:
                    worksheet_data = json.loads(response.text)
                    st.session_state.worksheet_data = worksheet_data
                    
                    # แสดง preview
                    st.success("Content generated successfully!")
                    st.json(worksheet_data)
                    
                    # คำนวณ cost
                    tokens_used = estimate_tokens(prompt, response.text)
                    cost = calculate_cost(tokens_used)
                    st.info(f"Estimated API Cost: ${cost:.4f} (~{cost*35:.2f} THB)")
                    
                except json.JSONDecodeError:
                    st.error("Failed to parse AI response. Please try again.")

with tab2:
    st.header("Design & Layout")
    
    if st.session_state.worksheet_data:
        # แสดงตัวเลือก design
        col1, col2 = st.columns(2)
        
        with col1:
            font_family = st.selectbox(
                "Font Family",
                ["Arial", "Times New Roman", "Comic Sans MS", "Century Gothic"]
            )
            
            color_scheme = st.color_picker("Primary Color", "#4A90E2")
            
        with col2:
            margin_size = st.slider("Margin (inches)", 0.5, 2.0, 0.75)
            show_grid = st.checkbox("Show Grid Lines", value=False)
        
        if st.button("Generate PDF"):
            pdf_buffer = generate_pdf(
                st.session_state.worksheet_data,
                paper_size="letter" if paper_size == "US Letter" else "a4",
                font_family=font_family,
                primary_color=color_scheme,
                margin=margin_size
            )
            
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name=f"worksheet_{worksheet_type.lower().replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

with tab3:
    st.header("TPT Listing Generator")
    
    if st.session_state.worksheet_data:
        if st.button("Generate SEO Listing"):
            with st.spinner("Creating listing..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                listing_prompt = create_listing_prompt(
                    st.session_state.worksheet_data,
                    worksheet_type, grade_level
                )
                
                response = model.generate_content(listing_prompt)
                
                listing_data = json.loads(response.text)
                
                # แสดง results
                st.subheader("📝 Product Title")
                st.text_input("Recommended Title", listing_data.get('title', ''))
                
                st.subheader(" Description")
                st.text_area("Description", listing_data.get('description', ''), height=300)
                
                st.subheader("🏷️ Tags")
                st.write("Categories:", ", ".join(listing_data.get('categories', [])))
                st.write("Subject Areas:", ", ".join(listing_data.get('subjects', [])))
                st.write("Tags:", ", ".join(listing_data.get('tags', [])))
                
                st.subheader(" Standards")
                for std in listing_data.get('standards', []):
                    st.write(f"- {std}")
                
                st.subheader("💵 Pricing")
                st.metric("Suggested Price", f"${listing_data.get('price', 3.50)}")
                
                # ปุ่ม copy
                if st.button("Copy All to Clipboard"):
                    st.code(format_listing_for_copy(listing_data))

with tab4:
    st.header("Product Preview & Thumbnails")
    
    if st.session_state.worksheet_data:
        st.subheader("Thumbnail Generator")
        
        thumbnail_style = st.selectbox(
            "Thumbnail Style",
            ["Modern Clean", "Colorful Elementary", "Professional", "Sample Collage"]
        )
        
        if st.button("Generate Thumbnails"):
            # สร้าง 4 thumbnails
            thumbnails = generate_thumbnails(
                st.session_state.worksheet_data,
                worksheet_type, grade_level,
                style=thumbnail_style
            )
            
            cols = st.columns(2)
            for i, thumb in enumerate(thumbnails):
                with cols[i % 2]:
                    st.image(thumb, caption=f"Thumbnail {i+1}")
                    
                    # Convert to bytes
                    img_buffer = io.BytesIO()
                    thumb.save(img_buffer, format='JPEG', quality=95)
                    
                    st.download_button(
                        label=f"Download Thumbnail {i+1}",
                        data=img_buffer.getvalue(),
                        file_name=f"thumbnail_{i+1}.jpg",
                        mime="image/jpeg"
                    )
        
        st.subheader("Product Preview PDF")
        if st.button("Generate Preview"):
            preview_pdf = generate_preview_pdf(
                st.session_state.worksheet_data,
                include_watermark=True
            )
            
            st.download_button(
                label="Download Preview PDF",
                data=preview_pdf,
                file_name="product_preview.pdf",
                mime="application/pdf"
            )

with tab5:
    st.header("Export Complete Package")
    
    if st.session_state.worksheet_data:
        st.write("This will generate:")
        st.write("- ✅ Student Worksheets PDF")
        st.write("- ✅ Answer Key PDF")
        st.write("- ✅ Product Preview PDF")
        st.write("- ✅ 4 Thumbnails (JPG)")
        st.write("- ✅ Listing Information (TXT)")
        st.write("- ✅ Complete ZIP Package")
        
        if st.button("Export Everything", type="primary"):
            with st.spinner("Creating package..."):
                package = create_complete_package(
                    st.session_state.worksheet_data,
                    worksheet_type, grade_level
                )
                
                st.download_button(
                    label="Download Complete Package (ZIP)",
                    data=package,
                    file_name=f"TPT_{worksheet_type}_{grade_level}_Package.zip",
                    mime="application/zip"
                )
                
                st.success("Package ready for TPT upload!")

# Helper functions
def calculate_opportunity_score(worksheet_type, grade_level):
    """คำนวณโอกาสทางการตลาด"""
    # ข้อมูลตัวอย่าง - ควร update จาก research จริง
    niche_data = {
        "Sight Words": {"competition": 90, "demand": 95},
        "Morning Work": {"competition": 85, "demand": 90},
        "Math Practice": {"competition": 80, "demand": 85},
        "Reading Comprehension": {"competition": 75, "demand": 88},
        "Phonics": {"competition": 70, "demand": 85},
        "Sudoku": {"competition": 40, "demand": 60},
        "Budget Worksheets": {"competition": 30, "demand": 70},
    }
    
    data = niche_data.get(worksheet_type, {"competition": 50, "demand": 50})
    
    # สูตรคำนวณ (ปรับได้ตามต้องการ)
    score = (data["demand"] * 0.6) + ((100 - data["competition"]) * 0.4)
    
    return int(score)

def create_worksheet_prompt(w_type, grade, difficulty, pages, theme):
    """สร้าง prompt สำหรับ generate worksheet"""
    return f"""
Create a complete educational worksheet with the following specifications:

Type: {w_type}
Grade: {grade}
Difficulty: {difficulty}
Number of Pages: {pages}
Theme: {theme}

Return in JSON format with this structure:
{{
    "title": "Worksheet title",
    "learning_objective": "Clear learning objective",
    "grade_level": "{grade}",
    "pages": [
        {{
            "page_number": 1,
            "page_type": "student_work",
            "instructions": "Student directions",
            "questions": [
                {{"id": 1, "question": "...", "answer": "...", "type": "..."}}
            ]
        }}
    ],
    "answer_key": {{
        "page_number": "answer key page number",
        "answers": [...]
    }},
    "skills_covered": ["skill1", "skill2"],
    "total_questions": 0
}}

Make sure:
1. Content is age-appropriate for {grade}
2. Questions progress in difficulty
3. All answers are accurate
4. Instructions are clear
5. Content is original
"""

def create_listing_prompt(worksheet_data, w_type, grade):
    """สร้าง prompt สำหรับ generate listing"""
    return f"""
Based on this worksheet data: {json.dumps(worksheet_data)}

Create a complete TPT listing with:

1. SEO-optimized title (include grade, skill, resource type)
2. Engaging description with:
   - Opening that solves teacher's problem
   - What's included
   - Skills covered
   - How to use
   - Differentiation
3. Categories and tags
4. Education standards (if applicable)
5. Suggested price based on page count and quality
6. Teaching duration

Return in JSON format:
{{
    "title": "...",
    "description": "...",
    "categories": ["..."],
    "subjects": ["..."],
    "tags": ["..."],
    "standards": ["..."],
    "price": 3.50,
    "teaching_duration": "1 week",
    "total_pages": 0,
    "grade_levels": ["..."]
}}

Use natural American English. Focus on buyer search intent.
"""

def estimate_tokens(input_text, output_text):
    """ประมาณการ tokens ที่ใช้"""
    # ประมาณ 4 characters = 1 token
    input_tokens = len(input_text) // 4
    output_tokens = len(output_text) // 4
    return input_tokens + output_tokens

def calculate_cost(total_tokens):
    """คำนวณ cost (Gemini 1.5 Flash)"""
    # Input: $0.35 per 1M tokens
    # Output: $1.05 per 1M tokens
    # ประมาณครึ่งหนึ่งเป็น input ครึ่งหนึ่งเป็น output
    input_cost = (total_tokens / 2) / 1_000_000 * 0.35
    output_cost = (total_tokens / 2) / 1_000_000 * 1.05
    return input_cost + output_cost

def generate_pdf(worksheet_data, paper_size, font_family, primary_color, margin):
    """Generate PDF worksheet"""
    buffer = io.BytesIO()
    
    if paper_size == "letter":
        size = letter
    else:
        size = A4
    
    c = canvas.Canvas(buffer, pagesize=size)
    width, height = size
    
    # ตั้งค่า font
    c.setFont(font_family, 12)
    
    # สร้างเนื้อหา
    for page in worksheet_data.get('pages', []):
        y_position = height - margin * 72  # เริ่มจากบน
        
        # Title
        c.setFont(font_family, 16)
        c.setFillColor(primary_color)
        c.drawString(margin * 72, y_position, page.get('instructions', ''))
        
        y_position -= 30
        
        # Questions
        c.setFont(font_family, 12)
        c.setFillColor('black')
        
        for q in page.get('questions', []):
            question_text = f"{q.get('id')}. {q.get('question', '')}"
            c.drawString(margin * 72, y_position, question_text)
            y_position -= 25
            
            # Answer space
            c.line(margin * 72, y_position, (margin + 6) * 72, y_position)
            y_position -= 30
            
            # New page if needed
            if y_position < margin * 72:
                c.showPage()
                y_position = height - margin * 72
                c.setFont(font_family, 12)
        
        c.showPage()
    
    c.save()
    buffer.seek(0)
    return buffer

def generate_thumbnails(worksheet_data, w_type, grade, style="Modern Clean"):
    """Generate 4 thumbnails"""
    thumbnails = []
    
    # Thumbnail 1: Main Cover
    img1 = Image.new('RGB', (1500, 1500), color='#4A90E2')
    draw1 = ImageDraw.Draw(img1)
    
    # เพิ่ม text (ใน production ควรใช้ font จริง)
    draw1.text((750, 400), worksheet_data.get('title', 'Worksheet'), 
               fill='white', anchor="mm")
    draw1.text((750, 600), grade, fill='white', anchor="mm")
    draw1.text((750, 800), w_type, fill='white', anchor="mm")
    
    thumbnails.append(img1)
    
    # Thumbnail 2: What's Included
    img2 = Image.new('RGB', (1500, 1500), color='#50C878')
    draw2 = ImageDraw.Draw(img2)
    draw2.text((750, 500), "What's Included:", fill='white', anchor="mm")
    draw2.text((750, 700), f"{len(worksheet_data.get('pages', []))} Student Pages", 
               fill='white', anchor="mm")
    draw2.text((750, 900), "Answer Key Included", fill='white', anchor="mm")
    
    thumbnails.append(img2)
    
    # Thumbnail 3: Skills
    img3 = Image.new('RGB', (1500, 1500), color='#FF6B6B')
    draw3 = ImageDraw.Draw(img3)
    draw3.text((750, 500), "Skills Covered:", fill='white', anchor="mm")
    for i, skill in enumerate(worksheet_data.get('skills_covered', [])[:3]):
        draw3.text((750, 650 + i*100), f"• {skill}", fill='white', anchor="mm")
    
    thumbnails.append(img3)
    
    # Thumbnail 4: Features
    img4 = Image.new('RGB', (1500, 1500), color='#FFD93D')
    draw4 = ImageDraw.Draw(img4)
    draw4.text((750, 500), "Features:", fill='black', anchor="mm")
    draw4.text((750, 700), "✓ No Prep", fill='black', anchor="mm")
    draw4.text((750, 850), "✓ Print & Go", fill='black', anchor="mm")
    draw4.text((750, 1000), "✓ Answer Key", fill='black', anchor="mm")
    
    thumbnails.append(img4)
    
    return thumbnails

def generate_preview_pdf(worksheet_data, include_watermark=True):
    """Generate product preview PDF"""
    # Implementation similar to generate_pdf
    # แต่เพิ่ม watermark และเลือกเฉพาะบางหน้า
    pass

def create_complete_package(worksheet_data, w_type, grade):
    """Create complete ZIP package"""
    import zipfile
    
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Student worksheets
        pdf_buffer = generate_pdf(worksheet_data, "letter", "Arial", "#000000", 0.75)
        zip_file.writestr("Student_Worksheets.pdf", pdf_buffer.getvalue())
        
        # Answer key
        if 'answer_key' in worksheet_data:
            ak_buffer = generate_answer_key_pdf(worksheet_data)
            zip_file.writestr("Answer_Key.pdf", ak_buffer.getvalue())
        
        # Thumbnails
        thumbnails = generate_thumbnails(worksheet_data, w_type, grade)
        for i, thumb in enumerate(thumbnails):
            img_buffer = io.BytesIO()
            thumb.save(img_buffer, format='JPEG')
            zip_file.writestr(f"Thumbnail_{i+1}.jpg", img_buffer.getvalue())
        
        # Listing info
        listing_text = format_listing_for_copy(worksheet_data)
        zip_file.writestr("Listing_Information.txt", listing_text)
        
        # Preview
        preview_buffer = generate_preview_pdf(worksheet_data)
        zip_file.writestr("Product_Preview.pdf", preview_buffer.getvalue())
    
    buffer.seek(0)
    return buffer

def format_listing_for_copy(listing_data):
    """Format listing for easy copy-paste"""
    text = f"""
TITLE:
{listing_data.get('title', '')}

DESCRIPTION:
{listing_data.get('description', '')}

CATEGORIES:
{', '.join(listing_data.get('categories', []))}

SUBJECTS:
{', '.join(listing_data.get('subjects', []))}

TAGS:
{', '.join(listing_data.get('tags', []))}

STANDARDS:
{chr(10).join(listing_data.get('standards', []))}

PRICE: ${listing_data.get('price', 3.50)}

TEACHING DURATION: {listing_data.get('teaching_duration', 'N/A')}

TOTAL PAGES: {listing_data.get('total_pages', 0)}
"""
    return text

# Run app
if __name__ == "__main__":
    st.write("---")
    st.caption("TPT Worksheet Generator v1.0 | Built with Streamlit & Gemini AI")
