import streamlit as st
import requests
import json
import time
from datetime import datetime

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="AI Gateway — UPSC Study Tool",
    page_icon="📚",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"


# ============ STYLING ============
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ============ FILE PROCESSING ============
import sys
sys.path.insert(0, '.')
from app.file_processor import process_file, get_supported_formats


def extract_file_content(uploaded_file):
    """Extract text from uploaded file"""
    if uploaded_file is None:
        return None, None
    
    file_bytes = uploaded_file.read()
    content, file_type = process_file(file_bytes, uploaded_file.name)
    return content, file_type


def send_request(endpoint, payload):
    """Send request to API"""
    try:
        response = requests.post(
            f"{API_URL}{endpoint}",
            json=payload,
            timeout=60
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## 📚 UPSC AI Study Tool")
    st.markdown("---")
    
    page = st.radio(
        "Choose Tool",
        [
            "📝 Answer Writing",
            "❓ Quiz Practice",
            "📚 Notes Generator",
            "📰 Current Affairs",
            "📖 Explain Concept",
            "✏️ Answer Evaluator",
            "📄 File Analyzer"
        ]
    )
    
    st.markdown("---")
    st.markdown("**Built by Kethavath Santhosh**")
    st.markdown("[GitHub](https://github.com/santhosh123-vs/ai-gateway)")


# ============ PAGE: ANSWER WRITING ============
if page == "📝 Answer Writing":
    st.markdown("# 📝 UPSC Answer Writing Practice")
    st.markdown("Get AI-generated model answers for any UPSC question")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        question = st.text_area(
            "Enter UPSC Question",
            placeholder="Example: Discuss the significance of the 73rd Constitutional Amendment in strengthening grassroots democracy in India.",
            height=120
        )
        
        # File upload option
        st.markdown("**OR upload a file with questions:**")
        uploaded_file = st.file_uploader(
            "Upload PDF, Word, Excel, CSV, TXT, or Image",
            type=["pdf", "docx", "xlsx", "csv", "txt", "png", "jpg", "jpeg"],
            key="answer_file"
        )
    
    with col2:
        subject = st.selectbox("Subject", [
            "general", "polity", "history", "geography",
            "economy", "science", "ethics", "environment",
            "international_relations", "society"
        ])
        word_limit = st.selectbox("Word Limit", [150, 250, 500])
        exam_type = st.selectbox("Exam Type", ["mains", "prelims"])
    
    if st.button("📝 Generate Model Answer", type="primary", use_container_width=True):
        # Handle file upload
        input_text = question
        if uploaded_file:
            content, file_type = extract_file_content(uploaded_file)
            if file_type == "image":
                st.warning("Image questions will be described. For best results, type the question.")
                input_text = f"Analyze this image content and answer any questions visible: [Image uploaded]"
            elif file_type == "error":
                st.error(content)
                st.stop()
            else:
                input_text = content
                st.info(f"📄 Extracted text from {uploaded_file.name} ({file_type})")
                with st.expander("View extracted text"):
                    st.text(input_text[:2000])
        
        if not input_text:
            st.warning("Please enter a question or upload a file!")
            st.stop()
        
        with st.spinner("Generating model answer..."):
            result = send_request("/api/v1/upsc/answer", {
                "question": input_text,
                "subject": subject,
                "word_limit": word_limit,
                "exam_type": exam_type
            })
        
        if result.get("success"):
            st.success(f"✅ Generated in {result.get('latency_ms', 0):.0f}ms | Cost: ${result.get('cost_usd', 0):.6f}")
            st.markdown("### Model Answer")
            st.markdown(result.get("output", ""))
            
            tokens = result.get("tokens_used", {})
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Input Tokens", tokens.get("input", 0))
            with c2:
                st.metric("Output Tokens", tokens.get("output", 0))
            with c3:
                st.metric("Model", result.get("model", ""))
        else:
            st.error(result.get("detail", result.get("error", "Unknown error")))


# ============ PAGE: QUIZ PRACTICE ============
elif page == "❓ Quiz Practice":
    st.markdown("# ❓ UPSC Quiz Practice")
    st.markdown("Generate MCQ questions for any topic")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "Topic",
            placeholder="Example: Fundamental Rights, Monsoon System, Five Year Plans"
        )
        
        st.markdown("**OR upload study material:**")
        uploaded_file = st.file_uploader(
            "Upload PDF, Word, Excel, CSV, or TXT",
            type=["pdf", "docx", "xlsx", "csv", "txt"],
            key="quiz_file"
        )
    
    with col2:
        subject = st.selectbox("Subject", [
            "general", "polity", "history", "geography",
            "economy", "science", "environment"
        ], key="quiz_subject")
        num_questions = st.slider("Number of Questions", 3, 10, 5)
        difficulty = st.selectbox("Difficulty", ["easy", "moderate", "hard"])
    
    if st.button("❓ Generate Quiz", type="primary", use_container_width=True):
        input_text = topic
        if uploaded_file:
            content, file_type = extract_file_content(uploaded_file)
            if file_type != "error":
                input_text = f"Generate questions based on this content:\n{content}"
                st.info(f"📄 Loaded content from {uploaded_file.name}")
        
        if not input_text:
            st.warning("Please enter a topic or upload a file!")
            st.stop()
        
        with st.spinner("Generating quiz questions..."):
            result = send_request("/api/v1/upsc/quiz", {
                "topic": input_text,
                "subject": subject,
                "num_questions": num_questions,
                "difficulty": difficulty
            })
        
        if result.get("success"):
            st.success(f"✅ {num_questions} questions generated!")
            st.markdown("### Quiz Questions")
            st.markdown(result.get("output", ""))
        else:
            st.error(result.get("detail", result.get("error", "Unknown error")))


