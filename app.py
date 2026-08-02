import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import Image as RLImage
from PIL import Image, ImageDraw, ImageFont
import io
import json
import zipfile
from datetime import datetime
import random
import re

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================

# Gemini Model Configuration
# หมายเหตุ: ใช้ gemini-3.5-flash ที่เสถียรที่สุด
# หากต้องการใช้รุ่นอื่น ให้เปลี่ยนชื่อโมเดลตรงนี้
GEMINI_MODEL = 'gemini-3.1-flash-lite'

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
    },
    "Forest": {
        "primary": "#2D5016",
        "secondary": "#6B8E23",
        "accent": "#DAA520",
        "bg": "#F5F5DC",
        "text": "#2F4F2F"
    }
}

# Product Categories (จากเอกสาร Reference)
PRODUCT_CATEGORIES = {
    "Early Literacy": [
        "Alphabet Recognition", "Letter Tracing", "Beginning Sounds", 
        "Ending Sounds", "Rhyming Words", "Phonemic Awareness",
        "CVC Words", "Word Families", "Blends", "Digraphs",
        "Long/Short Vowels", "Silent E", "Decodable Passages",
        "Reading Fluency", "Reading Comprehension", "Sight Words",
        "Vocabulary", "Spelling", "Grammar", "Sentence Building",
        "Writing Prompts", "Handwriting"
    ],
    "Mathematics": [
        "Number Recognition", "Counting", "Number Sense",
        "Addition", "Subtraction", "Multiplication", "Division",
        "Place Value", "Fractions", "Decimals", "Geometry",
        "Measurement", "Time", "Money", "Data & Graphs",
        "Word Problems", "Math Fact Fluency", "Mental Math",
        "Algebra Readiness", "Ratios & Proportions", "Integers",
        "Expressions & Equations", "Financial Literacy"
    ],
    "Science": [
        "Life Cycles", "Plants", "Animals", "Habitats",
        "Human Body", "Weather", "Seasons", "Earth Science",
        "Space", "Matter", "Energy", "Forces & Motion",
        "Ecosystems", "Scientific Method", "STEM Challenges"
    ],
    "Social Studies": [
        "Communities", "Maps & Geography", "Continents & Oceans",
        "Government", "Citizenship", "Economics",
        "Historical Figures", "Cultural Studies", "Timelines"
    ],
    "Classroom Resources": [
        "Morning Work", "Bell Ringers", "Exit Tickets",
        "Task Cards", "Centers", "Homework", "Assessments",
        "Sub Plans", "Early Finisher Activities", "Graphic Organizers"
    ],
    "Special Education": [
        "Functional Reading", "Functional Math", "Budgeting",
        "Shopping", "Money Management", "Time Management",
        "Daily Schedules", "Social Scenarios", "Community Signs",
        "Job Skills", "Emotional Regulation"
    ],
    "Puzzle-Based Learning": [
        "Sudoku", "Number Search", "Word Search", "Logic Puzzles",
        "Mazes", "Code Breakers", "Mystery Activities",
        "Pattern Puzzles", "Escape Room Worksheets", "Math Riddles"
    ],
    "Seasonal Products": [
        "Back to School", "Fall", "Winter", "Spring", "Summer",
        "Halloween", "Thanksgiving", "Christmas", "Valentine's Day",
        "Easter", "Earth Day", "End of Year", "Test Prep Season"
    ]
}

GRADE_LEVELS = [
    "Pre-K", "Kindergarten", "1st Grade", "2nd Grade", 
    "3rd Grade", "4th Grade", "5th Grade", "6th Grade",
    "7th Grade", "8th Grade", "Special Education"
]

