# Tokenomics
An intelligent LLM routing gateway that cuts inference costs 40-60% by automatically routing queries to the cheapest model capable of answering them well. Features complexity classification, confidence-based escalation, semantic caching, circuit breakers, and learned routing policies.

## Getting Started

### Running the UI Demo

The repository includes an interactive Streamlit customer support interface with live router telemetry (cache status, tier selection, latency, complexity scores, and uncertainty breakdown).

```bash
pip install -r requirements.txt
streamlit run ui/app.py
```
 
