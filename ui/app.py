import streamlit as st
import time
import json

# Setup page config
st.set_page_config(
    page_title="TechStore AI Support",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .metric-box {
        background-color: #1e1e2e;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #89b4fa;
    }
    .metric-title {
        font-size: 12px;
        color: #a6adc8;
        margin-bottom: 2px;
    }
    .metric-value {
        font-size: 16px;
        font-weight: bold;
        color: #cdd6f4;
    }
    .tier-economy { color: #a6e3a1; font-weight: bold; }
    .tier-frontier { color: #f38ba8; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize chat history and router metadata in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm the TechStore Support Assistant. How can I help you today?"}
    ]
if "last_routing_metadata" not in st.session_state:
    st.session_state.last_routing_metadata = None

# Sidebar: Routing Inspector (The "Under the Hood" view)
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/bot.png", width=60)
    st.title("Router Inspector")
    st.caption("Live telemetry from the LLM Cost-Optimized Gateway")
    st.divider()

    meta = st.session_state.last_routing_metadata

    if not meta:
        st.info("Waiting for first query...")
    else:
        # Cache Status
        cache_color = "green" if meta['cache_hit'] else "gray"
        st.markdown(f"**Cache Status**: :{cache_color}[{meta['cache_status'].upper()}]")
        
        # Tier Selection
        tier_color = "tier-economy" if meta['tier'] == "economy" else "tier-frontier"
        tier_display = "Economy (GPT-5.6 Luna)" if meta['tier'] == "economy" else "Frontier (GPT-5.6 Sol)"
        st.markdown(f"**Selected Tier**: <span class='{tier_color}'>{tier_display}</span>", unsafe_allow_html=True)
        
        # Cost metrics
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Estimated Cost</div>
            <div class="metric-value">${meta['cost']:.5f}</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Latency</div>
            <div class="metric-value">{meta['latency_ms']} ms</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("Decision Signals")
        
        # Classification & Escalation details
        if not meta['cache_hit']:
            st.markdown(f"**Complexity Score**: `{meta['complexity_score']:.2f}` (Threshold: 0.50)")
            
            if meta['tier'] == "economy":
                st.caption("Passed to Economy model.")
                # Show Uncertainty signals
                st.markdown("**Uncertainty Check (Layer 3)**:")
                st.progress(meta['uncertainty_composite'], text=f"Composite Score: {meta['uncertainty_composite']:.2f} / 0.45")
                with st.expander("Signal Breakdown"):
                    st.json(meta['uncertainty_signals'])
            else:
                if meta.get('escalated'):
                    st.error("⚠️ Escalated to Frontier!")
                    st.caption(f"Reason: Uncertainty score {meta['uncertainty_composite']:.2f} > 0.45")
                else:
                    st.caption("Sent directly to Frontier model.")
        else:
            st.caption(f"Cache Distance: `{meta['cache_distance']:.3f}`")
            if meta['cache_status'] == 'semantic':
                st.caption("Matched via semantic similarity.")

# Main Chat Interface
st.header("TechStore Customer Support")
st.caption("Ask about policies, order status, or product comparisons.")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("E.g., What's your return window?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- MOCK ROUTER LOGIC (To be replaced with actual API call) ---
    # We simulate different routing behaviors based on keywords for the demo
    with st.spinner("Processing through Router..."):
        time.sleep(0.6) # simulate latency
        
        prompt_lower = prompt.lower()
        
        # Simulate different scenarios based on the input
        if "return" in prompt_lower or "policy" in prompt_lower:
            # Simple FAQ -> Economy
            response = "TechStore offers a 30-day return window for all unused and sealed electronics. Open-box items are subject to a 15% restocking fee."
            meta = {
                "cache_hit": False, "cache_status": "miss",
                "tier": "economy", "cost": 0.00026, "latency_ms": 340,
                "complexity_score": 0.12, "uncertainty_composite": 0.15,
                "uncertainty_signals": {"logprob": 0.0, "hedge": 0.1, "length": 0.0, "repeat": 0.05, "struct": 0.0},
                "escalated": False
            }
        elif "order" in prompt_lower:
            # Order Status -> Economy but volatile (no semantic cache)
            response = "I checked your order. It is currently being prepared for shipment and should dispatch by tomorrow evening."
            meta = {
                "cache_hit": False, "cache_status": "miss",
                "tier": "economy", "cost": 0.00028, "latency_ms": 310,
                "complexity_score": 0.22, "uncertainty_composite": 0.10,
                "uncertainty_signals": {"logprob": 0.0, "hedge": 0.0, "length": 0.0, "repeat": 0.1, "struct": 0.0},
                "escalated": False
            }
        elif "charged" in prompt_lower or "dispute" in prompt_lower or "money" in prompt_lower:
            # Complex Billing -> Direct to Frontier
            response = "I see multiple charges on your account. I have initiated an investigation with our billing department and voided the duplicate pending transactions. You will receive an email confirmation shortly."
            meta = {
                "cache_hit": False, "cache_status": "miss",
                "tier": "frontier", "cost": 0.00460, "latency_ms": 1450,
                "complexity_score": 0.88, "uncertainty_composite": 0.0,
                "escalated": False
            }
        elif "vs" in prompt_lower or "compare" in prompt_lower:
            # Product Comparison -> Starts Economy, but might escalate
            response = "While both the X200 and Y500 are great, the Y500 features adaptive noise cancellation which is significantly better for a noisy open-plan office."
            meta = {
                "cache_hit": False, "cache_status": "miss",
                "tier": "frontier", "cost": 0.00486, "latency_ms": 1900, # Paid for both!
                "complexity_score": 0.45, "uncertainty_composite": 0.65, # Triggered escalation
                "uncertainty_signals": {"logprob": 0.3, "hedge": 0.5, "length": 0.0, "repeat": 0.0, "struct": 0.0},
                "escalated": True
            }
        else:
            # Semantic Cache Hit simulation for repeated questions
            response = "The SoundWave X200 features Active Noise Cancellation (ANC), 40-hour battery life, and Bluetooth 5.3."
            meta = {
                "cache_hit": True, "cache_status": "semantic", "cache_distance": 0.035,
                "tier": "economy", "cost": 0.00000, "latency_ms": 12,
                "complexity_score": 0.0, "uncertainty_composite": 0.0,
                "escalated": False
            }
            
    # Update state
    st.session_state.last_routing_metadata = meta
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Force sidebar update
    st.rerun()
