import streamlit as st
import requests
import json
import time
import sys
import os
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="AI Gateway Dashboard",
    page_icon="\U0001f916",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.file_processor import process_file


st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: 700; text-align: center; margin-bottom: 0.5rem;}
    .sub-header {font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 2rem;}
</style>
""", unsafe_allow_html=True)


def fetch_metrics():
    try:
        return requests.get(f"{API_URL}/api/v1/metrics", timeout=5).json()
    except:
        return None

def fetch_health():
    try:
        return requests.get(f"{API_URL}/api/v1/health", timeout=5).json()
    except:
        return None

def fetch_logs(limit=50):
    try:
        return requests.get(f"{API_URL}/api/v1/logs?limit={limit}", timeout=5).json()
    except:
        return None

def fetch_models():
    try:
        return requests.get(f"{API_URL}/api/v1/models", timeout=5).json()
    except:
        return None

def send_ai_request(task, input_text, provider="groq", model=None, max_tokens=500, temperature=0.7):
    try:
        payload = {"task": task, "input_text": input_text, "provider": provider, "max_tokens": max_tokens, "temperature": temperature}
        if model:
            payload["model"] = model
        return requests.post(f"{API_URL}/api/v1/{task}", json=payload, timeout=30).json()
    except Exception as e:
        return {"success": False, "error": str(e)}


with st.sidebar:
    st.markdown("## \U0001f916 AI Gateway")
    st.markdown("---")
    page = st.radio("Navigate", ["\U0001f4ca Dashboard", "\U0001f9ea Test API", "\U0001f4cb Request Logs", "\u2699\ufe0f Models & Config"], index=0)
    st.markdown("---")
    auto_refresh = st.checkbox("\U0001f504 Auto Refresh (5s)", value=False)
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    st.markdown("---")
    st.markdown("### Quick Actions")
    if st.button("\U0001f5d1\ufe0f Clear Cache"):
        try:
            requests.delete(f"{API_URL}/api/v1/cache/clear", timeout=5)
            st.success("Cache cleared!")
        except:
            st.error("Failed")
    st.markdown("---")
    st.markdown("**Built by Kethavath Santhosh**")
    st.markdown("AI Gateway - Unified LLM API")
    st.markdown("[GitHub](https://github.com/santhosh123-vs/ai-gateway)")


if page == "\U0001f4ca Dashboard":
    st.markdown('<p class="main-header">\U0001f916 AI Gateway Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Unified LLM API - Real-Time Monitoring</p>', unsafe_allow_html=True)
    health = fetch_health()
    metrics = fetch_metrics()
    if not health or not metrics:
        st.error("Cannot connect to AI Gateway server. Make sure it is running on port 8000.")
        st.code("uvicorn app.main:app --reload --port 8000", language="bash")
        st.stop()

    st.markdown("### Provider Status")
    provider_cols = st.columns(4)
    providers = health.get("providers", {})
    icons = {"groq": "\u26a1", "google": "\U0001f535", "openai": "\U0001f7e2", "anthropic": "\U0001f7e0"}
    for i, (name, status) in enumerate(providers.items()):
        with provider_cols[i % 4]:
            if status == "active":
                st.success(f"{icons.get(name, '')} **{name.upper()}**\n\nActive")
            else:
                st.warning(f"{icons.get(name, '')} **{name.upper()}**\n\n{status}")
    st.markdown("---")

    st.markdown("### Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Requests", metrics.get("total_requests", 0))
    with col2:
        st.metric("Total Cost", f"${metrics.get('total_cost_usd', 0):.6f}")
    with col3:
        st.metric("Avg Latency", f"{metrics.get('average_latency_ms', 0):.0f}ms")
    with col4:
        st.metric("Error Rate", f"{metrics.get('error_rate', 0) * 100:.1f}%")
    with col5:
        cache_stats = metrics.get("cache_stats", {})
        st.metric("Cache Hit Rate", f"{cache_stats.get('hit_rate', 0) * 100:.1f}%")
    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("### Requests by Task")
        tasks = metrics.get("requests_by_task", {})
        if tasks:
            st.bar_chart(pd.DataFrame({"Task": list(tasks.keys()), "Count": list(tasks.values())}).set_index("Task"))
        else:
            st.info("No requests yet. Test the API first!")
    with chart_col2:
        st.markdown("### Requests by Provider")
        prov_data = metrics.get("requests_by_provider", {})
        if prov_data:
            st.bar_chart(pd.DataFrame({"Provider": list(prov_data.keys()), "Count": list(prov_data.values())}).set_index("Provider"))
        else:
            st.info("No requests yet.")
    st.markdown("---")

    st.markdown("### Cache Statistics")
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        st.metric("Cached Entries", cache_stats.get("total_entries", 0))
    with cc2:
        st.metric("Cache Hits", cache_stats.get("hits", 0))
    with cc3:
        st.metric("Cache Misses", cache_stats.get("misses", 0))


elif page == "\U0001f9ea Test API":
    st.markdown('<p class="main-header">\U0001f9ea Test AI Gateway</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Send requests with text or file uploads</p>', unsafe_allow_html=True)

    input_method = st.radio("Input Method", ["Text Input", "File Upload"], horizontal=True)

    col1, col2 = st.columns([2, 1])

    input_text = ""

    with col1:
        if input_method == "Text Input":
            input_text = st.text_area("Input Text", value="Artificial intelligence is transforming how businesses operate. Machine learning models can now process natural language, recognize images, and make predictions with remarkable accuracy.", height=200)
        else:
            st.markdown("### Upload a File")
            uploaded_file = st.file_uploader(
                "Supported: PDF, Word, Excel, CSV, TXT, Images",
                type=["pdf", "docx", "doc", "xlsx", "xls", "csv", "txt", "md", "png", "jpg", "jpeg", "gif", "webp"]
            )

            if uploaded_file:
                file_bytes = uploaded_file.read()
                content, file_type = process_file(file_bytes, uploaded_file.name)

                if file_type == "error":
                    st.error(content)
                elif file_type == "image":
                    st.image(uploaded_file, caption=f"Uploaded: {uploaded_file.name}", width=400)
                    input_text = "This is an uploaded image. Please describe and analyze the visual content of this image in detail."
                    st.info("Image uploaded! AI will analyze based on text description capabilities.")
                else:
                    input_text = content
                    st.success(f"Extracted {len(content)} characters from {uploaded_file.name} ({file_type})")
                    with st.expander("View Extracted Content"):
                        st.text(content[:3000])
                        if len(content) > 3000:
                            st.info(f"Showing first 3000 of {len(content)} characters")

    with col2:
        task = st.selectbox("Task", ["summarize", "classify", "extract", "complete"])
        models_data = fetch_models()
        available_models = []
        if models_data:
            for provider_info in models_data.get("providers", {}).values():
                available_models.extend(provider_info.get("models", []))
        model = st.selectbox("Model", ["auto (default)"] + available_models)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1)
        max_tokens = st.slider("Max Tokens", 100, 2000, 500, 100)

    if st.button("\U0001f680 Send Request", type="primary", use_container_width=True):
        if not input_text:
            st.warning("Please enter text or upload a file!")
            st.stop()

        with st.spinner("Calling AI Gateway..."):
            selected_model = None if model == "auto (default)" else model
            result = send_ai_request(task=task, input_text=input_text, provider="groq", model=selected_model, max_tokens=max_tokens, temperature=temperature)

        if result.get("success"):
            st.success("### Success!")
            res_col1, res_col2, res_col3, res_col4 = st.columns(4)
            with res_col1:
                st.metric("Provider", result.get("provider", ""))
            with res_col2:
                st.metric("Model", result.get("model", "").split("/")[-1])
            with res_col3:
                st.metric("Latency", f"{result.get('latency_ms', 0):.0f}ms")
            with res_col4:
                st.metric("Cost", f"${result.get('cost_usd', 0):.6f}")
            st.markdown("### AI Output")
            st.markdown(result.get("output", ""))
            st.markdown("### Token Usage")
            tokens = result.get("tokens_used", {})
            t1, t2, t3 = st.columns(3)
            with t1:
                st.metric("Input Tokens", tokens.get("input", 0))
            with t2:
                st.metric("Output Tokens", tokens.get("output", 0))
            with t3:
                st.metric("Total Tokens", tokens.get("total", 0))
            if result.get("cached"):
                st.info("This response was served from CACHE!")
            with st.expander("View Raw JSON"):
                st.json(result)
        else:
            st.error(result.get("detail", result.get("error", "Unknown error")))


elif page == "\U0001f4cb Request Logs":
    st.markdown('<p class="main-header">\U0001f4cb Request Logs</p>', unsafe_allow_html=True)
    logs_data = fetch_logs(50)
    if logs_data and logs_data.get("recent_requests"):
        rl = logs_data["recent_requests"]
        st.markdown(f"**Total:** {logs_data.get('total_requests', 0)} | **Showing:** {len(rl)}")
        df = pd.DataFrame(rl)
        if not df.empty:
            s1, s2, s3 = st.columns(3)
            with s1:
                st.metric("Avg Latency", f"{df['latency_ms'].mean():.0f}ms")
            with s2:
                st.metric("Total Cost", f"${df['cost_usd'].sum():.6f}")
            with s3:
                st.metric("Success Rate", f"{(df['success'].sum()/len(df))*100:.0f}%")
            st.markdown("---")
            st.markdown("### Latency Over Time")
            st.line_chart(df["latency_ms"])
            st.markdown("### Cost Per Request")
            st.bar_chart(df["cost_usd"])
            st.markdown("### Request Details")
            st.dataframe(df[["task", "provider", "model", "latency_ms", "cost_usd", "success", "cached", "timestamp"]], use_container_width=True)
    else:
        st.info("No requests yet.")


elif page == "\u2699\ufe0f Models & Config":
    st.markdown('<p class="main-header">\u2699\ufe0f Models & Configuration</p>', unsafe_allow_html=True)
    models_data = fetch_models()
    if models_data:
        st.markdown("### Available Providers & Models")
        for pname, pinfo in models_data.get("providers", {}).items():
            with st.expander(f"{pname.upper()}", expanded=True):
                st.markdown(f"**Default:** {pinfo.get('default', 'N/A')}")
                for m in pinfo.get("models", []):
                    costs = models_data.get("cost_per_1k_tokens", {}).get(m, {})
                    st.markdown(f"- {m} | Input: ${costs.get('input', 'N/A')}/1K | Output: ${costs.get('output', 'N/A')}/1K")
        st.markdown("---")
        st.markdown("### Fallback Order")
        for i, p in enumerate(models_data.get("fallback_order", []), 1):
            st.markdown(f"{i}. **{p.upper()}**")
        st.markdown("---")
        st.markdown("### Cost Comparison")
        cost_data = models_data.get("cost_per_1k_tokens", {})
        if cost_data:
            rows = [{"Model": m, "Input": c.get("input",0), "Output": c.get("output",0)} for m,c in cost_data.items()]
            st.dataframe(pd.DataFrame(rows).sort_values("Input"), use_container_width=True)


st.markdown("---")
st.markdown('<div style="text-align:center;color:#888;">AI Gateway v1.0.0 | Built by Kethavath Santhosh | FastAPI + Streamlit</div>', unsafe_allow_html=True)
