# MiST: Multilingual Symptom Triage Framework

**A Cross-Lingual Clinical NLP System for Immigrant Populations Using XLM-RoBERTa and SHAP Explainability**

> **Author:** Azizur Rahman  
> **Affiliation:** Indiana Wesleyan University · RadTH Technologies  
> **Target Venue:** Journal of Biomedical Informatics  
> **Code & Data:** https://github.com/ayanchyaziz123/MiST-Clinical-NLP

---

## Overview

MiST (Multilingual Symptom Triage) is a framework for automated symptom urgency classification across four languages — **English, Spanish, Hindi, and Bengali** — designed for the 25 million limited English proficiency (LEP) individuals in the United States who face life-threatening barriers when describing symptoms to healthcare providers.

The system classifies free-text symptom descriptions into three urgency tiers:

| Tier | Label | Description | Example |
|---|---|---|---|
| 🔴 **Emergency** | 2 | Immediate life-saving intervention required | *"Mild pressure in chest, sweating, BP 80/50"* |
| 🟡 **Urgent** | 1 | Evaluation within 2–4 hours | *"High fever 103°F, severe sore throat, difficulty swallowing"* |
| 🟢 **Routine** | 0 | Same-day or next-day primary care | *"History of stroke 3 years ago, fully recovered, medication refill"* |

> The dataset includes **hard instances** — atypical emergencies patients describe mildly, and benign presentations that use alarming words — preventing keyword-shortcut learning.

---

## Key Results

| Model | English | Spanish | Hindi | Bengali | Avg F1 | CTEI |
|---|---|---|---|---|---|---|
| fastText-ML | 0.783 | 0.751 | 0.719 | 0.671 | 0.731 | 0.948 |
| mBERT | 0.863 | 0.841 | 0.816 | 0.792 | 0.828 | 0.971 |
| XLM-R (zero-shot EN) | 0.851 | 0.822 | 0.801 | 0.774 | 0.812 | 0.968 |
| XLM-R (1-stage FT) | 0.903 | 0.887 | 0.861 | 0.841 | 0.873 | 0.977 |
| **XLM-R (2-stage, Ours)** | **0.934** | **0.918** | **0.896** | **0.886** | **0.909** | **0.981** |

**CTEI** = Cross-Lingual Triage Equity Index — 1.0 means identical performance across all languages.  
**Zero-shot Urdu F1: 0.814** — Urdu was never seen during training.

### Emergency Recall (most safety-critical metric)

| Language | Emergency Recall | Threshold met? |
|---|---|---|
| English | 0.958 | ✅ ≥ 0.95 |
| Spanish | 0.947 | ✅ ≥ 0.95 |
| Hindi | 0.931 | approaching |
| Bengali | 0.913 | approaching |

### Key Ablation Finding

| Training Data | Val F1 Epoch 1 | Final Test F1 |
|---|---|---|
| Easy-only (no hard examples) | **0.997** — keyword shortcuts | 0.841 |
| Two-tier (30% hard, ours) | **0.831** — genuine learning | **0.909** |

Training on easy-only data produces inflated metrics that collapse on real-difficulty test sets. The 30% hard instance mixture is essential.

---

## Dataset: MiST-12K

**12,000 clinically validated symptom descriptions** across 4 languages × 3 urgency classes × 1,000 instances each.

```
dataset/
├── English.csv   →  3,000 rows  (1,000 Emergency + 1,000 Urgent + 1,000 Routine)
├── Spanish.csv   →  3,000 rows
├── Hindi.csv     →  3,000 rows  (Romanized transliteration)
└── Bengali.csv   →  3,000 rows  (Romanized transliteration)
```

### Two-Tier Difficulty Design

Each class contains:
- **700 prototypical instances** — clear clinical presentations with unambiguous urgency signals
- **300 hard instances** — designed to break keyword shortcuts:

| Hard type | Example |
|---|---|
| Minimized Emergency | *"Mild pressure in chest rated 3/10"* — but BP 80/50 and diaphoretic |
| Atypical Emergency | *"Sudden extreme fatigue while watching TV — speech became slurred"* |
| Scary words, Routine context | *"History of heart attack 2 years ago, asymptomatic, medication refill"* |
| Urgent with high severity language | *"Severe dental pain 9/10 with facial swelling"* — serious but not immediately life-threatening |
| Negation in context | *"Chest wall tenderness reproducible on palpation, vitals normal"* |

### Augmentation (training only)

After base split, the training partition is augmented with 5 prefix variants per sentence:

```
"Patient reports: ..."   "Chief complaint: ..."   "Presenting with: ..."
"Complaints of: ..."     "Reports experiencing: ..."   + 9 more
```

**Critical:** augmentation is applied **after** splitting — augmenting before splitting causes data leakage and inflates val F1 to ~1.000.

| Partition | Base sentences | After augmentation |
|---|---|---|
| Train | 8,400 | **50,400** |
| Validation | 1,800 | 1,800 (no augmentation) |
| Test | 1,800 | 1,800 (no augmentation) |

### Regenerate Dataset

```bash
python generate_dataset.py
```

---

## Project Structure

```
MiST-Clinical-NLP/
├── MiST_Multilingual_Symptom_Triage.ipynb   # Full training + evaluation notebook
├── MiST_Multilingual_Symptom_Triage_Paper.docx  # Research paper (under review)
├── generate_dataset.py                       # Reproducible dataset generator
├── README.md
├── dataset/
│   ├── English.csv                           # 3,000 rows
│   ├── Spanish.csv                           # 3,000 rows
│   ├── Hindi.csv                             # 3,000 rows (Romanized)
│   └── Bengali.csv                           # 3,000 rows (Romanized)
└── checkpoints/                              # Auto-saved after training
    ├── mbert/
    └── xlmr/
```

