# IntimacyLens - Relationship Health Analysis

A local-first, privacy-focused web application that analyzes relationship health using locally hosted AI models.

## Overview

IntimacyLens allows users to upload text exports of their conversations (WhatsApp, Instagram, SMS) and uses locally hosted LLMs to analyze relationship health based on psychological frameworks (Gottman Method, Attachment Theory).

**Key Features:**
- File upload and parsing for common chat export formats
- Phonetic text detection and normalization (handles Hinglish, Romanized scripts, etc.)
- Psychological analysis with toxicity scores and affection levels
- Professional dashboard visualizations
- Complete local processing (no data leaves your machine)

## Architecture

### Backend (Python)
- **Framework**: FastAPI
- **Model Hosting**: Transformers + Accelerate for local GPU inference
- **Model**: Qwen/Qwen2.5-7B-Instruct (default) or Mistral-7B-Instruct-v0.3
- **LLM Engine**: Two-pass pipeline (Normalization → Psychological Analysis)

### Frontend (Next.js)
- **Framework**: Next.js 14+ (App Router)
- **Styling**: Tailwind CSS + Shadcn UI
- **Charts**: Recharts for visualizations
- **Design**: Medical-grade aesthetic

## Prerequisites

### Python Environment (Backend)
- Python 3.10+
- CUDA compatible GPU with 16GB+ VRAM (recommended)
  - For CPU-only setup: Use smaller models (3B tokens)
- Conda or virtual environment

### Node.js Environment (Frontend)
- Node.js 18+
- npm 9+

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/IntimacyLens.git
cd IntimacyLens
```

### 2. Setup Backend
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Install Local LLM Model:**
The backend uses HuggingFace models via Transformers. Models are automatically downloaded on first run.

### 3. Setup Frontend
```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### 1-Click First-Time Setup & Start (Windows)
1. **First-Time Setup:**
   Double-click **`setup.bat`** to automatically verify environments, set up dependencies, and build the optimized app.
2. **Launch Anytime:**
   Double-click **`start.bat`** to start IntimacyLens. It will:
   - Check and start the FastAPI backend on port `8001`
   - Start the Next.js frontend on port `3000`
   - Automatically open your default browser to `http://localhost:3000`
   - Keep a clean, unified dashboard window (press any key to cleanly shut down all services)
3. **Clean Shutdown:**
   Double-click **`stop.bat`** anytime to instantly terminate all servers.

---

### Option 1: Manual Local Setup (GPU Recommended)

1. **Start the Backend**
```bash
cd backend

# Check GPU availability
python main.py --help

# Start the API server
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# This will download the model on first run (may take 5-10 minutes)
```

2. **Start the Frontend**
```bash
cd frontend

# In another terminal window
npm run dev
```

3. **Access the Application**
Open your browser and go to: `http://localhost:3000`

### Option 2: Pre-downloaded Model

To avoid long model download times during development:

1. **Download the model once**
```bash
cd backend
python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import snapshot_download
import torch

model_name = 'Qwen/Qwen2.5-7B-Instruct'
print(f'Downloading {model_name}...')
snapshot_download(repo_id=model_name, cache_dir='.cache')
print('Model downloaded successfully!')
"
```

2. Continue with standard startup process above.

## File Formats Supported

### WhatsApp Export
- Format: `[DD/MM/YYYY, HH:MM:SS] Name: Message`
- Also supports: `DD/MM/YYYY, HH:MM - Name: Message`

### Instagram Export
- Format: `Name (Timestamp): Message`

### SMS Export
- Format: `Timestamp Name: Message`

### Generic Plain Text
- Format: `Name: Message`

### JSON Format
- Expected keys: `sender`, `text`, `timestamp`
- Accepts various key names (`author`, `from`, `name`, `content`)

## User Instructions

**The User Instruction field significantly boosts accuracy for phonetic/slang text.**

When uploading a conversation, provide helpful context about:
- Language variations (e.g., "This conversation is in Hinglish, very slangy, and informal.")
- Special abbreviations (e.g., "Contains many emojis and Romanized Hindi.")
- Conversational style (e.g., "Very formal and academic tone.")

## Analysis Output

The dashboard displays:

### Key Metrics
- **Toxicity Score** (0-100): Overall relationship toxicity score
- **Affection Levels** (0-100): Per-person affection assessment
- **Gottman Four Horsemen**: Criticism, Contempt, Defensiveness, Stonewalling scores

### Visualizations
- **Toxicity Gauge**: Radial gauge showing toxicity level
- **Affection Bars**: Comparative chart for Person A vs Person B
- **Timeline Events**: Chronological view of major emotional spikes
- **Gottman Breakdown**: Stacked bar chart of the four horsemen indicators

### Analysis Categories
- **Key Red Flags**: Identified problematic communication patterns
- **Key Green Flags**: Identified healthy communication patterns
- **Verdict**: One of "Repairable", "Critical", or "Recommend Ending"
- **Actionable Advice**: Specific recommendations for relationship improvement

### Normalized Conversation
Cleaned, standard English version of the original chat export that preserves emotional tone and conversational flow.

## Privacy Notice

⚠️ **This analysis is generated by AI and should not be taken as professional psychological advice.** For serious relationship issues, consult a licensed therapist.

- **All processing is local-only** - No data is sent to external servers
- **Files are processed on your machine** - Uploaded content never leaves your device
- **No cloud dependencies** - Complete offline functionality

## Troubleshooting

### Common Issues

#### Model Download Issues
If the model download fails:
```bash
# Clear cache and retry
rm -rf ~/.cache/huggingface
# Then restart the application
```

#### GPU Memory Issues
If you encounter out-of-memory errors:
- Reduce model size to `Qwen/Qwen2.5-3B-Instruct`
- Or use CPU mode: `device_map="cpu"`

#### CORS Issues
If frontend cannot connect to backend:
- Update `backend/main.py` to allow your frontend origin
- Or use a reverse proxy to handle CORS

### Docker Setup (Optional)

For easier deployment, consider using Docker:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Customization

### Change Model
Modify `backend/main.py` or `backend/prompt_engine.py`:
```python
model_name = "mistralai/Mistral-7B-Instruct-v0.3"
```

### Adjust Prompts
Edit prompts in `backend/prompt_engine.py`:
- `_build_translator_prompt()` for normalization
- `_build_psychologist_prompt()` for analysis

### Frontend Styling
Modify `frontend/globals.css` for custom themes:
- Add custom colors
- Adjust spacing and layout

## Performance Optimization

### Model Quantization
For better performance with smaller GPUs:
```bash
# Use 4-bit or 8-bit quantization
pip install bitsandbytes
```

### Model Pruning
Consider pruning large models for faster inference:
- Start with 3B models for CPU-only setups
- Use 7B models with quantization for good performance

### Caching
The LLM outputs are cached for repeated requests, improving response times for subsequent analyses.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.