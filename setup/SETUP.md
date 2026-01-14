# Quick Setup Guide

## Prerequisites
- Python 3.9 or higher
- 4 GB RAM minimum
- 3.5 GB free disk space

## Installation Steps

### 1. Extract the Project
```bash
cd RAG_Sanskrit_Saurabh
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r code/requirements.txt
```

### 4. Download Model
**IMPORTANT:** Download the TinyLlama model file and place it in the `models/` folder:
- File name: `tinyllama.gguf`
- Size: 637 MB
- Location: Place in `models/tinyllama.gguf`

**Download links:**
- Hugging Face: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF
- Choose: `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf`
- Rename to: `tinyllama.gguf`

### 5. Verify Setup
```bash
# Check if model exists
ls -lh models/tinyllama.gguf

# Run test
python code/main.py --test
```

## Usage

### CLI Mode (Recommended for first run)
```bash
python code/main.py --test
```

### Interactive Mode
```bash
python code/main.py
```

### Web Interface
```bash
streamlit run "webapp stremlit/app.py"
```
Then open: http://localhost:8501

## Troubleshooting

### Model Not Found
```bash
# Make sure file is named exactly:
models/tinyllama.gguf
```

### Module Not Found
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r code/requirements.txt
```

### Slow Performance
- Close other applications
- Ensure CPU has 4+ cores
- Check available RAM (need 4 GB minimum)

## Expected Results
- ✅ 9/9 test queries pass
- ✅ Average latency: ~7-10 seconds
- ✅ No errors or warnings
- ✅ Answers in both English and Sanskrit

---

For detailed documentation, see **README.md**