# ============ PAGE: NOTES GENERATOR ============
elif page == "📚 Notes Generator":
    st.markdown("# 📚 Smart Notes Generator")
    st.markdown("Generate UPSC-focused study notes for any topic")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "Topic",
            placeholder="Example: Judicial Review, Green Revolution, WTO"
        )
        
        st.markdown("**OR upload source material:**")
        uploaded_file = st.file_uploader(
            "Upload PDF, Word, Excel, CSV, or TXT",
            type=["pdf", "docx", "xlsx", "csv", "txt"],
            key="notes_file"
        )
    
    with col2:
        subject = st.selectbox("Subject", [
            "general", "polity", "history", "geography",
            "economy", "science", "environment", "ethics"
        ], key="notes_subject")
        detail_level = st.selectbox("Detail Level", ["brief", "detailed", "comprehensive"])
    
    if st.button("📚 Generate Notes", type="primary", use_container_width=True):
        input_text = topic
        if uploaded_file:
            content, file_type = extract_file_content(uploaded_file)
            if file_type != "error":
                input_text = f"Generate UPSC notes from this material:\n{content}"
                st.info(f"📄 Loaded from {uploaded_file.name}")
        
        if not input_text:
            st.warning("Please enter a topic or upload a file!")
            st.stop()
        
        with st.spinner("Generating study notes..."):
            result = send_request("/api/v1/upsc/notes", {
                "topic": input_text,
                "subject": subject,
                "detail_level": detail_level
            })
        
        if result.get("success"):
            st.success(f"✅ Notes generated!")
            st.markdown("### Study Notes")
            st.markdown(result.get("output", ""))
        else:
            st.error(result.get("detail", result.get("error", "Unknown error")))


