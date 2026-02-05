import time
from collections import Counter
from dataclasses import dataclass
from typing import Optional
from openai import OpenAI

@dataclass
class Config:
    # 強模型（考官）設定
    strong_base_url: str = "http://127.0.0.1:4000/v1"
    strong_api_key: str = "sk-company-1234"
    strong_model_id: str = "gpt-oss-120b"
    
    # 弱模型（考生）設定
    weak_base_url: str = "http://127.0.0.1:4001/v1"
    weak_api_key: str = "sk-no-key-required"
    weak_model_id: str = "your_weak_model_name_or_id"
    
    # 執行次數
    num_cycles: int = 10
    
    # 最低信心程度要求
    min_confidence_threshold: int = 80

def create_clients(config: Config):
    """根據配置創建API客戶端"""
    strong_client = OpenAI(base_url=config.strong_base_url, api_key=config.strong_api_key)
    weak_client = OpenAI(base_url=config.weak_base_url, api_key=config.weak_api_key)
    return strong_client, weak_client

def generate_question(client, model_id: str):
    """強模型（考官）生成 Keju 問題"""
    prompt = """你是一位嚴謹的 Keju 考官。請生成一個高鑑別度的開放式問題，用於評估語言模型的綜合能力。問題需同時滿足以下條件：

1. **主題範圍**：涵蓋科學、技術、數學、哲學、歷史或跨領域議題。
2. **認知深度**：
   - 需要至少兩步以上的邏輯推理（multi-step reasoning）
   - 涉及概念解釋、因果分析、或假設性推演
   - 鼓勵批判性思考，而非單純事實回憶
3. **結構要求**：問題應明確要求回答者提供清晰的論證結構（例如：先定義、再分析、最後評估）。
4. **難度梯度**：
   - J (Junior Scholar) 級別的模型可能只能給出模糊或片面答案
   - G (Graduate Scholar) 級別的模型可能能覆蓋主要觀點但缺乏深度
   - A (Advanced Scholar) 級別的模型應能展現系統性、準確且具洞察力的回答

請確保問題表述清晰、無歧義、且不依賴外部圖表或未提供資訊。
"""
    
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.9 # 增加多樣性
    )
    question = response.choices[0].message.content.strip()
    return question

def get_weak_answer(client, question: str, model_id: str):
    """弱模型（考生）回答 Keju 問題"""
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": question}],
        max_tokens=2000,
        temperature=0.3
    )
    answer = response.choices[0].message.content.strip()
    return answer

def evaluate_answer(client, question: str, answer: str, model_id: str):
    """強模型（考官）根據 Keju 標準評估答案"""
    evaluation_prompt = f"""
你是一位公正且嚴格的 Keju 考官。請評估以下對問題的回答。

問題：
{question}

回答：
{answer}

請根據回答的準確性、完整性、相關性和邏輯性進行評分。
評分標準（Keju 三級制）：
- **J (Junior Scholar)**: 回答非常簡短、基本，可能包含錯誤或僅有表面陳述，缺乏推理和細節。
- **G (Graduate Scholar)**: 回答較為完整、結構清晰，能覆蓋主要觀點，但缺乏深度、具體例證或批判性洞見。
- **A (Advanced Scholar)**: 回答非常詳細、深入且高度準確，展現系統性、多步驟推理和批判性思考。

請提供一個最符合的回答等級（J, G, or A）。
同時，請給出你評分的信心程度百分比（0-100），確保這個信心程度至少為80%。
請按照以下格式回覆：
Keju Rating: <J/G/A>
Confidence: % (請確保此值 >= 80)
Comment: <簡短說明評分原因>
"""

    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": evaluation_prompt}],
        max_tokens=5000,
        temperature=0.2
    )
    evaluation_result = response.choices[0].message.content.strip()

    # 解析結果
    lines = evaluation_result.split('\n')
    keju_rating = None
    confidence = 0

    for line in lines:
        if "Keju Rating:" in line:
            rating_part = line.split("Keju Rating:")[1].strip()
            if rating_part in ["J", "G", "A"]:
                keju_rating = rating_part
        elif "Confidence:" in line:
            try:
                conf_part = line.split("Confidence:")[1].split('%')[0].strip()
                confidence = int(conf_part)
            except (IndexError, ValueError):
                print("無法解析信心程度。")
    return keju_rating, confidence, evaluation_result

