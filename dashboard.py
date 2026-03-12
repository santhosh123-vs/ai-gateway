import streamlit as st
import requests
import json
import time
import pandas as pd
from datetime import datetime

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="AI Gateway Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

# ============ CUSTOM STYLING ============
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)


# ============ HELPER FUNCTIONS ============
def fetch_metrics():
    try:
        response = requests.get(f"{API_URL}/api/v1/metrics", timeout=5)
        return response.json()
    except:
        return None


def fetch_health():
    try:
        response = requests.get(f"{API_URL}/api/v1/health", timeout=5)
        return response.json()
    except:
        return None


def fetch_logs(limit=50):
    try:
        response = requests.get(f"{API_URL}/api/v1/logs?limit={limit}", timeout=5)
        return response.json()
    except:
        return None


def fetch_models():
    try:
        response = requests.get(f"{API_URL}/api/v1/models", timeout=5)
        return response.json()
    except:
        return None


def send_ai_request(task, input_text, provider="groq", model=None, max_tokens=500, temperature=0.7):
    try:
        payload = {
            "task": task,
            "input_text": input_text,
            "provider": provider,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        if model:
            payload["model"] = model

        response = requests.post(
            f"{API_URL}/api/v1/{task}",
            json=payload,
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## 🤖 AI Gateway")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "🧪 Test API", "📋 Request Logs", "⚙️ Models & Config"],
        index=0
    )

    st.markdown("---")

    # Auto-refresh toggle
    auto_refresh = st.checkbox("🔄 Auto Refresh (5s)", value=False)

    if auto_refresh:
        time.sleep(5)
        st.rerun()

    st.markdown("---")
    st.markdown("### Quick Actions")

    if st.button("🗑️ Clear Cache"):
        try:
            requests.delete(f"{API_URL}/api/v1/cache/clear", timeout=5)
            st.success("Cache cleared!")
        except:
            st.error("Failed to clear cache")

    st.markdown("---")
    st.markdown(
        """
        **Built by Kethavath Santhosh**
        
        AI Gateway — Unified LLM API
        
        [GitHub](https://github.com/yourusername/ai-gateway)
        """
    )


# ============ PAGE 1: DASHBOARD ============
if page == "📊 Dashboard":
    st.markdown('<p class="main-header">🤖 AI Gateway Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Unified LLM API — Real-Time Monitoring</p>', unsafe_allow_html=True)

    # Fetch data
    health = fetch_health()
    metrics = fetch_metrics()

    if not health or not metrics:
        st.error("⚠️ Cannot connect to AI Gateway server. Make sure it's running on port 8000.")
        st.code("uvicorn app.main:app --reload --port 8000", language="bash")
        st.stop()

    # ---- Provider Status ----
    st.markdown("### 🟢 Provider Status")
    provider_cols = st.columns(4)

    providers = health.get("providers", {})
    icons = {"groq": "⚡", "google": "🔵", "openai": "🟢", "anthropic": "🟠"}

    for i, (name, status) in enumerate(providers.items()):
        with provider_cols[i % 4]:
            if status == "active":
                st.success(f"{icons.get(name, '🔘')} **{name.upper()}**\n\n✅ Active")
            else:
                st.warning(f"{icons.get(name, '🔘')} **{name.upper()}**\n\n⚠️ {status}")

    st.markdown("---")

    # ---- Key Metrics ----
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Requests",
            value=metrics.get("total_requests", 0)
        )

    with col2:
        st.metric(
            label="Total Cost",
            value=f"${metrics.get('total_cost_usd', 0):.6f}"
        )

    with col3:
        st.metric(
            label="Avg Latency",
            value=f"{metrics.get('average_latency_ms', 0):.0f}ms"
        )

    with col4:
        st.metric(
            label="Error Rate",
            value=f"{metrics.get('error_rate', 0) * 100:.1f}%"
        )

    with col5:
        cache_stats = metrics.get("cache_stats", {})
        st.metric(
            label="Cache Hit Rate",
            value=f"{cache_stats.get('hit_rate', 0) * 100:.1f}%"
        )

    st.markdown("---")

    # ---- Charts ----
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("### 📊 Requests by Task")
        tasks = metrics.get("requests_by_task", {})
        if tasks:
            task_df = pd.DataFrame({
                "Task": list(tasks.keys()),
                "Count": list(tasks.values())
            })
            st.bar_chart(task_df.set_index("Task"))
        else:
            st.info("No requests yet. Test the API first!")

    with chart_col2:
        st.markdown("### 🏢 Requests by Provider")
        providers_data = metrics.get("requests_by_provider", {})
        if providers_data:
            provider_df = pd.DataFrame({
                "Provider": list(providers_data.keys()),
                "Count": list(providers_data.values())
            })
            st.bar_chart(provider_df.set_index("Provider"))
        else:
            st.info("No requests yet. Test the API first!")

    st.markdown("---")

    # ---- Cache Stats ----
    st.markdown("### 💾 Cache Statistics")
    cache_col1, cache_col2, cache_col3 = st.columns(3)

    with cache_col1:
        st.metric("Cached Entries", cache_stats.get("total_entries", 0))
    with cache_col2:
        st.metric("Cache Hits", cache_stats.get("hits", 0))
    with cache_col3:
        st.metric("Cache Misses", cache_stats.get("misses", 0))

    # ---- Uptime ----
    st.markdown("---")
    st.markdown(f"**⏱️ Uptime:** {health.get('uptime', 'Unknown')}")


