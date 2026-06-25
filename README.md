# MiST: A Multilingual Symptom Triage Framework for Immigrant Populations Using XLM-RoBERTa and Cross-Lingual Explainability

**Author:** Azizur Rahman  
**Affiliation:** Indiana Wesleyan University · RadTH Technologies  
**Target Venue:** Journal of Biomedical Informatics  
**Code & Data:** https://github.com/ayanchyaziz123/MiST-Clinical-NLP

---

## Abstract

Approximately 25 million individuals in the United States have limited English proficiency (LEP), and language barriers during emergency triage are independently associated with delayed care, urgency misclassification, and preventable adverse outcomes. We present **MiST** (Multilingual Symptom Triage), a cross-lingual clinical NLP framework that classifies free-text symptom descriptions into three Emergency Severity Index-aligned urgency tiers — Emergency, Urgent, and Routine — across English, Spanish, Hindi, and Bengali. The core technical contribution is **MiST-12K**, a 12,000-instance dataset constructed with a two-tier adversarial design: 20% prototypical instances provide basic class orientation, while 80% are deliberately hard — minimized true emergencies, atypical presentations, and cross-vocabulary instances in which Emergency cases use Routine language ("calling to refill a prescription, mentioned face drooping") and Routine cases use Emergency language ("heart attack five years ago, fully recovered, here for annual follow-up"). This design forecloses two distinct shortcut learning failure modes we identify and characterize: leading-token shortcuts (model classifies on the first severity adjective) and vocabulary-cluster shortcuts (model identifies class from aggregate lexical distribution without reading context). We fine-tune XLM-RoBERTa using a two-stage procedure — classification head warm-up followed by full fine-tuning — and evaluate with a novel fairness metric, the Cross-Lingual Triage Equity Index (CTEI). Our best model achieves macro-averaged F1 of 0.909 across four languages, Emergency recall of 0.958 in English, CTEI of 0.981, and zero-shot F1 of 0.814 on Urdu, a language absent from all training data. We document four methodological lessons for synthetic clinical NLP: split before augmenting, include leading-token-free adversarial examples, inject cross-vocabulary instances, and match tokenizer to model encoder.

---

## 1. Introduction

### 1.1 Motivation

In the United States, triage nurses stratify patient urgency using the Emergency Severity Index (ESI), a five-level instrument that determines care priority from immediate life-threatening conditions to non-urgent complaints [1]. The instrument presupposes that a patient can articulate symptoms clearly and in English. For the approximately 25 million individuals classified as having limited English proficiency (LEP) [2], this assumption fails at the point of initial contact — precisely when accurate urgency assessment is most consequential.

Empirical evidence documents consistent harm from this failure. LEP patients wait significantly longer for initial pain assessment, are more frequently undertriaged to lower-acuity categories, and experience higher rates of adverse events compared to English-proficient patients at comparable acuity [3, 4]. These disparities widen at institutions lacking access to real-time professional interpreter services, which describes the majority of emergency departments in the United States.

A natural language processing system capable of accepting symptom text in any supported language and outputting an urgency tier represents a tractable, low-friction intervention: it requires no workflow restructuring, no additional personnel, and can operate as a passive pre-triage layer that flags potential emergencies for immediate clinical attention regardless of language. However, building such a system for even provisional clinical use requires solving three non-trivial problems simultaneously: cross-lingual generalization across typologically distinct languages, robustness to the atypical presentations that characterize the most safety-critical triage failures, and interpretable predictions that clinicians can audit and override.

### 1.2 The Shortcut Learning Problem in Synthetic Clinical NLP

We identify and characterize two distinct shortcut learning failure modes that arise when training triage classifiers on synthetic symptom datasets.

**Leading-token shortcuts.** The simplest failure: a model classifies on the first severity adjective in the sentence. A dataset in which Emergency templates begin with "Severe chest pain…" and Routine templates begin with "Mild cough…" teaches the model to read only the first word. Validation F1 reaches 0.997 within one epoch — not because the model has learned clinical reasoning, but because it has learned a trivial lexical rule. This failure is invisible on in-distribution validation sets constructed from the same templates.

**Vocabulary-cluster shortcuts.** A subtler and more persistent failure: even after removing leading severity adjectives, the model learns that Emergency class instances aggregate toward a vocabulary cluster (chest, arm, breathing, unconscious, ICU, diaphoretic) while Routine instances aggregate toward a different cluster (refill, recovered, history of, asymptomatic, musculoskeletal). No single word gives away the answer, but the distribution of words across the sentence does. A model with sufficient capacity and training data — such as mBERT fine-tuned over 25,000+ augmented instances — can learn this cluster mapping within one training epoch, again without reading clinical context.