DIFFICULTY_LEVELS = [
    "Beginner", "Easy", "Grade-Level Practice", 
    "Challenging", "Advanced/Enrichment"
]

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def calculate_opportunity_score(category, skill, grade):
    """
    คำนวณ Opportunity Score ตามเอกสาร Reference
    น้ำหนัก: Buyer need (20), Search relevance (15), Competition (15),
    Differentiation (15), Evergreen (10), Ease of use (10),
    Bundle potential (5), Visual marketing (5), Production feasibility (5)
    """
    # ข้อมูลตลาด (ประมาณการ)
    market_data = {
        "Sight Words": {"demand": 95, "competition": 90, "differentiation": 40},
        "Morning Work": {"demand": 90, "competition": 85, "differentiation": 50},
        "Reading Comprehension": {"demand": 88, "competition": 75, "differentiation": 60},
        "Math Practice": {"demand": 85, "competition": 80, "differentiation": 55},
        "Phonics": {"demand": 85, "competition": 70, "differentiation": 65},
        "Word Search": {"demand": 60, "competition": 40, "differentiation": 70},
        "Sudoku": {"demand": 60, "competition": 40, "differentiation": 75},
        "Budget Worksheets": {"demand": 70, "competition": 30, "differentiation": 85},
        "Tracing": {"demand": 75, "competition": 60, "differentiation": 60},
    }
    
    data = market_data.get(skill, {"demand": 50, "competition": 50, "differentiation": 50})
    
    # คำนวณคะแนน
    buyer_need = min(data["demand"] * 0.2, 20)
    search_relevance = min(data["demand"] * 0.15, 15)
    competition_score = max((100 - data["competition"]) * 0.15, 0)
    differentiation = min(data["differentiation"] * 0.15, 15)
    evergreen = 10 if "Seasonal" not in category else 5
    ease_of_use = 10
    bundle_potential = 5
    visual_marketing = 5
    production_feasibility = 5
    
    total = (buyer_need + search_relevance + competition_score + 
             differentiation + evergreen + ease_of_use + 
             bundle_potential + visual_marketing + production_feasibility)
    
    return int(total)

def generate_worksheet_content(api_key, category, skill, grade, difficulty, num_pages, theme):
    """สร้างเนื้อหาใบงานด้วย Gemini"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    prompt = f"""Create a complete educational worksheet for {grade} students.
Category: {category}
Skill: {skill}
Difficulty: {difficulty}
Theme: {theme}
Number of pages: {num_pages}

Return ONLY valid JSON with this exact structure:
{{
    "title": "Worksheet Title",
    "objective": "Clear learning objective",
    "description": "Brief description",
    "skills_covered": ["skill1", "skill2", "skill3"],
    "pages": [
        {{
            "page_number": 1,
            "page_title": "Page Title",
            "instructions": "Clear student directions",
            "questions": [
                {{
                    "id": 1,
                    "question": "Question text",
                    "answer": "Correct answer",
                    "type": "fill_blank|multiple_choice|short_answer|matching"
                }}
            ],
            "illustration_prompt": "Description of illustration (e.g., 'cute cartoon animals learning')"
        }}
    ],
    "total_questions": 0,
    "differentiation_notes": "How to differentiate for different learners"
}}

Requirements:
1. Content must be age-appropriate for {grade}
2. Questions must progress in difficulty
3. All answers must be accurate
4. Instructions must be clear
5. Content must be original
6. All content must be in English
7. Make it educationally valuable, not just decorative"""
    
    response = model.generate_content(prompt)
    clean_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_text)

def generate_listing(api_key, worksheet_data, category, skill, grade, num_pages):
    """สร้าง TPT Listing ด้วย Gemini"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    prompt = f"""Create a professional TPT product listing for this worksheet:
Title: {worksheet_data.get('title', '')}
Category: {category}
Skill: {skill}
Grade: {grade}
Pages: {num_pages}
Objective: {worksheet_data.get('objective', '')}
Skills: {', '.join(worksheet_data.get('skills_covered', []))}

Generate 5 title options and select the best one.
Return ONLY valid JSON:
{{
    "title_options": [
        "Title Option 1",
        "Title Option 2",
        "Title Option 3",
        "Title Option 4",
        "Title Option 5"
    ],
    "recommended_title": "Best title",
    "description": "Professional description with: opening, what's included, skills, how to use, differentiation, file info",
    "categories": ["Category 1", "Category 2"],
    "subjects": ["Subject 1", "Subject 2"],
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"],
    "standards": ["CCSS.X.X.X"],
    "price": 3.50,
    "teaching_duration": "1 week",
    "total_pages": {num_pages + 2},
    "grade_levels": ["{grade}"],
    "resource_type": "Worksheets",
    "audience": "Classroom Teachers, Homeschool Parents"
}}