# ============ PAGE 2: TEST API ============
elif page == "🧪 Test API":
    st.markdown('<p class="main-header">🧪 Test AI Gateway</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Send requests and see real-time results</p>', unsafe_allow_html=True)

    # Input form
    col1, col2 = st.columns([2, 1])

    with col1:
        input_text = st.text_area(
            "Input Text",
            value="Artificial intelligence is transforming how businesses operate. Machine learning models can now process natural language, recognize images, and make predictions with remarkable accuracy. Companies like Google, OpenAI, and Anthropic are leading the charge in developing more capable AI systems.",
            height=150
        )

    with col2:
        task = st.selectbox("Task", ["summarize", "classify", "extract", "complete"])

        models_data = fetch_models()
        available_models = []
        if models_data:
            for provider_info in models_data.get("providers", {}).values():
                available_models.extend(provider_info.get("models", []))

        model = st.selectbox(
            "Model",
            ["auto (default)"] + available_models
        )

        temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1)
        max_tokens = st.slider("Max Tokens", 100, 2000, 500, 100)

    if st.button("🚀 Send Request", type="primary", use_container_width=True):
        with st.spinner("Calling AI Gateway..."):
            selected_model = None if model == "auto (default)" else model

            result = send_ai_request(
                task=task,
                input_text=input_text,
                provider="groq",
                model=selected_model,
                max_tokens=max_tokens,
                temperature=temperature
            )

        if result.get("success"):
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("### ✅ Success!")
            st.markdown('</div>', unsafe_allow_html=True)

            # Result metrics
            res_col1, res_col2, res_col3, res_col4 = st.columns(4)
            with res_col1:
                st.metric("Provider", result.get("provider", ""))
            with res_col2:
                st.metric("Model", result.get("model", "").split("/")[-1])
            with res_col3:
                st.metric("Latency", f"{result.get('latency_ms', 0):.0f}ms")
            with res_col4:
                st.metric("Cost", f"${result.get('cost_usd', 0):.6f}")

            # Output
            st.markdown("### 📝 AI Output")
            st.markdown(result.get("output", ""))

            # Token details
            st.markdown("### 📊 Token Usage")
            tokens = result.get("tokens_used", {})
            tok_col1, tok_col2, tok_col3 = st.columns(3)
            with tok_col1:
                st.metric("Input Tokens", tokens.get("input", 0))
            with tok_col2:
                st.metric("Output Tokens", tokens.get("output", 0))
            with tok_col3:
                st.metric("Total Tokens", tokens.get("total", 0))

            # Cached?
            if result.get("cached"):
                st.info("⚡ This response was served from CACHE — zero cost, zero latency!")

            # Raw JSON
            with st.expander("🔍 View Raw JSON Response"):
                st.json(result)

        else:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.markdown("### ❌ Error")
            st.error(result.get("detail", result.get("error", "Unknown error")))
            st.markdown('</div>', unsafe_allow_html=True)