The clinical consequence of both shortcuts is identical: a model that appears to work in validation but fails on realistic patient language, particularly for the cases that matter most — a patient describing a myocardial infarction as "a bit of pressure" (Emergency vocabulary-deprived, cluster-breaking), or a well patient mentioning a five-year-old heart attack during a refill visit (Emergency vocabulary in a Routine context, cluster-breaking in the opposite direction).

### 1.3 Contributions

1. **MiST-12K**: A 12,000-instance multilingual triage dataset with a two-tier adversarial design that forecloses both leading-token and vocabulary-cluster shortcuts through template restructuring and cross-vocabulary injection.
2. **Cross-vocabulary injection**: A dataset construction technique in which Emergency class instances deliberately use Routine register language, and Routine instances deliberately use Emergency clinical vocabulary, forcing contextual reasoning rather than lexical pattern matching.
3. **Two-stage XLM-RoBERTa fine-tuning**: Classification head warm-up followed by full fine-tuning, achieving macro-F1 of 0.909 across four languages.
4. **CTEI**: The Cross-Lingual Triage Equity Index, a fairness metric quantifying performance parity across languages for clinical AI.
5. **Zero-shot Urdu transfer**: F1 of 0.814 on a language absent from all training data.
6. **Four methodological lessons**: Split before augmenting; remove leading severity tokens from prototypical templates; inject cross-vocabulary adversarial instances; match tokenizer to model encoder.

---

## 2. Related Work

### 2.1 Multilingual Clinical NLP

Large pre-trained multilingual models — mBERT [5] and XLM-RoBERTa [6] — have demonstrated strong zero-shot cross-lingual transfer on general NLP benchmarks. Their application to clinical text has primarily focused on English EHR data [7, 8]. Work on non-English clinical NLP is sparser, targeting European languages with existing clinical corpora [9]. South Asian languages in clinical contexts — Hindi, Bengali, Urdu — remain substantially underrepresented in the literature, and romanized transliterations of these languages, which dominate informal health communication in messaging apps and community health worker interactions, have received essentially no attention.

### 2.2 Automated Emergency Triage

Rule-based NLP systems [10] and traditional ML classifiers [11] have been applied to emergency department chief complaints, typically in English using structured EHR fields. Deep learning approaches with BERT-family encoders have improved ESI prediction performance [12] but rely on structured clinical data rather than free-form patient-reported text. No prior work simultaneously addresses the multilingual LEP population, unstructured free-text input, and cross-language performance equity.

### 2.3 Shortcut Learning and Adversarial Dataset Construction

Gururangan et al. [13] demonstrated that NLP models systematically exploit dataset artifacts and lexical shortcuts rather than task-relevant features. In clinical triage, this problem is compounded by the natural co-occurrence of severity vocabulary with urgency labels across any template-based dataset. Counterfactual data augmentation [14] and adversarial instance inclusion [15] have been proposed as mitigations. We extend these ideas to clinical triage with a specific focus on two-level shortcut elimination: first at the leading-token level (template restructuring), then at the vocabulary-cluster level (cross-vocabulary injection), and we provide empirical ablation distinguishing the contribution of each.

---

## 3. Dataset: MiST-12K

### 3.1 Overview

MiST-12K contains 12,000 symptom descriptions distributed across four languages (English, Spanish, Hindi, Bengali) and three urgency tiers (Emergency, Urgent, Routine), with exactly 1,000 instances per language-class cell. Each cell contains 200 prototypical and 800 adversarial instances. Hindi and Bengali use romanized transliteration, reflecting the dominant register of informal digital health communication among these speaker populations.

```
dataset/
├── English.csv   →  3,000 rows  (1,000 Emergency + 1,000 Urgent + 1,000 Routine)
├── Spanish.csv   →  3,000 rows
├── Hindi.csv     →  3,000 rows  (Romanized)
└── Bengali.csv   →  3,000 rows  (Romanized)
```

### 3.2 Urgency Classes

| Label | Class | ESI v4 Criterion | Canonical Example |
|---|---|---|---|
| 2 | **Emergency** | Immediate life-saving intervention required | *ST-elevation MI with diaphoresis and BP 82/50* |
| 1 | **Urgent** | Evaluation required within 2–4 hours | *Fever 103°F, severe sore throat, unable to swallow* |
| 0 | **Routine** | Same-day or next-day primary care appropriate | *Mild lingering cough 5 days after a cold, no fever* |

### 3.3 Two-Tier Adversarial Design

Each language-class combination contains:

- **200 prototypical instances (20%)**: Unambiguous presentations with clear canonical urgency signals, sufficient for basic class orientation during training.
- **800 adversarial instances (80%)**: Designed to prevent both identified shortcut failure modes.

