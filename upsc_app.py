import streamlit as st
import requests
import json
import time
import os
from datetime import datetime, timedelta

st.set_page_config(
    page_title="UPSC AI Mentor",
    page_icon="\U0001f3af",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"
PROFILE_FILE = "student_profile.json"
PROGRESS_FILE = "student_progress.json"


# ============ STYLING ============
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #FF6B35, #F7C948);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .task-card {
        background: #f8f9fa;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #FF6B35;
    }
    .score-big {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
    }
    .streak-fire {
        font-size: 1.5rem;
        text-align: center;
    }
    .progress-text {
        font-size: 1.1rem;
        color: #444;
    }
</style>
""", unsafe_allow_html=True)


# ============ DATA MANAGEMENT ============
def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return None

def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=2)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {
        "day_number": 1,
        "streak": 0,
        "last_active": None,
        "topics_learned": [],
        "answers_written": 0,
        "total_answer_score": 0,
        "mcqs_attempted": 0,
        "mcqs_correct": 0,
        "current_affairs_read": 0,
        "revisions_done": 0,
        "daily_tasks_completed": {},
        "subject_scores": {
            "polity": {"learned": 0, "total": 25, "mcq_correct": 0, "mcq_total": 0, "answer_score": 0, "answer_count": 0},
            "history": {"learned": 0, "total": 30, "mcq_correct": 0, "mcq_total": 0, "answer_score": 0, "answer_count": 0},
            "geography": {"learned": 0, "total": 25, "mcq_correct": 0, "mcq_total": 0, "answer_score": 0, "answer_count": 0},
            "economy": {"learned": 0, "total": 20, "mcq_correct": 0, "mcq_total": 0, "answer_score": 0, "answer_count": 0},
            "science": {"learned": 0, "total": 15, "mcq_correct": 0, "mcq_total": 0, "answer_score": 0, "answer_count": 0},
            "environment": {"learned": 0, "total": 15, "mcq_correct": 0, "mcq_total": 0, "answer_score": 0, "answer_count": 0},
            "ethics": {"learned": 0, "total": 15, "mcq_correct": 0, "mcq_total": 0, "answer_score": 0, "answer_count": 0},
            "current_affairs": {"learned": 0, "total": 50, "mcq_correct": 0, "mcq_total": 0, "answer_score": 0, "answer_count": 0}
        }
    }

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

def update_streak(progress):
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    if progress["last_active"] == today:
        return progress
    elif progress["last_active"] == yesterday:
        progress["streak"] += 1
    elif progress["last_active"] is None:
        progress["streak"] = 1
    else:
        progress["streak"] = 1
    
    progress["last_active"] = today
    return progress


def call_ai(prompt, system_prompt, max_tokens=1500):
    try:
        payload = {
            "task": "complete",
            "input_text": prompt,
            "provider": "groq",
            "model": "llama-3.3-70b-versatile",
            "max_tokens": max_tokens,
            "temperature": 0.4,
            "system_prompt": system_prompt
        }
        response = requests.post(f"{API_URL}/api/v1/complete", json=payload, timeout=60)
        result = response.json()
        if result.get("success"):
            return result.get("output", "")
        return None
    except:
        return None


# ============ UPSC SYLLABUS ============
SYLLABUS = {
    "polity": {
        "name": "Indian Polity & Governance",
        "topics": [
            "Historical Background of Indian Constitution",
            "Making of the Constitution",
            "Salient Features of the Constitution",
            "Preamble of the Constitution",
            "Union and its Territory",
            "Citizenship",
            "Fundamental Rights",
            "Directive Principles of State Policy",
            "Fundamental Duties",
            "Amendment of the Constitution",
            "Parliamentary System",
            "President of India",
            "Vice President of India",
            "Prime Minister and Council of Ministers",
            "Parliament - Lok Sabha and Rajya Sabha",
            "Supreme Court of India",
            "High Courts",
            "Governor and State Legislature",
            "Local Self Government - Panchayati Raj",
            "Local Self Government - Municipalities",
            "Election Commission of India",
            "UPSC and State PSCs",
            "Finance Commission",
            "Emergency Provisions",
            "Fundamental Rights vs DPSP"
        ]
    },
    "history": {
        "name": "Indian History",
        "topics": [
            "Indus Valley Civilization",
            "Vedic Period",
            "Buddhism and Jainism",
            "Mauryan Empire",
            "Gupta Empire",
            "South Indian Kingdoms",
            "Delhi Sultanate",
            "Mughal Empire",
            "Bhakti and Sufi Movements",
            "Maratha Empire",
            "European Arrival in India",
            "East India Company Rule",
            "Revolt of 1857",
            "Social Reform Movements",
            "Indian National Congress Formation",
            "Moderate and Extremist Phase",
            "Gandhian Era - Non Cooperation",
            "Civil Disobedience Movement",
            "Quit India Movement",
            "Subhas Chandra Bose and INA",
            "Partition and Independence",
            "Integration of Princely States",
            "World War I Impact on India",
            "World War II Impact on India",
            "Post Independence India",
            "Art and Culture of India",
            "Indian Architecture",
            "Indian Music and Dance Forms",
            "Indian Paintings",
            "Indian Literature and Languages"
        ]
    },
    "geography": {
        "name": "Indian & World Geography",
        "topics": [
            "Solar System and Universe",
            "Interior of Earth",
            "Rocks and Minerals",
            "Geomorphic Processes",
            "Atmosphere and Weather",
            "Climate of India",
            "Indian Monsoon System",
            "Ocean Currents and Tides",
            "Indian River Systems",
            "Himalayan Rivers",
            "Peninsular Rivers",
            "Soils of India",
            "Natural Vegetation of India",
            "Indian Agriculture",
            "Irrigation in India",
            "Mineral Resources of India",
            "Indian Industries",
            "Transport and Communication",
            "Population and Urbanization",
            "World Physical Geography",
            "World Climate Regions",
            "Indian States and Capitals",
            "National Parks and Wildlife",
            "Environmental Geography",
            "Disaster Management"
        ]
    },
    "economy": {
        "name": "Indian Economy",
        "topics": [
            "Basic Concepts of Economics",
            "National Income and GDP",
            "Planning in India and NITI Aayog",
            "Fiscal Policy",
            "Monetary Policy and RBI",
            "Banking System in India",
            "Inflation and Price Index",
            "Union Budget",
            "Taxation System - Direct and Indirect",
            "GST - Goods and Services Tax",
            "Foreign Trade and BOP",
            "Agriculture and Allied Sectors",
            "Industrial Policy",
            "Infrastructure Development",
            "Poverty and Unemployment",
            "Government Schemes and Programs",
            "Financial Markets",
            "International Economic Organizations",
            "Digital Economy and Fintech",
            "Sustainable Development"
        ]
    },
    "science": {
        "name": "Science & Technology",
        "topics": [
            "Physics in Everyday Life",
            "Chemistry in Everyday Life",
            "Biology Basics",
            "Human Body Systems",
            "Diseases and Health",
            "Space Technology - ISRO",
            "Nuclear Technology",
            "Defense Technology",
            "Biotechnology",
            "Nanotechnology",
            "Information Technology",
            "Artificial Intelligence and Robotics",
            "Cyber Security",
            "Intellectual Property Rights",
            "Science and Technology Policies"
        ]
    },
    "environment": {
        "name": "Environment & Ecology",
        "topics": [
            "Ecology Basics and Ecosystems",
            "Biodiversity and Conservation",
            "Environmental Pollution",
            "Climate Change and Global Warming",
            "Environmental Laws and Acts",
            "Wildlife Protection Act",
            "Forest Conservation",
            "Wetlands and Mangroves",
            "Renewable Energy Sources",
            "Waste Management",
            "Environmental Impact Assessment",
            "International Environmental Agreements",
            "Sustainable Agriculture",
            "Water Conservation",
            "Air Quality and Pollution Control"
        ]
    },
    "ethics": {
        "name": "Ethics, Integrity & Aptitude",
        "topics": [
            "Ethics and Human Interface",
            "Attitude - Content, Structure, Function",
            "Civil Service Values and Ethics",
            "Emotional Intelligence",
            "Contributions of Moral Thinkers - Indian",
            "Contributions of Moral Thinkers - Western",
            "Public Administration Ethics",
            "Accountability and Ethical Governance",
            "Corporate Governance Ethics",
            "Probity in Governance",
            "Information Sharing and Transparency",
            "RTI and Citizen Charters",
            "Code of Conduct and Code of Ethics",
            "Corruption and Anti-Corruption",
            "Case Studies in Ethics"
        ]
    }
}

def get_total_topics():
    total = 0
    for subject in SYLLABUS.values():
        total += len(subject["topics"])
    return total

def get_next_topic(progress):
    learned = progress.get("topics_learned", [])
    for subject_key, subject_data in SYLLABUS.items():
        for topic in subject_data["topics"]:
            topic_id = f"{subject_key}:{topic}"
            if topic_id not in learned:
                return subject_key, topic
    return None, None


# ============ PAGES ============
profile = load_profile()
progress = load_progress()


# ============ ONBOARDING ============
if profile is None:
    st.markdown('<p class="main-title">\U0001f3af UPSC AI Mentor</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Your Personal AI Guide to Cracking UPSC</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Welcome! Let me understand you first")
    st.markdown("*Answer these 5 questions so I can create your personalized study plan*")
    st.markdown("")
    
    with st.form("onboarding_form"):
        name = st.text_input("\U0001f464 What should I call you?", placeholder="Your name")
        
        target_year = st.selectbox("\U0001f3af Which UPSC exam are you targeting?", [
            "UPSC 2025 (This Year)",
            "UPSC 2026 (Next Year)",
            "UPSC 2027 (2 Years Away)",
            "Just Exploring"
        ])
        
        background = st.selectbox("\U0001f393 What is your educational background?", [
            "Engineering/Technical",
            "Arts/Humanities",
            "Commerce/Business",
            "Science",
            "Law",
            "Medicine",
            "Other"
        ])
        
        stage = st.selectbox("\U0001f4da Where are you in your preparation?", [
            "Complete Beginner - Haven't started yet",
            "Just Started - Less than 1 month",
            "Early Stage - 1 to 3 months",
            "Intermediate - 3 to 6 months",
            "Advanced - 6+ months",
            "Re-attempting - Attempted exam before"
        ])
        
        hours = st.selectbox("\u23f0 How many hours can you study daily?", [
            "2-3 hours (Working professional)",
            "4-5 hours (Part-time preparation)",
            "6-8 hours (Serious preparation)",
            "8-12 hours (Full-time dedication)"
        ])
        
        fear = st.selectbox("\U0001f62f What worries you most about UPSC?", [
            "Syllabus is too vast - don't know where to start",
            "I can't write good answers",
            "I don't understand current affairs",
            "I forget what I study",
            "I don't know if I'm on the right track",
            "Time management is difficult"
        ])
        
        submitted = st.form_submit_button("\U0001f680 Create My Study Plan", type="primary", use_container_width=True)
        
        if submitted and name:
            profile = {
                "name": name,
                "target_year": target_year,
                "background": background,
                "stage": stage,
                "hours": hours,
                "fear": fear,
                "created_at": datetime.now().isoformat(),
                "onboarding_complete": True
            }
            save_profile(profile)
            progress = load_progress()
            progress = update_streak(progress)
            save_progress(progress)
            st.rerun()
        elif submitted and not name:
            st.warning("Please enter your name!")

else:
    # ============ MAIN APP (After Onboarding) ============
    progress = update_streak(progress)
    save_progress(progress)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### \U0001f3af Hi, {profile['name']}!")
        st.markdown(f"\U0001f525 Streak: **{progress['streak']} days**")
        st.markdown(f"\U0001f4c5 Day **{progress['day_number']}** of preparation")
        st.markdown("---")
        
        page = st.radio("Navigate", [
            "\U0001f3e0 Today's Tasks",
            "\U0001f4d6 Learn Topic",
            "\u270d\ufe0f Write Answer",
            "\u2753 MCQ Practice",
            "\U0001f4f0 Current Affairs",
            "\U0001f504 Revision",
            "\U0001f4ca My Progress",
            "\u2699\ufe0f Profile"
        ])
        
        st.markdown("---")
        total_topics = get_total_topics()
        learned = len(progress.get("topics_learned", []))
        pct = int((learned / total_topics) * 100) if total_topics > 0 else 0
        st.markdown(f"\U0001f4da Syllabus: **{pct}%** complete")
        st.markdown(f"Topics: **{learned}/{total_topics}**")
        st.markdown("---")
        st.markdown("*UPSC AI Mentor v1.0*")
        st.markdown("*Built by Kethavath Santhosh*")
    
    
    # ============ TODAY'S TASKS ============
    if page == "\U0001f3e0 Today's Tasks":
        st.markdown(f'<p class="main-title">Good {"Morning" if datetime.now().hour < 12 else "Afternoon" if datetime.now().hour < 17 else "Evening"}, {profile["name"]}!</p>', unsafe_allow_html=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Progress overview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("\U0001f525 Streak", f"{progress['streak']} days")
        with col2:
            total_topics = get_total_topics()
            learned = len(progress.get("topics_learned", []))
            st.metric("\U0001f4da Topics", f"{learned}/{total_topics}")
        with col3:
            st.metric("\u270d\ufe0f Answers", progress["answers_written"])
        with col4:
            avg_score = 0
            if progress["answers_written"] > 0:
                avg_score = progress["total_answer_score"] / progress["answers_written"]
            st.metric("\U0001f4af Avg Score", f"{avg_score:.1f}/10")
        
        st.markdown("---")
        
        # Get next topic to study
        next_subject, next_topic = get_next_topic(progress)
        
        st.markdown("## \U0001f4cb Your 3 Tasks for Today")
        st.markdown("")
        
        # Task 1: Learn
        completed_today = progress.get("daily_tasks_completed", {}).get(today, {})
        
        task1_done = completed_today.get("learn", False)
        st.markdown(f"""### {"\u2705" if task1_done else "1\ufe0f\u20e3"} LEARN: {next_topic if next_topic else "All topics covered!"}
