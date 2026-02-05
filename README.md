# Keju: A Dynamic, Judge-Based Evaluation Framework for Language Models

**Keju** (科舉) is a novel evaluation framework designed to assess the **comprehensive reasoning and critical thinking abilities** of language models, moving beyond static benchmarks that are prone to overfitting.

Inspired by the historical Chinese imperial examination system, Keju employs a powerful "examiner" model to dynamically generate high-discrimination questions and grade the responses of the "candidate" model. This approach ensures that models are evaluated on their genuine, generalizable capabilities rather than their ability to memorize or game a fixed test set.

---

## Philosophy & Core Idea

Traditional benchmarks (like MMLU, GSM8K) are **static targets**. Once established, the research community inevitably optimizes for them, creating a gap between benchmark scores and true general intelligence.

Keju solves this by being **dynamic and adaptive**:
1.  **Dynamic Question Generation**: A strong "examiner" model creates fresh, complex, open-ended questions for each evaluation cycle.
2.  **Judge-Based Grading**: The same (or another) powerful model acts as a judge, evaluating the candidate's answer against a clear rubric.
3.  **Focus on Process, Not Just Facts**: Questions demand structured arguments (e.g., Define → Analyze → Evaluate), multi-step reasoning, and critical thought.

This makes it significantly harder to "cheat" and provides a more realistic assessment of a model's real-world utility.

---

## Keju Scoring System

Keju uses a simple, three-tiered scoring system inspired by the historical scholar ranks:

| Grade | Full Name          | Description                                                                                                                                 |
| :---- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| **J** | Junior Scholar     | Can grasp basic concepts and follow instructions but offers shallow, vague, or incomplete reasoning. Lacks depth and specific examples.      |
| **G** | Graduate Scholar   | Provides a complete and structured response covering main points. Reasoning is sound but may lack deep insight, nuanced analysis, or cross-domain integration. |
| **A** | Advanced Scholar   | Delivers a systematic, accurate, and insightful argument. Demonstrates multi-step logical reasoning, concrete evidence, and critical evaluation. |

---

## How It Works

The evaluation process for each cycle is straightforward:

1.  **Generate**: The examiner model creates a new, high-quality question.
2.  **Answer**: The candidate model provides its response.
3.  **Evaluate**: The examiner model grades the response as **J**, **G**, or **A**, along with a confidence score.
4.  **Aggregate**: After `N` cycles (e.g., 10), the results are aggregated. The most frequent grade becomes the model's **Overall Keju Rating**.

This design leverages the significant capability gap between top-tier proprietary models (the examiners) and open-source models up to 70B parameters (the candidates), providing a robust and fair assessment.

---

## Getting Started

### Prerequisites
- Python 3.8+
- Access to two LLM API endpoints:
    - A **strong model** (e.g., GPT-4, Claude 3 Opus, Qwen-Max) to act as the examiner.
    - The **model you want to evaluate** (the candidate).

### Installation
1.  Clone this repository.
    ```bash
    git clone https://github.com/your-username/keju.git
    cd keju
    ```
2.  Install the required dependencies.
    ```bash
    pip install openai
    ```

### Configuration
Edit the `Config` class in `main.py` to match your API settings:

```python
config = Config(
    # Examiner Model (Strong Model)
    strong_base_url="http://your-examiner-api-endpoint/v1",
    strong_api_key="your_examiner_api_key",
    strong_model_id="examiner-model-id", # e.g., "gpt-4o", "qwen-max"
    
    # Candidate Model (Weak Model to be Evaluated)
    weak_base_url="http://your-candidate-api-endpoint/v1",
    weak_api_key="your_candidate_api_key",
    weak_model_id="candidate-model-id", # e.g., "llama3-70b", "qwen-72b"
    
    num_cycles=10, # Number of evaluation rounds
    min_confidence_threshold=80 # Minimum confidence for a valid score
)
```

### Run the Evaluation
Simply execute the script:
```bash
python keju.py
```

The output will first display the raw data from all cycles and then provide a clear, summarized final report with the overall Keju rating.

---

## Why "Keju"?

The name "Keju" (科舉) is a direct reference to the Imperial Examination system of ancient China. Like its historical namesake, this framework aims to identify true intellectual merit through rigorous, dynamic, and fair assessment, rather than rote memorization or preparation for a known test.