Adversarial instances fall into six categories:

| Category | Description | Example |
|---|---|---|
| Minimized emergency | True emergency described with mild or dismissive language | *"Mild pressure under the breastbone, probably nothing — patient says it'll pass"* (MI with ST elevation) |
| Atypical presentation | Emergency without classic presenting complaint | *"Sudden extreme fatigue while watching TV — speech became slurred"* (stroke) |
| Observer account | Family or bystander describes what the patient minimizes | *"Elderly man who insists he is fine, found to be diaphoretic with BP 80/50"* |
| Scary words, benign context | Alarming vocabulary in clearly Routine situation | *"Palpitations lasting 2–3 seconds — EKG normal, resolves spontaneously"* |
| High-severity language in non-Emergency tier | Severe descriptors that do not meet Emergency threshold | *"Severe dental pain 9/10 with facial swelling, 48 hours, vitals stable"* (Urgent) |
| **Cross-vocabulary injection** | Emergency class using Routine register; Routine class using Emergency register | See §3.4 |

### 3.4 Cross-Vocabulary Injection

The sixth adversarial category is the primary methodological innovation over template-based adversarial datasets. It directly addresses vocabulary-cluster shortcuts by ensuring that signature vocabulary from each class appears systematically in other classes.

**Emergency instances using Routine register language:**
- *"Calling to refill metoprolol — mentioned during call that right side of face is drooping since this morning"*
- *"Routine blood pressure follow-up — patient feels fine today, but BP reads 265/145 and patient wants to leave"*
- *"Patient came in for prescription renewal — while waiting in triage, developed slurred speech and denies any problem"*
- *"Mild uncomfortable pressure in chest, probably nothing — wife insisted on calling — EKG shows ST elevation in multiple leads"*

**Routine instances using Emergency register language:**
- *"Heart attack 5 years ago, stent placed, fully recovered — presenting for annual cardiac follow-up"*
- *"Chest pain — started immediately after lifting heavy boxes — completely reproducible pressing on the rib, no radiation, vitals normal"*
- *"Experienced chest tightness and difficulty breathing — resolved within 20 minutes — confirmed panic attack, EKG normal, oxygen 99%"*
- *"Stroke symptoms three years ago with full neurological recovery — here for annual neurology follow-up and prescription refill"*

These instances force the model to process the complete clinical context — not merely detect the presence of high-valence vocabulary. A vocabulary-cluster classifier assigns the first group to Routine (because "refill," "follow-up," "patient feels fine" appear) and the second group to Emergency (because "heart attack," "chest pain," "difficulty breathing" appear); both assignments are incorrect. A contextual classifier assigns them correctly.

### 3.5 Train/Validation/Test Split and Augmentation

Data is split at the base-sentence level **before** augmentation. Augmenting before splitting creates near-duplicate contamination across partitions, inflating validation F1 to near 1.0 within one epoch (Methodological Lesson 1).

| Partition | Base Sentences | After Augmentation |
|---|---|---|
| Train (70%) | 8,400 | **25,200** (3× — original + 2 prefix variants) |
| Validation (15%) | 1,800 | 1,800 (no augmentation) |
| Test (15%) | 1,800 | 1,800 (no augmentation) |

Training instances receive 2 additional prefix variants from a pool of 14 clinical chief-complaint prefixes:

```
"Patient reports: "     "Chief complaint: "     "Presenting with: "
"Complaints of: "       "Reports experiencing: " [9 additional variants]
```

The augmentation factor is deliberately set to 3× (not the maximum possible) to prevent over-exposure to synthetic patterns within a single epoch, maintaining realistic gradient step counts that require the model to learn from context rather than memorize template structure.

### 3.6 Reproducibility

```bash
python generate_dataset.py
```

Fixed random seed (42) produces identical outputs on any platform. Generation takes under 30 seconds.

---

## 4. Methodology

### 4.1 Models

**mBERT** (multilingual BERT, 110M parameters) [5]: Pre-trained on Wikipedia text from 104 languages via masked language modeling and next-sentence prediction. WordPiece vocabulary of 120,002 tokens. Used as the baseline multilingual encoder.

**XLM-RoBERTa-base** (278M parameters) [6]: Pre-trained on 2.5TB of filtered CommonCrawl text from 100 languages via masked language modeling only. SentencePiece vocabulary of 250,002 tokens. Substantially stronger cross-lingual representations than mBERT, particularly for lower-resource and South Asian languages. Primary experimental model.

Both encoders are extended with a classification head: dropout (p=0.1) followed by a linear projection from 768 hidden dimensions to 3 output logits.

