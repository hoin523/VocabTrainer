import tkinter as tk
import random
import requests
import json
import os
from tkinter import messagebox

# Lingvanex API 설정
API_KEY = "your_api_key"  # 실제 API 키 입력
API_URL = "https://api-b2b.backenster.com/b1/api/v3/translate"

# 영어 단어 목록
words = ['apple', 'banana', 'cherry', 'date', 'elderberry', 'grape', 'lemon']

# 캐시 파일 경로
CACHE_FILE = "translations.json"

# 번역 캐시 (메모리)
translation_cache = {}


# ======================
# JSON 캐시 불러오기
# ======================
def load_cache():
    global translation_cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            translation_cache = json.load(f)
        print(f"[CACHE LOAD] {len(translation_cache)}개 단어 불러옴")
    else:
        print("[CACHE] 캐시 파일 없음")


# ======================
# JSON 캐시 저장
# ======================
def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(translation_cache, f, ensure_ascii=False, indent=2)
    print(f"[CACHE SAVE] {len(translation_cache)}개 단어 저장 완료")


# ======================
# API 번역 함수
# ======================
def translate(text, source_lang="en", target_lang="ko"):
    # 캐시에 있으면 바로 반환
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
            translation_cache[text] = translation  # 캐시에 저장
            save_cache()
            return translation
        else:
            print("[WARNING] result 키 없음")
            return None
    except Exception as e:
        print(f"[ERROR] 번역 실패: {text}, 에러: {e}")
        return None


# ======================
# 프로그램 시작 시 전체 번역 (캐시 없을 때만)
# ======================
def preload_translations():
    for word in words:
        if word not in translation_cache:
            translation = translate(word)
            if not translation:
                translation_cache[word] = "(번역 실패)"
    save_cache()


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
    word, correct_answer = get_random_word_and_translation()
    if not word or not correct_answer:
        messagebox.showerror("오류", "단어 번역을 가져오지 못했습니다.")
        return

    # 삼지선다 보기 생성
    options = [correct_answer]
    while len(options) < 3:
        _, wrong_answer = get_random_word_and_translation()
        if wrong_answer and wrong_answer not in options:
            options.append(wrong_answer)
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
    if selected_answer == correct_answer:
        option_buttons[idx].config(bg="#b2fab4")  # 초록
    else:
        option_buttons[idx].config(bg="#fab2b2")  # 빨강
    root.after(800, update_ui)


# ======================
# Tkinter UI
# ======================
root = tk.Tk()
root.title("VocabTrainer")
root.geometry("650x450")
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


# ======================
# 실행
# ======================
load_cache()          # JSON 캐시 불러오기
preload_translations()  # 필요 시 번역 후 저장
update_ui()
root.mainloop()