*Subject: {SYLLABUS.get(next_subject, {}).get("name", "")} | \u23f1 30 minutes*""")
        
        if not task1_done and next_topic:
            if st.button("\U0001f4d6 Start Learning", key="learn_btn", use_container_width=True):
                st.session_state["learn_topic"] = next_topic
                st.session_state["learn_subject"] = next_subject
                # Switch to learn page
                st.info("\U0001f449 Go to '\U0001f4d6 Learn Topic' in the sidebar to start!")
        elif task1_done:
            st.success("Completed!")
        
        st.markdown("")
        
        # Task 2: Write
        task2_done = completed_today.get("write", False)
        st.markdown(f"""### {"\u2705" if task2_done else "2\ufe0f\u20e3"} WRITE: Practice Answer Writing
*Write a 150-word answer | \u23f1 15 minutes*""")
        
        if not task2_done:
            if st.button("\u270d\ufe0f Start Writing", key="write_btn", use_container_width=True):
                st.info("\U0001f449 Go to '\u270d\ufe0f Write Answer' in the sidebar!")
        else:
            st.success("Completed!")
        
        st.markdown("")
        
        # Task 3: Current Affairs
        task3_done = completed_today.get("current", False)
        st.markdown(f"""### {"\u2705" if task3_done else "3\ufe0f\u20e3"} CURRENT AFFAIRS: Today's Important News
