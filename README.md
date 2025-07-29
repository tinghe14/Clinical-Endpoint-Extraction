# 🧬 Tumor Measurement Extraction via Instruction-Tuned LLMs
This project implements an end-to-end clinical NLP pipeline to extract tumor size and other measurement-related endpoints from oncology pathology reports. It benchmarks rule-based approaches against instruction-tuned large language models (LLaMA) fine-tuned via QLoRA.

## Project Highlights
1. Pipeline: End-to-end system from raw pathology report → preprocessing → rule-based extraction → LLM extraction → evaluation.
2. Rule-Based Baseline: Designed regex and pattern-matching extractors for tumor size, which exclude  depth of invasion, and metastatic focus size.
3. Instruction-Tuned Model: Used QLoRA and PyTorch to instruction-tune LLaMA on a labeled corpus of clinical measurement examples.

## Tech Stack
- Python, PyTorch, HuggingFace Transformers, QLoRA
- spaCy for preprocessing and NER scaffolding
- Pandas, Scikit-learn for evaluation

## Example Input / Output
- Input (pathology report):
"The tumor measured 3.2 cm in greatest dimension. Depth of invasion: 1.1 cm. Metastatic focus: 0.4 cm."
- Output: 3.2 cm

## Repo Structure

1. Preprocessing:
2. Modeling:
	- Apply rule-based regex system
	- Apply BERT model
	- Apply instruct-tuning LLM models
3. Evaluation

├── data/
│   ├── raw_reports/
│   └── annotations/
├── models/
│   ├── llama_finetune/
│   └── rule_based/
├── scripts/
│   ├── preprocess.py
│   ├── extract_rule.py
│   └── finetune_llama.py
├── evaluation/
│   └── evaluate_results.py
├── README.md

## How to Run
1. Fine-tune LLaMA using QLoRA
python scripts/finetune_llama.py --train data/train.json --output_dir models/llama_finetune
2. Run extraction using fine-tuned model
python scripts/extract_llama.py --input data/test.json --model_dir models/llama_finetune
3. Evaluate performance
python evaluation/evaluate_results.py --pred results.json --gold data/test_labels.json