### 4.2 Two-Stage Fine-Tuning

Full fine-tuning of large pre-trained transformers directly on small clinical datasets risks catastrophic forgetting of cross-lingual representations, particularly for lower-resource languages where the pre-training signal is weaker. We use a two-stage procedure designed to preserve these representations while adapting to the triage task.

**Stage 1 — Classification Head Warm-Up (3 epochs, lr = 5×10⁻⁴):**  
The encoder is frozen. Only the classification head is trained with a high learning rate. This initializes the head to a useful starting point without disturbing any pre-trained weights. The encoder's cross-lingual representations remain fully intact.

**Stage 2 — Full Fine-Tuning (8 epochs, lr = 2×10⁻⁵):**  
All weights are unfrozen and jointly optimized at a lower learning rate with a 10% linear warmup schedule. This adapts the upper encoder layers to the clinical triage domain while the lower layers, which carry the most language-general structure, change more slowly via the warmup.

The two-stage approach is particularly important for Bengali — the lowest-resource language in our training data — where a single-stage strategy risks early catastrophic forgetting of cross-lingual structure before the head has stabilized (ablated in §5.4).

### 4.3 Training Details

| Hyperparameter | mBERT | XLM-R Stage 1 | XLM-R Stage 2 |
|---|---|---|---|
| Epochs | 4 | 3 | 8 |
| Learning rate | 2×10⁻⁵ | 5×10⁻⁴ | 2×10⁻⁵ |
| Batch size | 32 | 32 | 32 |
| Max sequence length | 128 | 128 | 128 |
| Warmup steps | 10% | 10% | 10% |
| Dropout | 0.1 | 0.1 | 0.1 |
| Optimizer | AdamW | AdamW | AdamW |
| Training instances | 25,200 | 25,200 | 25,200 |

Training was performed on a T4 GPU (Google Colab). Total training time is approximately 50–70 minutes for the complete XLM-RoBERTa pipeline.

### 4.4 Baselines

| Baseline | Description |
|---|---|
| fastText-ML | Multilingual fastText on character n-gram features; lightweight non-neural baseline |
| XLM-R (zero-shot EN) | XLM-RoBERTa fine-tuned on English only, evaluated on all four languages; quantifies value of multilingual training |
| XLM-R (1-stage FT) | Standard single-stage full fine-tuning at lr=2×10⁻⁵; ablates two-stage contribution |

### 4.5 Evaluation Metrics

**Macro-averaged F1** is the primary metric, computed per language and averaged across all three classes. Preferred over accuracy because in real deployment scenarios class frequencies will not be balanced.

**Emergency recall** is the secondary safety-critical metric: the proportion of true Emergency instances correctly identified. A false negative (Emergency classified as Urgent or Routine) represents the most dangerous triage failure. We define ≥ 0.95 Emergency recall as the minimum threshold for clinical deployment consideration.

**CTEI (Cross-Lingual Triage Equity Index)** is a novel metric we introduce to quantify performance parity across supported languages:

```
CTEI = 1 − σ(F1₁, F1₂, ..., F1ₙ) / μ(F1₁, F1₂, ..., F1ₙ)
```

CTEI = 1.0 indicates identical F1 across all languages. We define CTEI ≥ 0.95 as the minimum threshold for equitable clinical deployment — a system that performs substantially better in one language than another introduces new disparities rather than addressing them.

---

## 5. Experiments and Results

### 5.1 Main Results

| Model | English F1 | Spanish F1 | Hindi F1 | Bengali F1 | Avg F1 | CTEI |
|---|---|---|---|---|---|---|
| fastText-ML | 0.791 | 0.741 | 0.712 | 0.648 | 0.723 | 0.944 |
| mBERT | 0.863 | 0.841 | 0.816 | 0.792 | 0.828 | 0.971 |
| XLM-R (zero-shot EN) | 0.851 | 0.822 | 0.812 | 0.774 | 0.815 | 0.968 |
| XLM-R (1-stage FT) | 0.903 | 0.887 | 0.861 | 0.841 | 0.873 | 0.977 |
| **XLM-R (2-stage, Ours)** | **0.934** | **0.918** | **0.896** | **0.886** | **0.909** | **0.981** |

The two-stage XLM-RoBERTa achieves the best performance across all four languages and exceeds both deployment thresholds (CTEI 0.981 > 0.95; Emergency recall 0.958, §5.2).

The performance gap between English and Bengali (0.934 vs 0.886) reflects two compounding factors: reduced Bengali coverage in XLM-RoBERTa's pre-training corpus, and the absence of a standardized romanization orthography for Bengali, producing higher intra-class surface variability. Despite this, Bengali Emergency recall reaches 0.913 — approaching clinical utility.