*Read 1 important news with UPSC analysis | \u23f1 10 minutes*""")
        
        if not task3_done:
            if st.button("\U0001f4f0 Read Today's News", key="news_btn", use_container_width=True):
                st.info("\U0001f449 Go to '\U0001f4f0 Current Affairs' in the sidebar!")
        else:
            st.success("Completed!")
        
        st.markdown("---")
        
        # Revision alert
        if len(progress.get("topics_learned", [])) > 3:
            st.markdown("### \u23f0 Revision Alert")
            st.warning(f"You have **{min(3, len(progress['topics_learned']))}** topics due for revision. Go to Revision tab!")
    
    
    # ============ LEARN TOPIC ============
    elif page == "\U0001f4d6 Learn Topic":
        st.markdown("## \U0001f4d6 Learn a Topic")
        
        # Subject selector
        subject_options = {key: val["name"] for key, val in SYLLABUS.items()}
        selected_subject = st.selectbox("Choose Subject", list(subject_options.keys()), format_func=lambda x: subject_options[x])
        
        # Topic selector
        topics = SYLLABUS[selected_subject]["topics"]
        learned_topics = progress.get("topics_learned", [])
        
        topic_status = []
        for t in topics:
            tid = f"{selected_subject}:{t}"
            status = "\u2705 " if tid in learned_topics else ""
            topic_status.append(f"{status}{t}")
        
        selected_idx = st.selectbox("Choose Topic", range(len(topics)), format_func=lambda i: topic_status[i])
        selected_topic = topics[selected_idx]
        topic_id = f"{selected_subject}:{selected_topic}"
        
        if topic_id in learned_topics:
            st.success(f"\u2705 You have already learned this topic!")
        
        if st.button("\U0001f4d6 Generate Smart Notes", type="primary", use_container_width=True):
            with st.spinner(f"Creating smart notes for: {selected_topic}..."):
                system_prompt = """You are an expert UPSC mentor. Generate smart study notes.