Requirements:
1. Title must match real buyer search intent
2. Title structure: Primary Skill + Resource Type + Grade + Feature
3. Description must be in natural American English
4. Tags must reflect how teachers actually search
5. Price must be market-appropriate
6. Standards must be verified (if applicable)
7. All content must be in English"""
    
    response = model.generate_content(prompt)
    clean_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_text)

def create_cartoon_illustration(prompt, theme_colors, size=(800, 600)):
    """สร้างภาพประกอบแบบง่ายๆ ด้วย shapes"""
    img = Image.new('RGB', size, color=theme_colors['bg'])
    draw = ImageDraw.Draw(img)
    
    # สร้าง background pattern
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
    
    caption = prompt[:50] if len(prompt) > 50 else prompt
    draw.text((size[0]//2, size[1] - 50), caption, fill=theme_colors['text'], 
              font=font, anchor="mm")
    
    return img

def create_thumbnail(worksheet_data, theme_colors, thumbnail_type, size=(1500, 1500)):
    """สร้าง Thumbnail ตามเอกสาร Reference"""
    img = Image.new('RGB', size, color=theme_colors['primary'])
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    
    if thumbnail_type == 1:  # Main Cover
        draw.rectangle([0, 0, size[0], size[1]], fill=theme_colors['primary'])
        title = worksheet_data.get('title', 'Worksheet')
        draw.text((size[0]//2, 300), title, fill='white', font=title_font, anchor="mm")
        grade = worksheet_data.get('grade', 'Grade Level')
        draw.text((size[0]//2, 500), grade, fill='white', font=body_font, anchor="mm")
        skill = worksheet_data.get('skill', 'Skill')
        draw.text((size[0]//2, 700), skill, fill='white', font=body_font, anchor="mm")
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
        
    elif thumbnail_type == 3:  # Skills and Features
        draw.rectangle([0, 0, size[0], size[1]], fill=theme_colors['accent'])
        draw.text((size[0]//2, 200), "Skills Covered:", fill='black', 
                 font=title_font, anchor="mm")
        skills = worksheet_data.get('skills_covered', ['Skill 1', 'Skill 2', 'Skill 3'])
        y_pos = 400
        for skill in skills[:3]:
            draw.text((size[0]//2, y_pos), f"• {skill}", fill='black', 
                     font=body_font, anchor="mm")
            y_pos += 150
            
    elif thumbnail_type == 4:  # Sample and Use Cases
        draw.rectangle([0, 0, size[0], size[1]], fill=theme_colors['bg'])
        draw.text((size[0]//2, 200), "Perfect For:", fill=theme_colors['text'], 
                 font=title_font, anchor="mm")
        features = [
            "✓ Morning Work",
            "✓ Independent Practice",
            "✓ Homework",
            "✓ Intervention"
        ]
        y_pos = 400
        for feature in features:
            draw.text((size[0]//2, y_pos), feature, fill=theme_colors['text'], 
                     font=body_font, anchor="mm")
            y_pos += 150
    
    return img

def generate_pdf(worksheet_data, theme_colors, paper_size="letter", include_answer_key=True):
    """สร้าง PDF สวยงามพร้อมภาพประกอบ"""
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
        c.rect(0, height - *inch, width, *inch, fill=1)
        
        # Title
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont("Helvetica-Bold", 24)
        c.drawString(0.75*inch, height - 1*inch, page.get('page_title', f'Page {i+1}'))
        
        # Instructions
        c.setFillColor(HexColor(theme_colors['text']))
        c.setFont("Helvetica", 12)
        y_pos = height - 2*inch
        c.drawString(0.75*inch, y_pos, page.get('instructions', ''))
        
        # Illustration
        if 'illustration_prompt' in page:
            try:
                illustration = create_cartoon_illustration(
                    page['illustration_prompt'], 
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
            c.drawString(0.75*inch, y_pos, f"Page {page.get('page_number', '')}")
            y_pos -= 0.3*inch
            
            c.setFont("Helvetica", 10)
            for q in page.get('questions', []):
                answer_text = f"{q.get('id')}. {q.get('answer', '')}"
                
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
    
    # Sample pages
    for i, page in enumerate(worksheet_data.get('pages', [])[:2]):
        c.setFillColor(HexColor(theme_colors['bg']))
        c.rect(0, 0, width, height, fill=1)
        
        c.setFillColor(HexColor(theme_colors['primary']))
        c.rect(0, height - 1.5*inch, width, 1.5*inch, fill=1)
        
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont("Helvetica-Bold", 20)
        c.drawString(0.75*inch, height - 1*inch, page.get('page_title', f'Sample Page {i+1}'))
        
        c.setFillColor(HexColor('#CCCCCC'))
        c.setFont("Helvetica-Bold", 72)
        c.drawCentredString(width/2, height/2, "PREVIEW")
        
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
{listing_data.get('recommended_title', '')}

ALTERNATIVE TITLES:
{chr(10).join(listing_data.get('title_options', []))}

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

GRADE LEVELS: {', '.join(listing_data.get('grade_levels', []))}

RESOURCE TYPE: {listing_data.get('resource_type', 'Worksheets')}

AUDIENCE: {listing_data.get('audience', 'Classroom Teachers')}
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

def validate_worksheet(worksheet_data):
    """ตรวจสอบคุณภาพใบงานตามเอกสาร Reference"""
    issues = []
    warnings = []
    
    # Educational QA
    if not worksheet_data.get('objective'):
        issues.append("Missing learning objective")
    
    if not worksheet_data.get('skills_covered'):
        issues.append("Missing skills covered")
    
    # Check each page
    for i, page in enumerate(worksheet_data.get('pages', [])):
        if not page.get('instructions'):
            warnings.append(f"Page {i+1}: Missing instructions")
        
        if not page.get('questions'):
            issues.append(f"Page {i+1}: No questions")
        
        for q in page.get('questions', []):
            if not q.get('answer'):
                warnings.append(f"Page {i+1}, Question {q.get('id')}: Missing answer")
    
    # Answer Key Validation
    total_questions = sum(len(p.get('questions', [])) for p in worksheet_data.get('pages', []))
    if worksheet_data.get('total_questions', 0) != total_questions:
        warnings.append(f"Total questions mismatch: stated {worksheet_data.get('total_questions')}, actual {total_questions}")
    
    return {
        "issues": issues,
        "warnings": warnings,
        "is_valid": len(issues) == 0
    }

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
st.markdown("✅ AI สร้างเนื้อหา | ✅ ภาพประกอบอัตโนมัติ | ✅ PDF สวยงาม | ✅ Thumbnail 4 แบบ | ✅ SEO Listing | ✅ Export ZIP")

# Sidebar
with st.sidebar:
    st.header("⚙️ ตั้งค่า")
    api_key = st.text_input(
        "Gemini API Key", 
        type="password",
        help="ใส่ API Key จาก https://aistudio.google.com/app/apikey"
    )
    
    st.divider()
    
    # Product Category
    category = st.selectbox("หมวดหมู่", list(PRODUCT_CATEGORIES.keys()))
    
    # Skill (based on category)
    skills = PRODUCT_CATEGORIES[category]
    skill = st.selectbox("ทักษะ", skills)
    
    # Grade Level
    grade_level = st.selectbox("ระดับชั้น", GRADE_LEVELS)
    
    # Difficulty
    difficulty = st.selectbox("ระดับความยาก", DIFFICULTY_LEVELS)
    
    # Number of pages
    num_pages = st.number_input("จำนวนหน้า", min_value=1, max_value=50, value=5)
    
    # Theme
    theme = st.selectbox("ธีมการออกแบบ", list(THEMES.keys()))
    
    # Paper size
    paper_size = st.radio("ขนาดกระดาษ", ["US Letter", "A4"])
    
    # Answer key
    include_answer_key = st.checkbox("รวม Answer Key", value=True)
    
    st.divider()
    
    # Opportunity Score
    if st.button("🎯 คำนวณคะแนนโอกาส"):
        score = calculate_opportunity_score(category, skill, grade_level)
        st.metric("Opportunity Score", f"{score}/100")
        
        if score >= 80:
            st.success("โอกาสดีเยี่ยม! แนะนำให้ทำ")
        elif score >= 65:
            st.info("น่าสนใจ ต้องมีจุดเด่นที่แตกต่าง")
        elif score >= 50:
            st.warning("การแข่งขันสูง พิจารณาหาจุดเด่นเพิ่มเติม")
        else:
            st.error("ไม่แนะนำในรูปแบบปัจจุบัน")

# Main Content
if "worksheet_data" not in st.session_state:
    st.session_state.worksheet_data = None

if "listing_data" not in st.session_state:
    st.session_state.listing_data = None

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 สร้างเนื้อหา",
    "📊 TPT Listing",
    "🎨 ตัวอย่างและ Preview",
    "🖼️ Thumbnails",
    "✅ Validation",
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
                        api_key, category, skill, grade_level, 
                        difficulty, num_pages, theme
                    )
                    data['grade'] = grade_level
                    data['skill'] = skill
                    data['category'] = category
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
            st.write(f"**Category:** {st.session_state.worksheet_data.get('category', '')}")
            st.write(f"**Skill:** {st.session_state.worksheet_data.get('skill', '')}")
        
        with col2:
            st.write(f"**Objective:** {st.session_state.worksheet_data.get('objective', '')}")
            st.write(f"**Total Questions:** {st.session_state.worksheet_data.get('total_questions', 0)}")
            st.write(f"**Pages:** {len(st.session_state.worksheet_data.get('pages', []))}")
        
        st.write(f"**Skills Covered:** {', '.join(st.session_state.worksheet_data.get('skills_covered', []))}")
        
        if st.session_state.worksheet_data.get('differentiation_notes'):
            st.write(f"**Differentiation:** {st.session_state.worksheet_data.get('differentiation_notes')}")
        
        with st.expander("ดูเนื้อหาทั้งหมด (JSON)"):
            st.json(st.session_state.worksheet_data)

with tab2:
    st.header("2. TPT Listing Generator")
    
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
                            category,
                            skill,
                            grade_level,
                            num_pages
                        )
                        st.session_state.listing_data = listing
                        st.success("✅ สร้าง Listing สำเร็จ!")
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {e}")
        
        if st.session_state.listing_data:
            st.subheader("📌 Title Options")
            for i, title in enumerate(st.session_state.listing_data.get('title_options', []), 1):
                st.write(f"{i}. {title}")
            
            st.subheader("✅ Recommended Title")
            st.text_area("Recommended", st.session_state.listing_data.get('recommended_title', ''), height=100)
            
            st.subheader("📝 Description")
            st.text_area("Description", st.session_state.listing_data.get('description', ''), height=400)
            
            st.subheader("🏷️ Metadata")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Categories:**", ", ".join(st.session_state.listing_data.get('categories', [])))
                st.write("**Subjects:**", ", ".join(st.session_state.listing_data.get('subjects', [])))
                st.write("**Resource Type:**", st.session_state.listing_data.get('resource_type', ''))
                st.write("**Audience:**", st.session_state.listing_data.get('audience', ''))
            
            with col2:
                st.write("**Tags:**", ", ".join(st.session_state.listing_data.get('tags', [])))
                st.write("**Standards:**", ", ".join(st.session_state.listing_data.get('standards', [])))
                st.write("**Grade Levels:**", ", ".join(st.session_state.listing_data.get('grade_levels', [])))
            
            st.subheader("💰 Pricing & Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Suggested Price", f"${st.session_state.listing_data.get('price', 3.50)}")
            with col2:
                st.metric("Teaching Duration", st.session_state.listing_data.get('teaching_duration', 'N/A'))
            with col3:
                st.metric("Total Pages", st.session_state.listing_data.get('total_pages', 0))
    else:
        st.warning("กรุณาสร้างเนื้อหาในแท็บแรกก่อน")

with tab3:
    st.header("3. ตัวอย่างและ Preview")
    
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
                        f"TPT_{skill.replace(' ', '_')}_{grade_level.replace(' ', '_')}.pdf",
                        "application/pdf"
                    )
                    st.success("✅ สร้าง PDF สำเร็จ!")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
        
        st.subheader("📄 Product Preview")
        if st.button("📄 สร้าง Preview PDF", type="primary"):
            with st.spinner("กำลังสร้าง Preview..."):
                try:
                    preview_buffer = create_preview_pdf(
                        st.session_state.worksheet_data,
                        theme_colors
                    )
                    
                    st.download_button(
                        "📥 ดาวน์โหลด Preview PDF",
                        preview_buffer,
                        "Product_Preview.pdf",
                        "application/pdf"
                    )
                    st.success("✅ สร้าง Preview สำเร็จ!")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
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
    st.header("5. Validation Center")
    
    if st.session_state.worksheet_data:
        st.info("ตรวจสอบคุณภาพใบงานตามมาตรฐาน TPT")
        
        if st.button("✅ ตรวจสอบคุณภาพ", type="primary"):
            validation = validate_worksheet(st.session_state.worksheet_data)
            
            if validation['is_valid']:
                st.success("✅ ใบงานผ่านเกณฑ์คุณภาพ!")
            else:
                st.error("❌ พบปัญหาที่ต้องแก้ไข:")
                for issue in validation['issues']:
                    st.error(f"  • {issue}")
            
            if validation['warnings']:
                st.warning("⚠️ คำเตือน:")
                for warning in validation['warnings']:
                    st.warning(f"  • {warning}")
            
            if validation['is_valid'] and not validation['warnings']:
                st.balloons()
    else:
        st.warning("กรุณาสร้างเนื้อหาในแท็บแรกก่อน")

with tab6:
    st.header("6. Export Complete Package")
    
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
                        f"TPT_{skill.replace(' ', '_')}_{grade_level.replace(' ', '_')}_Package.zip",
                        "application/zip"
                    )
                    
                    st.success("✅ สร้าง Package สำเร็จ! พร้อมอัปโหลดขึ้น TPT")
                    st.balloons()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
    else:
        st.warning("กรุณาสร้างเนื้อหาและ Listing ก่อน")

# Footer
st.divider()
st.caption("TPT Worksheet Generator Pro | Built with Streamlit & Gemini AI | AI-Generated Content")
st.caption("หมายเหตุ: ใช้ Gemini 3.5 Flash สำหรับสร้างเนื้อหา | ภาพประกอบสร้างด้วย shapes | รันบน Streamlit Cloud ได้ 100%")
