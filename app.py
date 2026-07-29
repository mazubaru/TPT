import React, { useState } from 'react';
import { 
  Settings, FileText, ShoppingCart, Download, 
  Wand2, Printer, CheckCircle, AlertCircle, Image as ImageIcon, Copy
} from 'lucide-react';

export default function App() {
  const [apiKey, setApiKey] = useState('');
  const [topic, setTopic] = useState('Spring Season Math');
  const [grade, setGrade] = useState('1st Grade');
  const [subject, setSubject] = useState('Math');
  const [numPages, setNumPages] = useState(2);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('content');
  const [productData, setProductData] = useState(null);

  const generateTPTProduct = async () => {
    if (!apiKey) {
      setError('กรุณาใส่ Gemini API Key ก่อนครับ');
      return;
    }
    
    setIsGenerating(true);
    setError('');

    try {
      const prompt = `
        You are an expert TPT (Teachers Pay Teachers) product creator.
        Create a complete English-language product for:
        Topic: ${topic}
        Grade: ${grade}
        Subject: ${subject}
        Number of worksheet pages: ${numPages} (each page should have 3-5 questions)

        Return ONLY a JSON object matching this exact structure:
        {
          "listing_info": {
            "seo_title": "Catchy SEO Title for TPT",
            "description": "Engaging product description (min 3 paragraphs)",
            "suggested_price": 3.00,
            "teaching_duration": "e.g., 1 Hour",
            "tags": ["tag1", "tag2", "tag3"],
            "categories": ["category1", "category2"]
          },
          "pages": [
            {
              "page_title": "Title of the page",
              "instructions": "Instructions for student",
              "questions": [
                { "q": "Question text", "a": "Answer text", "clipart": "keyword for clipart (e.g., cute apple)" }
              ]
            }
          ]
        }
      `;

      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { responseMimeType: "application/json" }
        })
      });

      if (!response.ok) {
        throw new Error('API Request failed. Please check your API Key.');
      }

      const data = await response.json();
      const jsonText = data.candidates[0].content.parts[0].text;
      
      const parsedData = JSON.parse(jsonText);
      setProductData(parsedData);
      setActiveTab('content'); // Switch to content tab on success
      
    } catch (err) {
      setError(err.message || 'เกิดข้อผิดพลาดในการประมวลผล');
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePrint = () => {
    const printContent = document.getElementById('printable-worksheet').innerHTML;
    const printWindow = window.open('', '', 'width=800,height=900');
    printWindow.document.write(`
      <html>
        <head>
          <title>Print Worksheet</title>
          <style>
            @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap');
            body { 
              font-family: 'Comic Neue', cursive, sans-serif; 
              margin: 0; padding: 0; 
              color: #333;
            }
            .page { 
              page-break-after: always; 
              padding: 40px; 
              width: 8.5in; 
              height: 11in; 
              box-sizing: border-box;
              margin: 0 auto;
            }
            .header { 
              text-align: center; 
              border-bottom: 2px solid #333; 
              padding-bottom: 10px; 
              margin-bottom: 30px; 
            }
            .title { font-size: 28px; font-weight: bold; margin-bottom: 5px; }
            .instructions { font-size: 16px; font-style: italic; }
            .name-date { 
              display: flex; justify-content: space-between; 
              font-size: 18px; margin-bottom: 20px; font-weight: bold;
            }
            .question-box { 
              margin-bottom: 25px; padding: 15px; 
              border: 2px dashed #bbb; border-radius: 10px; 
              min-height: 80px;
            }
            .clipart-box {
              float: right; width: 60px; height: 60px;
              border: 1px solid #eee; background: #fafafa;
              display: flex; align-items: center; justify-content: center;
              font-size: 10px; color: #aaa; text-align: center; border-radius: 8px;
            }
            .q-text { font-size: 20px; margin-bottom: 10px; }
            .answer-line { 
              margin-top: 30px; border-bottom: 1px solid #333; 
              width: 80%; height: 20px; 
            }
          </style>
        </head>
        <body>${printContent}</body>
      </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 500);
  };

  const handleUpdateQuestion = (pageIndex, qIndex, field, value) => {
    const newData = { ...productData };
    newData.pages[pageIndex].questions[qIndex][field] = value;
    setProductData(newData);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('คัดลอกข้อความแล้ว (Copied!)');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col md:flex-row font-sans text-gray-800">
      
      {/* SIDEBAR */}
      <div className="w-full md:w-80 bg-white border-r border-gray-200 shadow-sm flex flex-col">
        <div className="p-6 border-b border-gray-200 bg-indigo-600 text-white">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Wand2 className="w-6 h-6" /> TPT Builder Pro
          </h1>
          <p className="text-xs text-indigo-200 mt-1">AI Worksheet & Listing Generator</p>
        </div>

        <div className="p-6 flex-1 overflow-y-auto space-y-6">
          {/* API Setup */}
          <div className="space-y-3">
            <label className="text-sm font-semibold flex items-center gap-2 text-gray-700">
              <Settings className="w-4 h-4 text-gray-500"/> Gemini API Key
            </label>
            <input 
              type="password" 
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              placeholder="AIzaSy..."
            />
          </div>

          <div className="w-full h-px bg-gray-200"></div>

          {/* Product Settings */}
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-700">⚙️ Product Details</h3>
            
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Grade Level</label>
              <select value={grade} onChange={(e) => setGrade(e.target.value)} className="w-full p-2 border border-gray-300 rounded-md">
                <option>Pre-K</option>
                <option>Kindergarten</option>
                <option>1st Grade</option>
                <option>2nd Grade</option>
                <option>3rd Grade</option>
                <option>Special Ed</option>
              </select>
            </div>

            <div>
              <label className="text-xs text-gray-500 mb-1 block">Subject</label>
              <select value={subject} onChange={(e) => setSubject(e.target.value)} className="w-full p-2 border border-gray-300 rounded-md">
                <option>Math</option>
                <option>ELA / Reading</option>
                <option>Science</option>
                <option>Life Skills</option>
              </select>
            </div>

            <div>
              <label className="text-xs text-gray-500 mb-1 block">Specific Topic (Niche)</label>
              <input 
                type="text" 
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="e.g. Spring Addition, Phonics..."
              />
            </div>

            <div>
              <label className="text-xs text-gray-500 mb-1 block">Pages to Generate: {numPages}</label>
              <input 
                type="range" min="1" max="5" 
                value={numPages}
                onChange={(e) => setNumPages(e.target.value)}
                className="w-full"
              />
            </div>
          </div>

          <button 
            onClick={generateTPTProduct}
            disabled={isGenerating}
            className={`w-full py-3 rounded-lg font-bold text-white shadow-md transition-all flex justify-center items-center gap-2
              ${isGenerating ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 hover:-translate-y-0.5'}`}
          >
            {isGenerating ? 'Generating...' : '🪄 Generate Full Product'}
          </button>
          
          {error && (
            <div className="p-3 bg-red-50 text-red-600 text-sm rounded-md flex gap-2 items-start">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>
      </div>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        
        {/* TABS */}
        <div className="bg-white border-b border-gray-200 px-6 pt-4 flex gap-6 shrink-0">
          <button 
            onClick={() => setActiveTab('content')}
            className={`pb-3 font-medium flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'content' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            <FileText className="w-4 h-4"/> 1. Worksheet Editor
          </button>
          <button 
            onClick={() => setActiveTab('listing')}
            className={`pb-3 font-medium flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'listing' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            <ShoppingCart className="w-4 h-4"/> 2. TPT Listing Info
          </button>
          <button 
            onClick={() => setActiveTab('export')}
            className={`pb-3 font-medium flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'export' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            <Download className="w-4 h-4"/> 3. Export PDF
          </button>
        </div>

        {/* TAB CONTENT */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
          
          {!productData && !isGenerating && (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 space-y-4">
              <Wand2 className="w-16 h-16 opacity-20" />
              <p className="text-lg">ใส่ API Key แล้วกด Generate ด้านซ้ายเพื่อสร้างใบงาน</p>
            </div>
          )}

          {isGenerating && (
            <div className="h-full flex flex-col items-center justify-center text-indigo-500 space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              <p className="text-lg font-medium animate-pulse">AI กำลังวิเคราะห์และออกแบบเนื้อหา...</p>
            </div>
          )}

          {productData && !isGenerating && (
            <div className="max-w-4xl mx-auto pb-20">
              
              {/* TAB 1: CONTENT EDITOR */}
              {activeTab === 'content' && (
                <div className="space-y-8">
                  <div className="bg-blue-50 border border-blue-200 text-blue-800 p-4 rounded-lg flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 mt-0.5 shrink-0" />
                    <div>
                      <h4 className="font-bold">สร้างเนื้อหาสำเร็จ!</h4>
                      <p className="text-sm opacity-90">คุณสามารถตรวจสอบและแก้ไขข้อความต่างๆ ด้านล่างนี้ได้โดยตรง ก่อนทำการปริ้นต์หรือเซฟเป็น PDF</p>
                    </div>
                  </div>

                  {productData.pages.map((page, pIdx) => (
                    <div key={pIdx} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                      <h3 className="text-lg font-bold mb-4 border-b pb-2 flex items-center gap-2">
                        <FileText className="w-5 h-5 text-gray-400"/> หน้าที่ {pIdx + 1}: {page.page_title}
                      </h3>
                      
                      <div className="space-y-6">
                        {page.questions.map((q, qIdx) => (
                          <div key={qIdx} className="p-4 bg-gray-50 rounded-lg border border-gray-100 flex gap-4">
                            <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center flex-shrink-0">
                              <ImageIcon className="w-6 h-6" />
                            </div>
                            <div className="flex-1 space-y-3">
                              <div className="flex justify-between items-center text-xs text-gray-500">
                                <span>ข้อที่ {qIdx + 1}</span>
                                <span className="bg-gray-200 px-2 py-1 rounded">Clipart IDEA: {q.clipart}</span>
                              </div>
                              <div>
                                <label className="text-xs font-semibold text-gray-600 uppercase">Question (โจทย์)</label>
                                <input 
                                  className="w-full p-2 border border-gray-300 rounded font-medium focus:ring-1 focus:ring-indigo-500 outline-none"
                                  value={q.q}
                                  onChange={(e) => handleUpdateQuestion(pIdx, qIdx, 'q', e.target.value)}
                                />
                              </div>
                              <div>
                                <label className="text-xs font-semibold text-green-600 uppercase">Answer (เฉลย)</label>
                                <input 
                                  className="w-full p-2 border border-gray-300 rounded bg-green-50 text-green-800 focus:ring-1 focus:ring-indigo-500 outline-none"
                                  value={q.a}
                                  onChange={(e) => handleUpdateQuestion(pIdx, qIdx, 'a', e.target.value)}
                                />
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* TAB 2: LISTING INFO */}
              {activeTab === 'listing' && (
                <div className="space-y-6">
                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-5">
                    
                    <div className="flex justify-between items-start">
                      <div className="w-3/4">
                        <label className="text-sm font-bold text-gray-700 block mb-1">Product Title (SEO Optimized)</label>
                        <div className="text-xl font-bold text-indigo-700 bg-indigo-50 p-3 rounded border border-indigo-100">
                          {productData.listing_info.seo_title}
                        </div>
                      </div>
                      <div className="w-1/4 text-right">
                        <label className="text-sm font-bold text-gray-700 block mb-1">Suggested Price</label>
                        <div className="text-2xl font-black text-green-600">
                          ${parseFloat(productData.listing_info.suggested_price).toFixed(2)}
                        </div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between items-end mb-1">
                        <label className="text-sm font-bold text-gray-700">Product Description</label>
                        <button onClick={() => copyToClipboard(productData.listing_info.description)} className="text-xs text-indigo-600 flex items-center gap-1 hover:underline">
                          <Copy className="w-3 h-3"/> Copy to clipboard
                        </button>
                      </div>
                      <textarea 
                        readOnly 
                        className="w-full p-4 border border-gray-300 rounded-lg h-64 bg-gray-50 focus:outline-none leading-relaxed"
                        value={productData.listing_info.description}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                      <div>
                         <label className="text-sm font-bold text-gray-700 block mb-2">Categories</label>
                         <div className="flex flex-wrap gap-2">
                           {productData.listing_info.categories.map((c, i) => (
                             <span key={i} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium">{c}</span>
                           ))}
                         </div>
                      </div>
                      <div>
                         <label className="text-sm font-bold text-gray-700 block mb-2">Tags / Keywords</label>
                         <div className="flex flex-wrap gap-2">
                           {productData.listing_info.tags.map((t, i) => (
                             <span key={i} className="bg-gray-200 text-gray-700 px-3 py-1 rounded-full text-xs font-medium">#{t}</span>
                           ))}
                         </div>
                      </div>
                    </div>

                  </div>
                </div>
              )}

              {/* TAB 3: EXPORT */}
              {activeTab === 'export' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  
                  {/* Action Panel */}
                  <div className="md:col-span-1 space-y-4">
                    <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
                      <h3 className="font-bold text-lg mb-4">Export Options</h3>
                      <button 
                        onClick={handlePrint}
                        className="w-full bg-red-500 hover:bg-red-600 text-white p-3 rounded-lg font-bold flex items-center justify-center gap-2 shadow-md transition-all"
                      >
                        <Printer className="w-5 h-5"/> Save as PDF / Print
                      </button>
                      <p className="text-xs text-gray-500 mt-3 text-center">
                        * ระบบจะเปิดหน้าต่างปริ้นต์ ให้คุณเลือก <b>"Save as PDF"</b> (ขนาด US Letter)
                      </p>
                    </div>

                    <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
                      <h3 className="font-bold text-lg mb-4 text-green-700">Answer Key</h3>
                      <div className="text-sm space-y-3 bg-gray-50 p-3 rounded border">
                        {productData.pages.map((p, i) => (
                          <div key={i}>
                            <div className="font-bold border-b pb-1 mb-1">Page {i+1}</div>
                            {p.questions.map((q, j) => (
                              <div key={j}><span className="text-gray-500">{j+1}.</span> {q.a}</div>
                            ))}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Visual Preview Panel */}
                  <div className="md:col-span-2 bg-gray-300 p-8 rounded-xl flex flex-col items-center overflow-y-auto" style={{ maxHeight: '70vh' }}>
                    
                    {/* Rendered Hidden HTML for Printing */}
                    <div id="printable-worksheet" className="w-full max-w-[816px] bg-white shadow-xl">
                      {productData.pages.map((page, pIdx) => (
                        <div key={pIdx} className="page" style={{ padding: '40px', boxSizing: 'border-box', minHeight: '1056px', borderBottom: '1px dashed #ccc' }}>
                          <div className="name-date" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', fontFamily: 'sans-serif' }}>
                            <span>Name: ______________________</span>
                            <span>Date: _______________</span>
                          </div>
                          
                          <div className="header" style={{ textAlign: 'center', borderBottom: '2px solid #333', paddingBottom: '10px', marginBottom: '30px' }}>
                            <div className="title" style={{ fontSize: '28px', fontWeight: 'bold' }}>{page.page_title}</div>
                            <div className="instructions" style={{ fontStyle: 'italic', color: '#555' }}>{page.instructions}</div>
                          </div>

                          <div className="questions">
                            {page.questions.map((q, qIdx) => (
                              <div key={qIdx} className="question-box" style={{ padding: '15px', border: '2px dashed #bbb', borderRadius: '10px', marginBottom: '20px', minHeight: '80px', overflow: 'hidden' }}>
                                <div className="clipart-box" style={{ float: 'right', width: '60px', height: '60px', border: '1px solid #eee', backgroundColor: '#fafafa', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', color: '#aaa', textAlign: 'center', borderRadius: '8px' }}>
                                  [ {q.clipart} ]
                                </div>
                                <div className="q-text" style={{ fontSize: '20px', fontWeight: '500', marginBottom: '15px' }}>
                                  {qIdx + 1}. {q.q}
                                </div>
                                <div className="answer-line" style={{ borderBottom: '1px solid #333', width: '70%', height: '20px' }}></div>
                              </div>
                            ))}
                          </div>
                          <div style={{ textAlign: 'center', marginTop: '40px', fontSize: '10px', color: '#999' }}>© {productData.listing_info.seo_title} | TPT Worksheet Builder</div>
                        </div>
                      ))}
                    </div>
                  </div>

                </div>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