FORMAT STRICTLY:
1. ONE LINE SUMMARY (what is this topic in 1 sentence)
2. 5-7 KEY POINTS (bullet points, most important facts only)
3. MEMORY TRICK (mnemonic or analogy to remember)
4. EXAM ALERT (how many times asked in UPSC, which years)
5. CURRENT CONNECTION (any recent news related to this)
6. COMMON MISTAKES (what students get wrong)
7. KEYWORDS (important terms that score marks in answers)

Keep it concise. A student should finish reading in 10 minutes.
Do NOT write long paragraphs. Use bullet points everywhere."""
                
                result = call_ai(f"Generate UPSC smart notes for: {selected_topic} (Subject: {subject_options[selected_subject]})", system_prompt)
            
            if result:
                st.markdown(f"### \U0001f4d6 {selected_topic}")
                st.markdown(result)
                
                st.markdown("---")
                
                if topic_id not in learned_topics:
                    if st.button("\u2705 Mark as Learned", type="primary", use_container_width=True):
                        progress["topics_learned"].append(topic_id)
                        progress["subject_scores"][selected_subject]["learned"] += 1
                        
                        today = datetime.now().strftime("%Y-%m-%d")
                        if today not in progress["daily_tasks_completed"]:
                            progress["daily_tasks_completed"][today] = {}
                        progress["daily_tasks_completed"][today]["learn"] = True
                        
                        save_progress(progress)
                        st.success(f"\u2705 {selected_topic} marked as learned!")
                        st.rerun()
            else:
                st.error("Could not generate notes. Make sure API server is running.")
    
    
    # ============ WRITE ANSWER ============
    elif page == "\u270d\ufe0f Write Answer":
        st.markdown("## \u270d\ufe0f Answer Writing Practice")
        
        # Generate or custom question
        question_type = st.radio("Question Source", ["Generate Question for Me", "Enter My Own Question"], horizontal=True)
        
        if question_type == "Generate Question for Me":
            subject_options = {key: val["name"] for key, val in SYLLABUS.items()}
            q_subject = st.selectbox("Subject", list(subject_options.keys()), format_func=lambda x: subject_options[x], key="q_sub")
            
            if st.button("\U0001f3b2 Generate Question"):
                with st.spinner("Generating UPSC question..."):
                    system_prompt = "You are a UPSC Mains question setter. Generate exactly ONE question that could appear in UPSC Mains exam. Just the question, nothing else. Make it analytical, not factual. 150-word answer expected."
                    result = call_ai(f"Generate one UPSC Mains question on {subject_options[q_subject]}", system_prompt, max_tokens=200)
                if result:
                    st.session_state["current_question"] = result.strip()
        else:
            custom_q = st.text_area("Enter your question", placeholder="Type or paste a UPSC question here")
            if custom_q:
                st.session_state["current_question"] = custom_q
        
        # Show question and answer area
        if "current_question" in st.session_state and st.session_state["current_question"]:
            st.markdown("---")
            st.markdown(f"### Question:")
            st.markdown(f"**{st.session_state['current_question']}**")
            st.markdown(f"*Word limit: 150 words | Time: 7 minutes*")
            
            answer = st.text_area("Write your answer below:", height=250, placeholder="Start writing your answer here...")
            
            word_count = len(answer.split()) if answer else 0
            st.markdown(f"**Words: {word_count}/150**")
            
            if st.button("\U0001f4dd Submit for Evaluation", type="primary", use_container_width=True):
                if not answer or word_count < 20:
                    st.warning("Please write at least 20 words!")
                else:
                    with st.spinner("AI Examiner is evaluating your answer..."):
                        system_prompt = """You are a strict but helpful UPSC Mains examiner. Evaluate this answer.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