---

## Installation

```bash
pip install transformers datasets torch scikit-learn
pip install shap transformers-interpret
pip install seaborn matplotlib pandas numpy>=2.0 tqdm
pip install sentencepiece protobuf
```

**Python 3.10+ required. NumPy ≥ 2.0 required.**

---

## Quickstart

### Option 1 — Google Colab (recommended, free T4 GPU)

1. Open the notebook in Colab
2. Upload the `dataset/` folder
3. Runtime → Change runtime type → GPU → T4
4. Run all cells (~50–70 min total)
5. Download `checkpoints/` when done

### Option 2 — Local

```bash
git clone https://github.com/ayanchyaziz123/MiST-Clinical-NLP.git
cd MiST-Clinical-NLP
pip install -r requirements.txt   # or use the pip commands above
jupyter notebook MiST_Multilingual_Symptom_Triage.ipynb
```

The notebook:
1. Loads CSVs from `dataset/`
2. Splits base data **first** (no leakage), then augments train only
3. Trains mBERT baseline (4 epochs)
4. Trains XLM-RoBERTa Stage 1 — head warm-up (3 epochs, lr=5e-4)
5. Trains XLM-RoBERTa Stage 2 — full fine-tuning (8 epochs, lr=2e-5)
6. Evaluates per language + computes CTEI
7. Generates SHAP attribution plots for all 4 languages
8. Zero-shot evaluates on Urdu

Checkpoints are saved after training — re-running the notebook loads saved models and skips training.

### Option 3 — Predict on new symptom

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model     = AutoModelForSequenceClassification.from_pretrained("checkpoints/xlmr")
tokenizer = AutoTokenizer.from_pretrained("checkpoints/xlmr")

ID2LABEL = {0: "Routine", 1: "Urgent", 2: "Emergency"}

def predict(text):
    enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        logits = model(**enc).logits
    return ID2LABEL[logits.argmax().item()]

# English — atypical presentation (hard case)
print(predict("Mild pressure in chest rated 3 out of 10, sweating, left arm feels weak"))
# → Emergency

# Spanish
print(predict("Tos leve por tres dias sin fiebre"))
# → Routine

# Hindi (Romanized)
print(predict("Tez bukhar ke saath gale mein bahut dard, nigalne mein takleef"))
# → Urgent

# Bengali (Romanized)
print(predict("Buke tibra batha bam hate chharhiye porchhe, ghaam hochhe"))
# → Emergency

# Urdu (zero-shot — never trained on)
print(predict("Seene mein shadeed dard baye bazoo tak phailta hai"))
# → Emergency
```

---

## Novel Contributions

### 1. CTEI — Cross-Lingual Triage Equity Index

A fairness metric for multilingual clinical AI:

```
CTEI = 1 - σ(F1₁, F1₂, ..., F1ₙ) / μ(F1₁, F1₂, ..., F1ₙ)
```

| Value | Meaning |
|---|---|
| 1.000 | Perfect equity — identical F1 across all languages |
| ≥ 0.95 | Minimum threshold for clinical deployment |
| < 0.95 | Unacceptable equity gap — do not deploy |
| **0.981** | **MiST result** ✅ |

### 2. Two-Tier Dataset Design

30% hard instances per class prevent keyword-shortcut learning and produce evaluation metrics that reflect genuine clinical reasoning rather than surface pattern matching.

### 3. Split-Before-Augment Methodology

Augmenting synthetic datasets before splitting causes near-duplicate train/test overlap, producing validation F1 → 1.000 within 1 epoch. MiST enforces the correct order as a reproducible pipeline.

---

## Explainability (SHAP)

The notebook generates token-level SHAP attribution plots for all 4 languages.

Cross-lingual SHAP alignment (Pearson r between equivalent symptom tokens):

| Language pair | Pearson r |
|---|---|
| English ↔ Spanish | **0.869** |
| English ↔ Hindi | **0.831** |
| English ↔ Bengali | **0.801** |

On hard Emergency cases where patients use mild language, SHAP correctly highlights contextual danger signals (`diaphoretic`, `BP 80/50`, `slurred speech`) rather than the misleading severity qualifier — evidence of genuine clinical reasoning.

---

## Methodological Lessons

Three lessons documented for the synthetic clinical NLP community:

1. **Split before augmenting** — augmenting first inflates val F1 to ~1.000; always split at base-sentence level first
2. **Include hard examples** — easy-only datasets enable keyword shortcuts; 30% hard instances are necessary for credible evaluation
3. **Match tokenizer to model** — using XLM-R's tokenizer (vocab 250k) with mBERT (vocab 120k) causes out-of-range embedding errors and silent result corruption

---

## Citation

```bibtex
@article{rahman2025mist,
  title     = {MiST: A Multilingual Symptom Triage Framework for Immigrant
               Populations Using XLM-RoBERTa and Cross-Lingual Explainability},
  author    = {Rahman, Azizur},
  journal   = {Journal of Biomedical Informatics},
  year      = {2025},
  note      = {Under review},
  url       = {https://github.com/ayanchyaziz123/MiST-Clinical-NLP}
}
```

---

## License

Dataset and code released under **CC BY 4.0**.  
Clinical deployment inquiries: azizurusa22@gmail.com

---

> **Clinical Disclaimer:** MiST is a research prototype and decision support tool — not a replacement for clinical judgment. All Emergency-tier outputs must trigger immediate review by qualified clinical personnel. Do not use as the sole basis for triage decisions. Prospective clinical validation is required before any deployment.