The zero-shot XLM-R baseline (English training only) achieves F1 of 0.774 on Bengali, substantially above chance, confirming that clinical triage concepts transfer cross-lingually through shared subword structure even without target-language training data.

### 5.2 Emergency Recall

| Language | Emergency Recall | Deployment Threshold (≥ 0.95) |
|---|---|---|
| English | **0.958** | ✅ Met |
| Spanish | **0.947** | ✅ Approaching |
| Hindi | **0.931** | approaching |
| Bengali | **0.913** | approaching |

English meets the threshold; Spanish approaches it. Hindi and Bengali, while substantially above baseline, do not yet reach the 0.95 threshold, indicating that additional training data or language-specific fine-tuning is required before deployment in Hindi- or Bengali-primary clinical settings.

### 5.3 Zero-Shot Transfer to Urdu

Urdu was withheld from all training data. The final XLM-RoBERTa model evaluated directly on Urdu symptom descriptions yields F1 of **0.814** — approaching Hindi performance (0.896) without any Urdu exposure. This result is structurally expected: Urdu and Hindi share a common spoken form (Hindustani), and romanized Urdu text has substantial subword overlap with romanized Hindi as tokenized by XLM-RoBERTa's SentencePiece vocabulary. The result confirms that the model has learned transferable clinical representations, not language-surface patterns.

### 5.4 Ablation: Two-Stage vs. One-Stage Fine-Tuning

| Fine-Tuning Strategy | English F1 | Bengali F1 | Avg F1 | CTEI |
|---|---|---|---|---|
| Single-stage (2×10⁻⁵ throughout) | 0.903 | 0.841 | 0.873 | 0.977 |
| **Two-stage (warm-up → full FT)** | **0.934** | **0.886** | **0.909** | **0.981** |

The two-stage procedure produces the largest gains in Bengali (+0.045) relative to English (+0.031), consistent with the hypothesis that warm-up preserves cross-lingual representations for lower-resource languages where early full fine-tuning risks catastrophic forgetting.

### 5.5 Ablation: Dataset Shortcut Suppression

This ablation documents the contribution of each design decision toward eliminating shortcut learning. The diagnostic signal for shortcut learning is validation F1 at epoch 1: a high value indicates the model has found a trivial rule rather than learning from context.

| Dataset Configuration | Val F1 @ Epoch 1 | Final Test F1 | Emergency Recall (EN) |
|---|---|---|---|
| Easy-only (100% prototypical) | **0.997** — leading-token shortcut | 0.841 | 0.887 |
| 80% hard, but with leading severity tokens | **0.961** — vocabulary-cluster shortcut | 0.891 | 0.921 |
| **80% hard + cross-vocab injection (ours)** | **0.831** — contextual learning | **0.909** | **0.958** |

The easy-only model achieves 0.997 F1 at epoch 1 by reading the first adjective ("Severe" → Emergency, "Mild" → Routine). Removing leading tokens drops epoch-1 F1 to 0.961 — better, but the model still exploits vocabulary clusters. Adding cross-vocabulary injection — Emergency instances with Routine language, Routine instances with Emergency language — breaks the cluster signal and forces contextual reasoning, dropping epoch-1 F1 to 0.831 while improving final test F1 from 0.891 to 0.909 and Emergency recall from 0.921 to 0.958.

The simultaneous improvement in final test F1 and Emergency recall confirms that the shortcut-suppression design is not merely making training harder — it is causing the model to learn genuinely better clinical representations.

---

## 6. Explainability Analysis

### 6.1 SHAP Token Attributions

We apply SHAP with a token-masking perturbation approach to generate per-token attribution scores. Attributions are computed on 200 held-out instances per language, stratified by class and difficulty tier (prototypical vs. adversarial).

**Cross-lingual SHAP alignment**: We compute Pearson correlation between attribution vectors for semantically equivalent tokens in parallel symptom descriptions across languages:

| Language Pair | Pearson r |
|---|---|
| English ↔ Spanish | 0.869 |
| English ↔ Hindi | 0.831 |
| English ↔ Bengali | 0.801 |

All three correlations exceed 0.80, indicating the model attends to the same clinical concepts regardless of language. Higher English-Spanish alignment reflects greater shared subword overlap in XLM-RoBERTa's vocabulary compared to English-Hindi or English-Bengali.

### 6.2 Attribution Behavior on Adversarial Emergency Instances

The most important explainability test is attribution behavior on cross-vocabulary Emergency instances — cases where the patient uses Routine register language but the situation is a true emergency. On these instances, SHAP attributions correctly identify the clinical danger signals embedded in context rather than surface language:

- For *"calling to refill metoprolol — mentioned face drooping since this morning"*: high attribution on `drooping`, `this morning`, `face` — not on `refill` or `metoprolol`
- For *"follow-up for blood pressure, feels fine today, but BP 265/145 and wants to leave"*: high attribution on `265/145`, `wants to leave` — not on `feels fine` or `follow-up`
- For *"mild pressure under breastbone, probably nothing — EKG shows ST elevation"*: high attribution on `ST elevation`, not on `mild` or `probably nothing`

This attribution pattern demonstrates clinical reasoning alignment: the model weighs objective clinical findings over subjective severity language, consistent with the clinical principle that patient-reported intensity does not reliably predict ESI tier, but objective findings do.

---

## 7. Methodological Lessons

We document four reproducible failure modes encountered during development. Each is presented with the diagnostic signal that reveals it and the specific fix that eliminates it. These lessons target researchers building synthetic clinical NLP datasets.

### Lesson 1: Split Before Augmenting

**Failure**: Applying text augmentation before splitting creates near-duplicate contamination. Augmented variants of training sentences appear in the validation set, producing validation F1 ≈ 1.000 within one epoch — not because the model has generalized, but because it has memorized near-identical copies.

**Diagnostic signal**: Val F1 exceeds 0.99 at epoch 1 *and* val loss is very close to 0 (< 0.01).

**Fix**: Split at the base-sentence level first. Apply augmentation exclusively to the training partition. The validation and test partitions contain only original base sentences.

**Rule**: Augmentation is a training-only operation.

### Lesson 2: Remove Leading Severity Tokens from Prototypical Templates

**Failure**: Synthetic templates co-locate severity adjectives at the sentence-leading position ("`Severe` chest pain…", "`Mild` cough…"). A model learns to read only the first word and classify accordingly. Validation F1 reaches 0.997 at epoch 1.

**Diagnostic signal**: Val F1 exceeds 0.97 at epoch 1 even on a small training set (< 2,000 instances).

**Fix**: Restructure all prototypical templates so that severity/quality descriptors do not appear in the first lexical slot. "Chest pain radiating to left arm — with sweating and nausea" rather than "Severe chest pain radiating to left arm."

**Rule**: The first content word of any template must not be a class-diagnostic modifier.

### Lesson 3: Inject Cross-Vocabulary Adversarial Instances

**Failure**: Even after removing leading tokens, models with sufficient capacity and training data learn vocabulary-cluster shortcuts — the statistical co-occurrence of clinical vocabulary with class labels across the full training distribution. Epoch-1 val F1 remains high (~0.96) because the model can identify class from aggregate word frequency without reading sentence context.

**Diagnostic signal**: Val F1 exceeds 0.90 at epoch 1 *despite* correct leading-token removal and ≥ 70% adversarial instances.

**Fix**: Add cross-vocabulary instances: Emergency class examples that use characteristic Routine-class language (refill calls where the patient discloses a stroke symptom; routine follow-up visits where the patient is found to be in crisis); Routine class examples that use characteristic Emergency-class language (chest pain that is musculoskeletal on exam; resolved panic attacks described with severe symptom language).

**Rule**: Each class in the training set must contain instances whose vocabulary distribution statistically resembles at least one other class. The model must read context to classify correctly.

### Lesson 4: Match Tokenizer to Model Encoder

**Failure**: XLM-RoBERTa uses SentencePiece (vocabulary size 250,002); mBERT uses WordPiece (vocabulary size 120,002). Instantiating mBERT with XLM-RoBERTa's tokenizer produces token IDs in the range [120,003 – 250,002] that fall outside mBERT's embedding matrix. PyTorch does not raise an error — it silently wraps or truncates the IDs, producing corrupted embeddings. Training loss appears to decrease normally, but test F1 is at or near random-chance levels (~0.33 for 3 classes).

**Diagnostic signal**: Test F1 approximately equals 1/n_classes despite normal-looking training curves.

**Fix**: Always load the tokenizer from the same checkpoint as the encoder: `AutoTokenizer.from_pretrained("bert-base-multilingual-cased")` for mBERT; `AutoTokenizer.from_pretrained("xlm-roberta-base")` for XLM-R.

**Rule**: `model_checkpoint == tokenizer_checkpoint`. Any deviation requires explicit cross-compatibility verification.

---

## 8. Discussion

### 8.1 Clinical Significance

MiST's primary clinical value is its Emergency recall in non-English languages. An LEP patient arriving at an emergency department and communicating in Spanish or Hindi currently encounters a triage system whose urgency assessment depends on language comprehension. The present standard — relying on ad hoc bilingual staff or delaying assessment until an interpreter is available — introduces delay at precisely the point where time determines outcomes in true emergencies (stroke: 4.5-hour thrombolysis window; MI: 90-minute door-to-balloon target; anaphylaxis: minutes to airway compromise).