SCORE: X/10

GOOD POINTS:
- (what the student did well)

MISSING POINTS:
- (important points the student missed)

IMPROVEMENT TIPS:
- (specific actionable advice)

MODEL ANSWER:
(Write a brief model answer in 150 words for comparison)"""
                        
                        prompt = f"QUESTION: {st.session_state['current_question']}\n\nSTUDENT ANSWER ({word_count} words):\n{answer}"
                        result = call_ai(prompt, system_prompt, max_tokens=2000)
                    
                    if result:
                        st.markdown("---")
                        st.markdown("## \U0001f4ca Evaluation Report")
                        st.markdown(result)
                        
                        # Update progress
                        progress["answers_written"] += 1
                        try:
                            score_line = [l for l in result.split("\n") if "SCORE" in l.upper() and "/10" in l]
                            if score_line:
                                import re
                                score_match = re.search(r"(\d+\.?\d*)/10", score_line[0])
                                if score_match:
                                    score = float(score_match.group(1))
                                    progress["total_answer_score"] += score
                        except:
                            progress["total_answer_score"] += 5
                        
                        today = datetime.now().strftime("%Y-%m-%d")
                        if today not in progress["daily_tasks_completed"]:
                            progress["daily_tasks_completed"][today] = {}
                        progress["daily_tasks_completed"][today]["write"] = True
                        
                        save_progress(progress)
                    else:
                        st.error("Could not evaluate. Make sure API server is running.")
    
    
    # ============ MCQ PRACTICE ============
    elif page == "\u2753 MCQ Practice":
        st.markdown("## \u2753 MCQ Practice")
        
        subject_options = {key: val["name"] for key, val in SYLLABUS.items()}
        mcq_subject = st.selectbox("Subject", list(subject_options.keys()), format_func=lambda x: subject_options[x], key="mcq_sub")
        
        difficulty = st.selectbox("Difficulty", ["Easy", "Moderate", "Hard"])
        
        if st.button("\U0001f3b2 Generate 5 MCQs", type="primary", use_container_width=True):
            with st.spinner("Generating questions..."):
                system_prompt = f"""Generate exactly 5 UPSC Prelims style MCQs on the given topic.
