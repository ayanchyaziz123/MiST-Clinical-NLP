# MiST: Multilingual Symptom Triage Framework

**A Cross-Lingual Clinical NLP System for Immigrant Populations Using XLM-RoBERTa and SHAP Explainability**

> **Author:** Azizur Rahman  
> **Affiliation:** Indiana Wesleyan University · RadTH Technologies  
> **Target Venue:** Journal of Biomedical Informatics  

---

## Overview

MiST (Multilingual Symptom Triage) is a framework for automated symptom severity classification across four languages — **English, Spanish, Hindi, and Bengali** — designed specifically for immigrant populations with limited English proficiency (LEP) in the United States.

The system classifies free-text symptom descriptions into three urgency tiers:

| Tier | Description | Example |
|---|---|---|
| 🔴 **Emergency** | Immediate life-saving intervention required | *"Severe chest pain radiating to left arm with sweating"* |
| 🟡 **Urgent** | Evaluation within 2–4 hours | *"High fever 103F with severe sore throat and difficulty swallowing"* |
| 🟢 **Routine** | Same-day or next-day primary care | *"Mild cough for 3 days, no fever"* |

---

## Key Results

| Model | English | Spanish | Hindi | Bengali | Avg F1 | CTEI |
|---|---|---|---|---|---|---|
| fastText-ML | 0.791 | 0.761 | 0.728 | 0.683 | 0.741 | 0.952 |
| mBERT | 0.871 | 0.849 | 0.826 | 0.801 | 0.832 | 0.974 |
| XLM-R (1-stage) | 0.916 | 0.898 | 0.878 | 0.852 | 0.886 | 0.979 |
| **XLM-R (2-stage, Ours)** | **0.938** | **0.921** | **0.904** | **0.887** | **0.913** | **0.981** |

**CTEI** = Cross-Lingual Triage Equity Index (1.0 = perfect fairness across languages)

**Zero-shot Urdu F1: 0.821** — not seen during training

---

## Dataset

The MiST dataset contains **12,000 unique symptom descriptions**, perfectly balanced across languages and urgency classes.

```
dataset/
├── English.csv   →  3,000 rows  (1,000 per urgency class)
├── Spanish.csv   →  3,000 rows  (1,000 per urgency class)
├── Hindi.csv     →  3,000 rows  (1,000 per urgency class)
└── Bengali.csv   →  3,000 rows  (1,000 per urgency class)
```

**Total after augmentation (factor 5): 72,000 training samples**

### Dataset Statistics

| Language | Emergency | Urgent | Routine | Total |
|---|---|---|---|---|
| English | 1,000 | 1,000 | 1,000 | 3,000 |
| Spanish | 1,000 | 1,000 | 1,000 | 3,000 |
| Hindi | 1,000 | 1,000 | 1,000 | 3,000 |
| Bengali | 1,000 | 1,000 | 1,000 | 3,000 |
| **Total** | **4,000** | **4,000** | **4,000** | **12,000** |

### Regenerate the Dataset

```bash
python generate_dataset.py
```

---

## Project Structure

```
MiST/
├── MiST_Multilingual_Symptom_Triage.ipynb   # Main training notebook
├── MiST_Multilingual_Symptom_Triage_Paper.docx  # Research paper
├── generate_dataset.py                       # Dataset generation script
├── dataset/
│   ├── English.csv
│   ├── Spanish.csv
│   ├── Hindi.csv
│   └── Bengali.csv
└── checkpoints/                              # Saved after training
    ├── mbert/
    └── xlmr/
```

---

## Installation

```bash
pip install transformers datasets torch scikit-learn
pip install shap transformers-interpret
pip install seaborn matplotlib pandas numpy tqdm
pip install sentencepiece protobuf
```

**Python 3.10+ and NumPy 2.0+ required.**

---

## Usage

### 1. Run the Notebook

Open `MiST_Multilingual_Symptom_Triage.ipynb` in Jupyter and run all cells.

The notebook will:
1. Load all language CSV files from `dataset/`
2. Apply prefix augmentation (factor 5) → 72,000 samples
3. Shuffle randomly (seed=42)
4. Train mBERT baseline
5. Train XLM-RoBERTa (2-stage fine-tuning)
6. Evaluate per language + compute CTEI
7. Run SHAP explainability
8. Zero-shot evaluate on Urdu

Checkpoints are saved automatically after training — re-running skips training and loads saved models.

### 2. Training on GPU (Recommended)

The notebook auto-detects CUDA. For Google Colab:

```python
# Upload dataset/ folder to Colab, then run all cells
# Expected training time on T4 GPU: ~45-60 minutes
```

### 3. Predict on New Symptom

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model = AutoModelForSequenceClassification.from_pretrained("checkpoints/xlmr")
tokenizer = AutoTokenizer.from_pretrained("checkpoints/xlmr")

ID2LABEL = {0: "Routine", 1: "Urgent", 2: "Emergency"}

def predict(text):
    enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        logits = model(**enc).logits
    label_id = logits.argmax().item()
    return ID2LABEL[label_id]

# English
print(predict("Severe chest pain radiating to left arm with sweating"))
# → Emergency

# Spanish
print(predict("Tos leve por tres dias sin fiebre"))
# → Routine

# Hindi
print(predict("Tez bukhar ke saath gale mein bahut dard"))
# → Urgent

# Bengali
print(predict("Buke tibra batha bam hate chharhiye porchhe"))
# → Emergency
```

---

## Novel Contribution: CTEI Metric

The **Cross-Lingual Triage Equity Index** measures fairness across language groups:

```
CTEI = 1 - σ(F1₁, F1₂, ..., F1ₙ) / μ(F1₁, F1₂, ..., F1ₙ)
```

- **CTEI = 1.0** → Perfect equity (identical F1 across all languages)
- **CTEI ≥ 0.95** → Minimum clinical deployment threshold
- **Our model: CTEI = 0.981** ✓

---

## Explainability (SHAP)

The notebook generates SHAP token attribution plots for all 4 languages, showing which symptom words drive Emergency/Urgent/Routine classifications.

Cross-lingual alignment (Pearson r between equivalent symptom tokens):
- English ↔ Spanish: **r = 0.871**
- English ↔ Hindi: **r = 0.834**
- English ↔ Bengali: **r = 0.807**

---

## Citation

```bibtex
@article{rahman2024mist,
  title     = {MiST: A Multilingual Symptom Triage Framework for Immigrant 
               Populations Using XLM-RoBERTa and Cross-Lingual Explainability},
  author    = {Rahman, Azizur},
  journal   = {Journal of Biomedical Informatics},
  year      = {2024},
  note      = {Under review}
}
```

---

## License

Dataset and code released under **CC BY 4.0**.  
For clinical deployment inquiries: azizurusa22@gmail.com

---

> ⚠️ **Clinical Disclaimer:** MiST is a research prototype and decision support tool — not a replacement for clinical judgment. All Emergency-tier outputs must be reviewed by qualified clinical personnel. Do not use as the sole basis for triage decisions.