def run_evaluation_cycle(strong_client, weak_client, config: Config):
    """執行單一 Keju 評分循環：出題 -> 回答 -> 評分"""
    print(f"--- Generating New Keju Question ---")
    question = generate_question(strong_client, config.strong_model_id)
    print(f"Generated Question:\n{question}\n")
    
    print(f"--- Getting Weak Model Answer ---")
    answer = get_weak_answer(weak_client, question, config.weak_model_id)
    print(f"Weak Model Answer:\n{answer}\n")
    
    print(f"--- Evaluating Answer (Keju Standard) ---")
    rating, confidence, eval_text = evaluate_answer(strong_client, question, answer, config.strong_model_id)
    print(f"Evaluation Result:\n{eval_text}\n")
    
    if confidence < config.min_confidence_threshold:
        print(f"警告：信心程度 {confidence}% 低於 {config.min_confidence_threshold}% 的要求。\n")
        
    return question, answer, rating, confidence

def main():
    config = Config(
        strong_base_url="http://127.0.0.1:4000/v1",
        strong_api_key="sk-company-1234",
        strong_model_id="gpt-oss-120b",
        weak_base_url="http://127.0.0.1:4001/v1",
        weak_api_key="sk-no-key-required",
        weak_model_id="your_weak_model_name_or_id",
        num_cycles=10,
        min_confidence_threshold=80
    )
    
    strong_client, weak_client = create_clients(config)

    all_ratings = []
    valid_ratings = []
    all_data = []

    for i in range(config.num_cycles):
        print(f"--- Cycle {i+1}/{config.num_cycles} ---")
        question, answer, rating, confidence = run_evaluation_cycle(strong_client, weak_client, config)
        
        all_data.append({
            "question": question,
            "answer": answer,
            "rating": rating,
            "confidence": confidence
        })
        
        if confidence >= config.min_confidence_threshold and rating is not None:
            all_ratings.append(rating)
            valid_ratings.append(rating)
            print(f"有效評分 ({confidence}%): {rating}\n")
        else:
            all_ratings.append(None)
            print(f"跳過此評分 (信心程度不足或無效評等)\n")
            
        time.sleep(1)

    # === 列出 Raw Data ===
    print("\n" + "="*50)
    print("=== Keju Evaluation: Raw Data ===")
    print("="*50)
    print(f"All collected ratings (including skipped): {all_ratings}")
    print(f"Valid ratings (confidence >= {config.min_confidence_threshold}%): {valid_ratings}")

    if not valid_ratings:
        print(f"\n沒有任何信心程度大於或等於{config.min_confidence_threshold}%的有效評分。")
        return

    # === 整理總結 ===
    print("\n" + "="*50)
    print("=== Keju Evaluation: Final Summary ===")
    print("="*50)
    
    rating_counts = Counter(valid_ratings)
    result_parts = []
    for grade in ["J", "G", "A"]:
        count = rating_counts.get(grade, 0)
        # 將等級映射為全名以便閱讀
        full_name = {"J": "Junior Scholar", "G": "Graduate Scholar", "A": "Advanced Scholar"}[grade]
        result_parts.append(f"{grade} ({full_name}) = {count}")
    
    final_result_line = ", ".join(result_parts)
    print(f"Keju Score Distribution:\n{final_result_line}\n")
    
    # 找出出現最多的等級
    if rating_counts:
        most_common_rating, frequency = rating_counts.most_common(1)[0]
        full_name = {"J": "Junior Scholar", "G": "Graduate Scholar", "A": "Advanced Scholar"}[most_common_rating]
        print(f"Overall Keju Rating: {most_common_rating} ({full_name}) [Frequency: {frequency}]")
    
    # 打印所有循環的摘要
    print("\n--- All Cycles Summary ---")
    for idx, data in enumerate(all_data):
        status = "有效" if data["confidence"] >= config.min_confidence_threshold and data["rating"] is not None else "無效"
        print(f"{idx+1}. 問題: {data['question'][:50]}... | 評等: {data['rating']} | 信心度: {data['confidence']}% | 狀態: {status}")


if __name__ == "__main__":
    main()