MiST demonstrates that automated pre-triage screening using free-text symptom input in four languages is feasible at Emergency recall rates approaching clinical thresholds in English and Spanish. The framework is intended as a pre-triage screening layer, not a replacement for clinical judgment: it flags potential emergencies for immediate human attention regardless of the language in which they are presented.

The cross-vocabulary design ensures that the model's Emergency flagging behavior is robust to the most dangerous real-world presentation pattern — the patient who minimizes symptoms, uses non-clinical language, or describes an emergency situation in the register of a routine call.

### 8.2 Limitations

**Synthetic data**: MiST-12K is generated from templates rather than drawn from real patient records. Real patient language is noisier, more idiomatic, and exhibits vocabulary distributions that will differ from even the most carefully designed synthetic templates. Prospective validation on real patient-reported symptom text is required before any clinical deployment consideration.

**Romanized transliteration variance**: Hindi and Bengali instances use romanized forms without standardized orthography. Different romanization conventions not present in the training templates may reduce performance for real users.

**Language coverage**: MiST covers four languages. The approximately 350 languages spoken across the United States include many that would benefit from similar tooling, particularly for Southeast Asian and Pacific Islander populations who face documented healthcare disparities.

**Calibration**: We report classification performance but not probability calibration. Clinical decision support tools should produce well-calibrated confidence estimates. Calibration analysis is deferred to future work with real patient data.

**Emergency threshold**: English and Spanish approach the ≥ 0.95 Emergency recall threshold; Hindi and Bengali do not yet meet it. Deployment for Hindi- or Bengali-primary clinical populations requires additional work.

### 8.3 National Importance

This work addresses a documented national health priority: reducing healthcare disparities for immigrant and LEP populations, as identified in HHS Healthy People 2030 objectives and the AHRQ National Healthcare Quality and Disparities Report. The 25 million LEP individuals in the United States face measurably elevated clinical risk specifically during emergency triage — the highest-stakes clinical encounter. MiST is designed for integration with existing US hospital triage systems (Epic, Cerner) via standard NLP API endpoints, making deployment feasible without infrastructure change.

---

## 9. Conclusion

We presented MiST, a multilingual symptom triage framework addressing the healthcare disparity faced by limited English proficiency immigrants during emergency triage in the United States. The framework's core contribution is a two-tier adversarial dataset design — MiST-12K — that systematically eliminates two distinct shortcut learning failure modes through template restructuring and cross-vocabulary injection. This design produces a model that reads clinical context rather than pattern-matching on lexical surface features, which is the essential requirement for safe clinical deployment.

Two-stage XLM-RoBERTa fine-tuning achieves macro-averaged F1 of 0.909 across four languages, Emergency recall of 0.958 in English, and CTEI of 0.981 — meeting or approaching clinical deployment thresholds in English and Spanish. Zero-shot transfer to Urdu (F1 0.814) confirms that the model has learned language-invariant clinical representations. We document four methodological lessons — split before augmenting, remove leading severity tokens, inject cross-vocabulary instances, match tokenizer to encoder — as reproducible guidance for the synthetic clinical NLP community. Each lesson is accompanied by a diagnostic signal that reveals the failure mode and a specific fix that eliminates it.

---

## References

[1] Gilboy N, et al. *Emergency Severity Index (ESI): A Triage Tool for Emergency Department Care, Version 4.* AHRQ Publication No. 12-0014. 2012.

[2] US Census Bureau. *American Community Survey: Language Use in the United States, 2019.*

[3] Flores G. "The Impact of Medical Interpreter Services on the Quality of Healthcare: A Systematic Review." *Medical Care Research and Review* 62(3):255–299, 2005.

[4] Divi C, et al. "Language Proficiency and Adverse Events in US Hospitals: A Pilot Study." *International Journal for Quality in Health Care* 19(2):60–67, 2007.

[5] Devlin J, Chang MW, Lee K, Toutanova K. "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." *NAACL*, 2019.

[6] Conneau A, et al. "Unsupervised Cross-lingual Representation Learning at Scale." *ACL*, 2020.

[7] Alsentzer E, et al. "Publicly Available Clinical BERT Embeddings." *NAACL Clinical NLP Workshop*, 2019.

[8] Lee J, et al. "BioBERT: A Pre-trained Biomedical Language Representation Model for Biomedical Text Mining." *Bioinformatics* 36(4):1234–1240, 2020.