# ============ PAGE: CURRENT AFFAIRS ============
elif page == "📰 Current Affairs":
    st.markdown("# 📰 Current Affairs Analyzer")
    st.markdown("Analyze any news topic for UPSC relevance")
    st.markdown("---")
    
    topic = st.text_area(
        "Paste News Topic or Article",
        placeholder="Example: India-Middle East-Europe Economic Corridor (IMEC) announced at G20 Summit",
        height=150
    )
    
    st.markdown("**OR upload news article:**")
    uploaded_file = st.file_uploader(
        "Upload PDF, Word, TXT",
        type=["pdf", "docx", "txt"],
        key="current_file"
    )
    
    analysis_type = st.selectbox("Analysis Type", ["comprehensive", "brief", "exam_focused"])
    
    if st.button("📰 Analyze", type="primary", use_container_width=True):
        input_text = topic
        if uploaded_file:
            content, file_type = extract_file_content(uploaded_file)
            if file_type != "error":
                input_text = content
                st.info(f"📄 Loaded from {uploaded_file.name}")
        
        if not input_text:
            st.warning("Please enter a topic or upload a file!")
            st.stop()
        
        with st.spinner("Analyzing for UPSC relevance..."):
            result = send_request("/api/v1/upsc/current-affairs", {
                "topic": input_text,
                "analysis_type": analysis_type
            })
        
        if result.get("success"):
            st.success("✅ Analysis complete!")
            st.markdown("### UPSC Analysis")
            st.markdown(result.get("output", ""))
        else:
            st.error(result.get("detail", result.get("error", "Unknown error")))


