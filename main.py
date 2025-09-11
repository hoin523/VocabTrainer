import tkinter as tk
import random
import requests
import json
import os
from tkinter import messagebox

# ======================
# 설정
# ======================
API_KEY = "your_api_key"  # Lingvanex API 키
API_URL = "https://api-b2b.backenster.com/b1/api/v3/translate"

WORDS_FILE = "data/word_list.txt"         # 단어 파일
CACHE_FILE = "translations.json" # 번역 캐시

# ======================
# 단어 불러오기
# ======================
def load_words(filename=WORDS_FILE):
    if not os.path.exists(filename):
        print(f"[ERROR] {filename} 없음")
        return []
    with open(filename, "r", encoding="utf-8") as f:
        words_list = [line.strip() for line in f if line.strip()]
    print(f"[INFO] {len(words_list)}개 단어 불러옴")
    return words_list

words = load_words()

# ======================
# 캐시 로드/저장
# ======================
translation_cache = {}

def load_cache():
    global translation_cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            translation_cache = json.load(f)
        print(f"[CACHE LOAD] {len(translation_cache)}개 번역 로드")

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(translation_cache, f, ensure_ascii=False, indent=2)
    print(f"[CACHE SAVE] {len(translation_cache)}개 번역 저장")

# ======================
# 번역 함수
# ======================
def translate(text, source_lang="en", target_lang="ko"):
    if text in translation_cache:
        return translation_cache[text]

    payload = {
        "text": text,
        "from": source_lang,
        "to": target_lang,
        "platform": "api"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": API_KEY
    }
    try:
        print(f"[API REQUEST] 단어: {text}")
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        result = response.json()
        print(f"[API RESPONSE] {result}")

        if "result" in result and result["result"]:
            translation = result["result"]
            translation_cache[text] = translation
            save_cache()
            return translation
        else:
            print(f"[WARNING] 번역 실패: {text}")
            translation_cache[text] = "(번역 실패)"
            save_cache()
            return None
    except Exception as e:
        print(f"[ERROR] 번역 실패: {text}, 에러: {e}")
        translation_cache[text] = "(번역 실패)"
        save_cache()
        return None

# ======================
# 캐시 없는 단어 번역 미리 수행
# ======================
def preload_translations():
    for word in words:
        if word not in translation_cache:
            translate(word)

# ======================
# 결과 기록
# ======================
results = []  # [{'word': 'apple', 'selected': '사과', 'correct': True}, ...]

# ======================
# 무작위 단어 + 정답
# ======================
def get_random_word_and_translation():
    word = random.choice(words)
    translation = translation_cache.get(word, None)
    return word, translation

# ======================
# UI 업데이트
# ======================
def update_ui():
    global current_word

    # 번역 가능한 단어 찾기 (최대 20회 시도)
    attempts = 0
    while attempts < 20:
        word, correct_answer = get_random_word_and_translation()
        if word and correct_answer and correct_answer != "(번역 실패)":
            break
        attempts += 1
    else:
        # 20회 시도에도 없으면 그냥 표시
        word = "단어 없음"
        correct_answer = "???"

    current_word = word  # 결과 기록용

    # 삼지선다 보기 생성
    options = [correct_answer]
    attempts2 = 0
    while len(options) < 3 and attempts2 < 20:
        _, wrong_answer = get_random_word_and_translation()
        if wrong_answer and wrong_answer not in options and wrong_answer != "(번역 실패)":
            options.append(wrong_answer)
        attempts2 += 1

    while len(options) < 3:
        options.append("???")  # 임시 텍스트

    random.shuffle(options)

    # 화면 갱신
    word_label.config(text=word)
    for i, btn in enumerate(option_buttons):
        btn.config(text=options[i], bg="#ffffff", fg="#333333")
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#d0e1ff"))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#ffffff"))
        btn.config(command=lambda i=i: check_answer(i, options[i], correct_answer))


# ======================
# 정답 확인
# ======================
def check_answer(idx, selected_answer, correct_answer):
    correct = selected_answer == correct_answer
    results.append({'word': current_word, 'selected': selected_answer, 'correct': correct})

    if correct:
        option_buttons[idx].config(bg="#b2fab4")  # 초록
    else:
        option_buttons[idx].config(bg="#fab2b2")  # 빨강
    root.after(800, update_ui)

# ======================
# 결과 보기
# ======================
def show_results():
    if not results:
        messagebox.showinfo("결과", "아직 푼 문제가 없습니다.")
        return
    correct_count = sum(r['correct'] for r in results)
    total = len(results)
    summary = f"총 {total}문제 중 {correct_count}개 정답\n\n"
    for r in results:
        summary += f"{r['word']}: 선택='{r['selected']}' 정답={'O' if r['correct'] else 'X'}\n"
    messagebox.showinfo("결과", summary)

# ======================
# Tkinter UI
# ======================
root = tk.Tk()
root.title("VocabTrainer")
root.geometry("650x500")
root.configure(bg="#f0f4f8")

word_label = tk.Label(root, text="", font=("Helvetica", 36, "bold"),
                      bg="#f0f4f8", fg="#1a1a1a")
word_label.pack(pady=(40, 20))

option_buttons = []
for _ in range(3):
    btn = tk.Button(root, text="", font=("Helvetica", 16, "bold"), width=50, height=2,
                    bg="#ffffff", fg="#333333", relief="raised", bd=5)
    btn.pack(pady=10, padx=20)
    option_buttons.append(btn)

# 결과 보기 버튼
result_btn = tk.Button(root, text="결과 보기", font=("Helvetica", 14, "bold"),
                       bg="#f5f5f5", fg="#333333", relief="raised", bd=3,
                       command=show_results)
result_btn.pack(pady=10)

# ======================
# 실행
# ======================
load_cache()          # 캐시 로드
preload_translations()  # 캐시 없는 단어 번역 수행
update_ui()
root.mainloop()