Difficulty: {difficulty}

FORMAT EACH QUESTION EXACTLY LIKE THIS:

Q1. [Question text]
(A) Option A
(B) Option B
(C) Option C
(D) Option D
ANSWER: (X)
EXPLANATION: [Brief explanation why this is correct and others are wrong]

---

Make questions tricky and analytical like real UPSC prelims."""
                
                result = call_ai(f"Generate 5 UPSC MCQs on {subject_options[mcq_subject]}", system_prompt, max_tokens=2500)
            
            if result:
                st.markdown("### Questions")
                st.markdown(result)
                
                progress["mcqs_attempted"] += 5
                save_progress(progress)
            else:
                st.error("Could not generate. Make sure API server is running.")
    
    
    # ============ CURRENT AFFAIRS ============
    elif page == "\U0001f4f0 Current Affairs":
        st.markdown("## \U0001f4f0 Current Affairs for UPSC")
        
        input_method = st.radio("How to input?", ["Enter Topic/News", "Paste Full Article"], horizontal=True)
        
        if input_method == "Enter Topic/News":
            news_topic = st.text_input("Enter a current affairs topic", placeholder="Example: India-Canada diplomatic row, RBI monetary policy, Supreme Court verdict on...")
        else:
            news_topic = st.text_area("Paste the news article", height=200, placeholder="Paste any news article here...")
        
        if news_topic and st.button("\U0001f50d Analyze for UPSC", type="primary", use_container_width=True):
            with st.spinner("Analyzing UPSC relevance..."):
                system_prompt = """You are a UPSC current affairs expert. Analyze this news for UPSC relevance.