[9] Névéol A, et al. "Clinical NLP for Languages Other Than English: Opportunities and Challenges." *BioNLP Workshop*, 2018.

[10] Travers DA, et al. "Using Computer-assisted Text Analysis to Characterize Chief Complaints in an Emergency Department." *Academic Emergency Medicine* 11(11):1168–1175, 2004.

[11] Horng S, et al. "Creating an Automated Trigger for Sepsis Clinical Decision Support at Emergency Department Triage Using Machine Learning." *PLOS ONE* 12(4):e0174708, 2017.

[12] Levin S, et al. "Machine-Learning-Based Electronic Triage More Accurately Differentiates Patients With Respect to Clinical Outcomes Compared With the Emergency Severity Index." *Annals of Emergency Medicine* 71(5):565–574, 2018.

[13] Gururangan S, et al. "Annotation Artifacts in Natural Language Inference Data." *NAACL*, 2018.

[14] Kaushik D, Hovy E, Lipton Z. "Learning the Difference That Makes a Difference with Counterfactually-Augmented Data." *ICLR*, 2020.

[15] Jia R, Liang P. "Adversarial Examples for Evaluating Reading Comprehension Systems." *EMNLP*, 2017.

---

## Appendix A: Project Structure

```
MiST-Clinical-NLP/
├── MiST_Multilingual_Symptom_Triage.ipynb      # Training, evaluation, explainability
├── generate_dataset.py                          # Reproducible dataset generator
├── README.md                                    # This document
├── dataset/
│   ├── English.csv    (3,000 rows)
│   ├── Spanish.csv    (3,000 rows)
│   ├── Hindi.csv      (3,000 rows, Romanized)
│   └── Bengali.csv    (3,000 rows, Romanized)
└── checkpoints/
    ├── mbert/
    └── xlmr/
```

## Appendix B: Installation

```bash
pip install transformers datasets torch scikit-learn
pip install shap transformers-interpret
pip install seaborn matplotlib pandas numpy tqdm sentencepiece protobuf
```

Python 3.10+. GPU recommended (T4 or better). Expected runtime on T4: 50–70 minutes.

## Appendix C: Inference Example

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model     = AutoModelForSequenceClassification.from_pretrained("checkpoints/xlmr")
tokenizer = AutoTokenizer.from_pretrained("checkpoints/xlmr")
ID2LABEL  = {0: "Routine", 1: "Urgent", 2: "Emergency"}

def predict(text):
    enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        logits = model(**enc).logits
    return ID2LABEL[logits.argmax().item()]

# Cross-vocabulary Emergency: Routine language, true emergency
predict("Calling to refill metoprolol — mentioned face drooping since this morning")
# → Emergency

# Cross-vocabulary Routine: Emergency language, benign context
predict("Heart attack 5 years ago, stent placed, fully recovered, annual cardiac follow-up")
# → Routine

# Spanish — urgent
predict("Fiebre 39.8 con dolor de garganta tan fuerte que no puede tragar")
# → Urgent

# Hindi (Romanized) — emergency
predict("Seene ka dard baye haath tak failta hai, pasina aa raha hai")
# → Emergency

# Urdu — zero-shot (never seen during training)
predict("Seene mein shadeed dard baye bazoo tak phailta hai, paseena aur matli")
# → Emergency
```

## Appendix D: CTEI

```
CTEI = 1 − σ(F1_lang1, F1_lang2, ..., F1_langN) / μ(F1_lang1, ..., F1_langN)
```

| CTEI | Interpretation |
|---|---|
| 1.000 | Perfect equity — identical F1 across all languages |
| ≥ 0.950 | Minimum threshold for equitable clinical deployment |
| < 0.950 | Unacceptable performance gap — introduces new disparities |
| **0.981** | **MiST (XLM-R 2-stage) result** |

---

> **Clinical Disclaimer:** MiST is a research prototype intended as a decision support aid, not a replacement for clinical judgment. Emergency-tier outputs must trigger immediate review by qualified clinical personnel and must not serve as the sole basis for triage decisions. Prospective validation on real patient-reported symptom text is required before any deployment in healthcare settings.

> **Citation:**
> ```bibtex
> @article{rahman2025mist,
>   title   = {MiST: A Multilingual Symptom Triage Framework for Immigrant
>              Populations Using XLM-RoBERTa and Cross-Lingual Explainability},
>   author  = {Rahman, Azizur},
>   journal = {Journal of Biomedical Informatics},
>   year    = {2025},
>   note    = {Under review},
>   url     = {https://github.com/ayanchyaziz123/MiST-Clinical-NLP}
> }
> ```

> **License:** Dataset and code released under CC BY 4.0. Clinical deployment inquiries: azizurusa22@gmail.com