# ============ PAGE 3: REQUEST LOGS ============
elif page == "📋 Request Logs":
    st.markdown('<p class="main-header">📋 Request Logs</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">View recent API requests and responses</p>', unsafe_allow_html=True)

    logs_data = fetch_logs(50)

    if logs_data and logs_data.get("recent_requests"):
        requests_list = logs_data["recent_requests"]

        st.markdown(f"**Total Requests:** {logs_data.get('total_requests', 0)}")
        st.markdown(f"**Showing:** Last {len(requests_list)} requests")
        st.markdown("---")

        # Convert to DataFrame
        df = pd.DataFrame(requests_list)

        if not df.empty:
            # Summary stats
            sum_col1, sum_col2, sum_col3 = st.columns(3)
            with sum_col1:
                st.metric("Avg Latency", f"{df['latency_ms'].mean():.0f}ms")
            with sum_col2:
                st.metric("Total Cost", f"${df['cost_usd'].sum():.6f}")
            with sum_col3:
                success_count = df['success'].sum()
                st.metric("Success Rate", f"{(success_count/len(df))*100:.0f}%")

            st.markdown("---")

            # Latency chart
            st.markdown("### ⏱️ Latency Over Time")
            if len(df) > 1:
                st.line_chart(df["latency_ms"])

            # Cost chart
            st.markdown("### 💰 Cost Per Request")
            if len(df) > 1:
                st.bar_chart(df["cost_usd"])

            # Request table
            st.markdown("### 📋 Request Details")
            display_df = df[["task", "provider", "model", "latency_ms", "cost_usd", "success", "cached", "timestamp"]]
            st.dataframe(display_df, use_container_width=True)

    else:
        st.info("No requests logged yet. Go to 'Test API' page to make some requests!")


# ============ PAGE 4: MODELS & CONFIG ============
elif page == "⚙️ Models & Config":
    st.markdown('<p class="main-header">⚙️ Models & Configuration</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Available models and pricing</p>', unsafe_allow_html=True)

    models_data = fetch_models()

    if models_data:
        # Available providers
        st.markdown("### 🏢 Available Providers & Models")

        for provider_name, provider_info in models_data.get("providers", {}).items():
            with st.expander(f"{'⚡' if provider_name == 'groq' else '🔘'} {provider_name.upper()}", expanded=True):
                st.markdown(f"**Default Model:** `{provider_info.get('default', 'N/A')}`")
                st.markdown("**Available Models:**")
                for m in provider_info.get("models", []):
                    costs = models_data.get("cost_per_1k_tokens", {}).get(m, {})
                    input_cost = costs.get("input", "N/A")
                    output_cost = costs.get("output", "N/A")
                    st.markdown(f"- `{m}` — Input: ${input_cost}/1K tokens | Output: ${output_cost}/1K tokens")

        # Fallback order
        st.markdown("---")
        st.markdown("### 🔄 Fallback Order")
        fallback = models_data.get("fallback_order", [])
        for i, provider in enumerate(fallback, 1):
            st.markdown(f"{i}. **{provider.upper()}**")

        # Cost comparison
        st.markdown("---")
        st.markdown("### 💰 Cost Comparison (per 1K tokens)")

        cost_data = models_data.get("cost_per_1k_tokens", {})
        if cost_data:
            cost_rows = []
            for model_name, costs in cost_data.items():
                cost_rows.append({
                    "Model": model_name,
                    "Input Cost ($)": costs.get("input", 0),
                    "Output Cost ($)": costs.get("output", 0),
                    "Total (approx)": costs.get("input", 0) + costs.get("output", 0)
                })

            cost_df = pd.DataFrame(cost_rows).sort_values("Total (approx)")
            st.dataframe(cost_df, use_container_width=True)

            # Visual comparison
            st.markdown("### 📊 Cost Comparison Chart")
            chart_df = pd.DataFrame({
                "Model": [r["Model"] for r in cost_rows],
                "Input": [r["Input Cost ($)"] for r in cost_rows],
                "Output": [r["Output Cost ($)"] for r in cost_rows]
            }).set_index("Model")
            st.bar_chart(chart_df)

    else:
        st.error("Cannot fetch model data. Is the server running?")


# ============ FOOTER ============
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 0.85rem;">
        AI Gateway v1.0.0 | Built with FastAPI + Streamlit | 
        Unified LLM API with Smart Routing, Caching & Monitoring
    </div>
    """,
    unsafe_allow_html=True
)