FORMAT YOUR RESPONSE EXACTLY:

WHAT HAPPENED (2-3 lines):
(Brief factual summary)

UPSC RELEVANCE:
- GS Paper: (which paper - GS1/GS2/GS3/GS4)
- Syllabus Topic: (exact syllabus topic this connects to)

IF ASKED IN PRELIMS:
- (Possible MCQ question with answer)

IF ASKED IN MAINS:
- Question: (probable Mains question)
- Key Points to Write:
  1. (point)
  2. (point)
  3. (point)
  4. (point)
  5. (point)

CONNECTED TOPICS:
- (other UPSC topics this links to)

GOVERNMENT SCHEMES RELATED:
- (any related schemes or policies)

Keep it concise and exam-focused."""
                
                result = call_ai(news_topic, system_prompt)
            
            if result:
                st.markdown("### \U0001f4f0 UPSC Analysis")
                st.markdown(result)
                
                progress["current_affairs_read"] += 1
                today = datetime.now().strftime("%Y-%m-%d")
                if today not in progress["daily_tasks_completed"]:
                    progress["daily_tasks_completed"][today] = {}
                progress["daily_tasks_completed"][today]["current"] = True
                save_progress(progress)
            else:
                st.error("Could not analyze. Make sure API server is running.")
    
    
    # ============ REVISION ============
    elif page == "\U0001f504 Revision":
        st.markdown("## \U0001f504 Quick Revision")
        
        learned = progress.get("topics_learned", [])
        
        if not learned:
            st.info("You haven't learned any topics yet. Go to 'Learn Topic' first!")
        else:
            st.markdown(f"**Topics learned: {len(learned)}**")
            st.markdown("Select a topic to revise with a quick quiz:")
            
            topic_names = [t.split(":")[1] for t in learned]
            selected = st.selectbox("Choose topic to revise", topic_names)
            
            if st.button("\U0001f504 Quick Revision Quiz (5 questions)", type="primary", use_container_width=True):
                with st.spinner(f"Creating revision quiz for: {selected}..."):
                    system_prompt = """Generate 5 quick revision questions for the given UPSC topic.