# ============ PAGE: EXPLAIN CONCEPT ============
elif page == "📖 Explain Concept":
    st.markdown("# 📖 Concept Explainer")
    st.markdown("Get any concept explained in simple, UPSC-friendly language")
    st.markdown("---")
    
    concept = st.text_input(
        "What concept do you want to understand?",
        placeholder="Example: What is Collegium System, What is El Nino, What is Fiscal Deficit"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("Subject", [
            "general", "polity", "history", "geography",
            "economy", "science", "environment", "ethics"
        ], key="explain_subject")
    with col2:
        level = st.selectbox("Explanation Level", ["beginner", "intermediate", "advanced"])
    
    if st.button("📖 Explain", type="primary", use_container_width=True):
        if not concept:
            st.warning("Please enter a concept!")
            st.stop()
        
        with st.spinner("Generating explanation..."):
            result = send_request("/api/v1/upsc/explain", {
                "concept": concept,
                "subject": subject,
                "level": level
            })
        
        if result.get("success"):
            st.success(f"✅ Explained in {result.get('latency_ms', 0):.0f}ms")
            st.markdown("### Explanation")
            st.markdown(result.get("output", ""))
        else:
            st.error(result.get("detail", result.get("error", "Unknown error")))


# ============ PAGE: ANSWER EVALUATOR ============
elif page == "✏️ Answer Evaluator":
    st.markdown("# ✏️ Answer Evaluator")
    st.markdown("Get your UPSC answers evaluated by AI examiner")
    st.markdown("---")
    
    question = st.text_area(
        "UPSC Question",
        placeholder="Enter the UPSC question here",
        height=100
    )
    
    your_answer = st.text_area(
        "Your Answer",
        placeholder="Type or paste your answer here for evaluation",
        height=250
    )
    
    st.markdown("**OR upload your answer:**")
    uploaded_file = st.file_uploader(
        "Upload your answer (PDF, Word, TXT, Image)",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        key="eval_file"
    )
    
    word_limit = st.selectbox("Expected Word Limit", [150, 250, 500], key="eval_word")
    
    if st.button("✏️ Evaluate My Answer", type="primary", use_container_width=True):
        answer_text = your_answer
        if uploaded_file:
            content, file_type = extract_file_content(uploaded_file)
            if file_type != "error" and file_type != "image":
                answer_text = content
                st.info(f"📄 Answer loaded from {uploaded_file.name}")
        
        if not question or not answer_text:
            st.warning("Please enter both the question and your answer!")
            st.stop()
        
        with st.spinner("Evaluating your answer..."):
            result = send_request("/api/v1/upsc/evaluate", {
                "question": question,
                "your_answer": answer_text,
                "word_limit": word_limit
            })
        
        if result.get("success"):
            st.success("✅ Evaluation complete!")
            st.markdown("### Evaluation Report")
            st.markdown(result.get("output", ""))
        else:
            st.error(result.get("detail", result.get("error", "Unknown error")))


# ============ PAGE: FILE ANALYZER ============
elif page == "📄 File Analyzer":
    st.markdown("# 📄 File Analyzer")
    st.markdown("Upload any document and get AI-powered analysis")
    st.markdown("---")
    
    st.markdown("### Supported Formats")
    formats = get_supported_formats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📄 Documents**")
        for f in formats["documents"]:
            st.markdown(f"- {f}")
    with col2:
        st.markdown("**📊 Spreadsheets**")
        for f in formats["spreadsheets"]:
            st.markdown(f"- {f}")
    with col3:
        st.markdown("**🖼️ Images**")
        for f in formats["images"]:
            st.markdown(f"- {f}")
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "Upload your file",
        type=["pdf", "docx", "xlsx", "csv", "txt", "png", "jpg", "jpeg"],
        key="analyze_file"
    )
    
    analysis_task = st.selectbox("What do you want to do?", [
        "Summarize the content",
        "Generate UPSC notes from this",
        "Generate quiz questions from this",
        "Analyze for UPSC current affairs relevance",
        "Extract key facts and data",
        "Explain the concepts in this document"
    ])
    
    if uploaded_file and st.button("🔍 Analyze File", type="primary", use_container_width=True):
        content, file_type = extract_file_content(uploaded_file)
        
        if file_type == "error":
            st.error(content)
            st.stop()
        
        if file_type == "image":
            st.image(uploaded_file, caption="Uploaded Image", width=400)
            st.info("Image analysis: Text will be described based on image content")
            content = "Analyze this uploaded image and provide detailed analysis"
        
        st.info(f"📄 Extracted {len(content)} characters from {uploaded_file.name}")
        
        with st.expander("View extracted content"):
            st.text(content[:3000])
        
        # Map task to endpoint
        task_map = {
            "Summarize the content": ("/api/v1/summarize", {
                "task": "summarize",
                "input_text": content,
                "provider": "groq",
                "max_tokens": 1500,
                "temperature": 0.4
            }),
            "Generate UPSC notes from this": ("/api/v1/upsc/notes", {
                "topic": content,
                "subject": "general",
                "detail_level": "detailed"
            }),
            "Generate quiz questions from this": ("/api/v1/upsc/quiz", {
                "topic": content,
                "subject": "general",
                "num_questions": 5,
                "difficulty": "moderate"
            }),
            "Analyze for UPSC current affairs relevance": ("/api/v1/upsc/current-affairs", {
                "topic": content,
                "analysis_type": "exam_focused"
            }),
            "Extract key facts and data": ("/api/v1/extract", {
                "task": "extract",
                "input_text": content,
                "provider": "groq",
                "max_tokens": 1500,
                "temperature": 0.3
            }),
            "Explain the concepts in this document": ("/api/v1/upsc/explain", {
                "concept": content,
                "subject": "general",
                "level": "intermediate"
            })
        }
        
        endpoint, payload = task_map[analysis_task]
        
        with st.spinner(f"Analyzing {uploaded_file.name}..."):
            result = send_request(endpoint, payload)
        
        if result.get("success"):
            st.success(f"✅ Analysis complete! ({result.get('latency_ms', 0):.0f}ms)")
            st.markdown("### Analysis Result")
            st.markdown(result.get("output", ""))
        elif result.get("output"):
            st.markdown("### Result")
            st.markdown(result.get("output", ""))
        else:
            st.error(result.get("detail", result.get("error", "Unknown error")))


# ============ FOOTER ============
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888;">
        AI Gateway UPSC Study Tool v1.0 | Built by Kethavath Santhosh | 
        Powered by Groq + Llama 3.3 70B
    </div>
    """,
    unsafe_allow_html=True
)
