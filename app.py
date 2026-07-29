import streamlit as st
import google.generativeai as genai
import json
import pdfkit
import re

# ==========================================
# 1. การตั้งค่าหน้าเว็บ (Page Config)
# ==========================================
st.set_page_config(page_title="TPT Worksheet Pro Builder", layout="wide", page_icon="📚")
st.title("🚀 TPT Worksheet Pro Builder & Marketplace Assistant")
st.markdown("ระบบผู้ช่วยสร้างใบงานและข้อมูลลงขาย Teachers Pay Teachers อัตโนมัติ")

# ==========================================
# 2. ฟังก์ชันช่วยเหลือ (Helper Functions)
# ==========================================
def clean_json_string(raw_string):
    """ลบ Markdown ออกจาก JSON ที่ได้จาก AI"""
    match = re.search(r'
