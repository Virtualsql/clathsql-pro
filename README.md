# ⚡ ClathSQL Pro — Intelligent Data Routing Engine

**HJK-INC Enterprise Core | Virtual SQL Organisation**  
*Automate Your Storage Decisions with AI-Powered Intelligence*

---

![License](https://img.shields.io/badge/License-MIT-blue.svg)  
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)  
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)  

---

## 📖 Overview

**ClathSQL Pro** is an autonomous data ingestion and routing platform designed for high-volume, multi-format data pipelines. By leveraging TinyLlama-based neural inference, it classifies incoming unstructured content into three execution paths:

| Route | Technology | Use Case |
|-------|------------|----------|
| **SQL** | SQLite (Relational) | Structured tabular data, queryable records |
| **NOSQL** | JSON Document Store | Unstructured documents, nested schemas |
| **PLOT** | Matplotlib Visualization | Time-series, numerical sequences, metrics |

Built by **hjk-inc**, this system embodies our philosophy: *"Build once, automate everywhere."* No manual classification needed—the brain decides, the vault stores, the GUI visualizes.

---

## 🎯 Key Features

### 🔹 Hybrid AI Routing Logic
- **Neural Inference**: TinyLlama-1.1B Chat model for semantic understanding
- **Regex Bypass**: Zero-latency pattern matching for obvious cases (JSON → NOSQL, SELECT → SQL)
- **Warmup Sequence**: Pre-loaded model weights eliminate first-inference lag

### 🔹 Dual-Storage Vault
- **SQLite Backend**: Indexed temporal database with auto-timestamps
- **Append-Only JSON**: Lock-safe NoSQL document storage with PID concurrency control

### 🔹 Enterprise Dashboard
- **CustomTkinter UI**: Dark-mode optimized for extended operations
- **Real-time Monitoring**: CPU/RAM telemetry via `psutil`
- **Embedded Visualization**: Matplotlib plots rendered directly in GUI
- **Export Automation**: One-click CSV export of vault contents

### 🔹 Thread-Safe Architecture
- All heavy operations run on background threads
- Non-blocking UI during AI inference (5-15s models)
- Graceful shutdown with resource cleanup

---

## 🚀 Installation & Setup

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install customtkinter torch transformers pandas matplotlib psutil
```

### Quick Start
```bash
git clone https://github.com/virtualsql/clathsql-pro.git
cd clathsql-pro
python clathsql_pro.py
```

### First Run Checklist
1. ✅ Model downloads automatically (~1GB TinyLlama cache)
2. ✅ Watch status indicator turn green ("Brain Online")
3. ✅ Paste test data → Click "CLUTCH DATA"
4. ✅ Verify vault files created (`hjk_clath_vault.db`, `hjk_clath_docs.json`)

---

---

## 🧪 Usage Examples

### 1. Routing to SQL
```text
Paste: "SELECT * FROM users WHERE id > 100"
→ AI detects SQL keywords → Stored in relational table
```

### 2. Routing to NoSQL
```json
Paste: {"user_id": 42, "action": "purchase", "amount": 99.99}
→ Regex bypasses AI → Appended as JSON document
```

### 3. Routing to Plot
```text
Paste:
10.5
20.3
15.8
25.1
30.4
→ AI identifies numerical sequence → Generated trend plot
```

---

## 🛠️ Configuration

### Environment Variables (Optional)
```bash
# .env file at project root
MODEL_ID=TinyLlama/TinyLlama-1.1B-Chat-v1.0   # Switch to Phi-3 or Llama-3
DEVICE=0                                       # 0 for GPU, -1 for CPU
MAX_TOKENS=5                                   # Response length limit
```

### Customizing AI Model
Edit `ClathSQL_Brain.__init__`:
```python
model_id = "mistralai/Mistral-7B-Instruct-v0.1"  # Higher accuracy
torch_dtype=torch.float16                        # Reduce VRAM usage
```

---

## 📊 Vault Statistics

Access real-time metrics via the sidebar panel:

| Metric | Description |
|--------|-------------|
| **SQL Entries** | Count of records in `clath_stream` table |
| **NoSQL Docs** | Lines written to document store |
| **CPU Power** | Real-time processor utilization |
| **RAM Usage** | System memory consumption percentage |

Refresh manually or watch auto-updates every 30 seconds.

---

## 🤝 Integration Guide

### Connect to Maker's Newspaper Platform
Expose ClathSQL routing logic via FastAPI for cross-service automation:

```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/route-data")
def route_data(data: str):
    decision = brain.clutch_logic(data)
    return {"route": decision}
```

Then consume from your other HJK-INC microservices without duplicating infrastructure.

### Embed in Existing Applications
Import core classes directly:
```python
from clathsql_pro import ClathSQL_Brain, ClathSQL_Vault

brain = ClathSQL_Brain(lambda x, y: None)  # Disable UI callback
vault = ClathSQL_Vault()
decision = brain.clutch_logic(user_input)
vault.store_sql(user_input) if decision == "SQL" else vault.store_nosql(user_input)
```

---

## 🔒 Security Considerations

| Risk | Mitigation |
|------|------------|
| **Path Injection** | Input sanitized before file I/O |
| **Concurrent Writes** | PID lock file prevents race conditions |
| **Memory Leaks** | Explicit thread cleanup on app close |
| **Model Exploits** | Temperature=0.1 limits adversarial outputs |

> ⚠️ **Warning**: For production use, add input size limits (max 1MB per payload) and authentication middleware.

---

## 🐛 Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| First inference takes ~15s | Expected | Warmup runs automatically on launch |
| Plot fails with <2 numbers | Intentional | Display warning instead of fake data |
| Large JSON slows append | Ongoing | Batch writes planned v2.1 |

---

## 📅 Roadmap

- [x] V2.0 — Stable release with hybrid routing
- [ ] V2.1 — Multi-threaded batch processing
- [ ] V2.2 — REST API layer for remote routing
- [ ] V2.3 — PostgreSQL/Redis adapters
- [ ] V2.4 — Cloud deployment templates (Docker/Kubernetes)

---

## 👥 Contributing

Pull requests welcome! Please follow these guidelines:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit with conventional messages (`feat:`, `fix:`, `docs:`)
4. Push to branch and open Pull Request
5. Ensure all tests pass before merge

---

## 📄 License

MIT License © 2024 **HJK-INC**. See [LICENSE](LICENSE) for full details.

---

## 📞 Support

For enterprise support, integration consulting, or bulk deployment:

---

<div align="center">

### Built with ❤️ by the HJK-INC Engineering Team

*"Lazy by design, powerful by necessity"*

</div>