Mix of: 2 MCQs + 2 True/False + 1 One-line answer.
Include answers immediately after each question.
Keep it quick - student should finish in 3 minutes."""
                    
                    result = call_ai(f"Quick revision quiz on: {selected}", system_prompt, max_tokens=1500)
                
                if result:
                    st.markdown(f"### Revision: {selected}")
                    st.markdown(result)
                    
                    progress["revisions_done"] += 1
                    save_progress(progress)
                else:
                    st.error("Could not generate. Make sure API server is running.")
    
    
    # ============ PROGRESS ============
    elif page == "\U0001f4ca My Progress":
        st.markdown("## \U0001f4ca Your Progress Dashboard")
        
        # Overall stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("\U0001f525 Streak", f"{progress['streak']} days")
        with col2:
            total_topics = get_total_topics()
            learned = len(progress.get("topics_learned", []))
            pct = int((learned / total_topics) * 100)
            st.metric("\U0001f4da Syllabus", f"{pct}%")
        with col3:
            st.metric("\u270d\ufe0f Answers", progress["answers_written"])
        with col4:
            avg = progress["total_answer_score"] / max(progress["answers_written"], 1)
            st.metric("\U0001f4af Avg Score", f"{avg:.1f}/10")
        
        st.markdown("---")
        
        # Subject wise progress
        st.markdown("### Subject-wise Progress")
        
        for subject_key, subject_data in SYLLABUS.items():
            total = len(subject_data["topics"])
            learned_count = 0
            for t in subject_data["topics"]:
                if f"{subject_key}:{t}" in progress.get("topics_learned", []):
                    learned_count += 1
            
            pct = int((learned_count / total) * 100) if total > 0 else 0
            bar = "\u2588" * (pct // 5) + "\u2591" * (20 - pct // 5)
            
            color = "\U0001f7e2" if pct >= 60 else "\U0001f7e1" if pct >= 30 else "\U0001f534"
            
            st.markdown(f"{color} **{subject_data['name']}**: {bar} {pct}% ({learned_count}/{total})")
        
        st.markdown("---")
        
        # Activity summary
        st.markdown("### Activity Summary")
        st.markdown(f"- Topics Learned: **{len(progress.get('topics_learned', []))}**")
        st.markdown(f"- Answers Written: **{progress['answers_written']}**")
        st.markdown(f"- MCQs Attempted: **{progress['mcqs_attempted']}**")
        st.markdown(f"- Current Affairs Read: **{progress['current_affairs_read']}**")
        st.markdown(f"- Revisions Done: **{progress['revisions_done']}**")
        st.markdown(f"- Days Active: **{len(progress.get('daily_tasks_completed', {}))}**")
    
    
    # ============ PROFILE ============
    elif page == "\u2699\ufe0f Profile":
        st.markdown("## \u2699\ufe0f Your Profile")
        
        st.markdown(f"**Name:** {profile['name']}")
        st.markdown(f"**Target:** {profile['target_year']}")
        st.markdown(f"**Background:** {profile['background']}")
        st.markdown(f"**Stage:** {profile['stage']}")
        st.markdown(f"**Daily Hours:** {profile['hours']}")
        st.markdown(f"**Biggest Concern:** {profile['fear']}")
        st.markdown(f"**Joined:** {profile['created_at'][:10]}")
        
        st.markdown("---")
        
        if st.button("\U0001f504 Reset Profile (Start Over)", type="secondary"):
            if os.path.exists(PROFILE_FILE):
                os.remove(PROFILE_FILE)
            if os.path.exists(PROGRESS_FILE):
                os.remove(PROGRESS_FILE)
            st.success("Profile reset! Refreshing...")
            st.rerun()


# Footer
st.markdown("---")
st.markdown("""<div style="text-align:center;color:#888;">
UPSC AI Mentor v1.0 | Built by Kethavath Santhosh | Powered by AI Gateway
</div>""", unsafe_allow_html=True)
