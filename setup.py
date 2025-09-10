import os

# 프로젝트 폴더
PROJECT_NAME = "VocabTrainer"
DATA_DIR = os.path.join(PROJECT_NAME, "data")

# 파일 내용
files = {
    os.path.join(PROJECT_NAME, "main.py"): '''import tkinter as tk
from tkinter import messagebox
from vocab_api import get_meaning
from quiz_manager import get_random_word, update_stats, load_stats

current_word = ""

def new_quiz():
    global current_word
    current_word = get_random_word()
    word_label.config(text=current_word)
    answer_entry.delete(0, tk.END)

def check_answer():
    user_ans = answer_entry.get().strip()
    correct_meaning = get_meaning(current_word)
    if not correct_meaning:
        messagebox.showwarning("알림", f"{current_word} 단어 뜻을 찾을 수 없습니다.")
        new_quiz()
        return
    if user_ans.lower() == correct_meaning.lower():
        messagebox.showinfo("정답", "정답입니다!")
        update_stats(current_word, True)
    else:
        messagebox.showerror("틀림", f"틀렸습니다!\\n정답: {correct_meaning}")
        update_stats(current_word, False)
    new_quiz()

def show_stats():
    stats = load_stats()
    text = "\\n".join([f"{w}: 맞춤 {r['correct']} / 틀림 {r['wrong']}" for w, r in stats.items()])
    messagebox.showinfo("학습 기록", text if text else "기록이 없습니다.")

# GUI 설정
root = tk.Tk()
root.title("VocabTrainer")

word_label = tk.Label(root, text="", font=("Arial", 24))
word_label.pack(pady=20)

answer_entry = tk.Entry(root, font=("Arial", 18))
answer_entry.pack(pady=10)

check_btn = tk.Button(root, text="제출", font=("Arial", 14), command=check_answer)
check_btn.pack(pady=5)

stats_btn = tk.Button(root, text="학습 기록 보기", font=("Arial", 14), command=show_stats)
stats_btn.pack(pady=5)

new_quiz()
root.mainloop()
''',

    os.path.join(PROJECT_NAME, "vocab_api.py"): '''import requests

def get_meaning(word):
    """Free Dictionary API에서 단어 뜻 가져오기"""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            meaning = data[0]['meanings'][0]['definitions'][0]['definition']
            return meaning
        except (IndexError, KeyError):
            return None
    return None
''',

    os.path.join(PROJECT_NAME, "quiz_manager.py"): '''import json
import random
import os

DATA_DIR = "data"
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
WORD_LIST_FILE = os.path.join(DATA_DIR, "word_list.txt")

# stats.json 초기화
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(STATS_FILE):
    stats = {}
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

# 로컬 단어 리스트 불러오기
with open(WORD_LIST_FILE, 'r', encoding='utf-8') as f:
    words = [line.strip() for line in f if line.strip()]

def get_random_word():
    return random.choice(words)

def load_stats():
    with open(STATS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_stats(stats):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def update_stats(word, correct):
    stats = load_stats()
    if word not in stats:
        stats[word] = {"correct": 0, "wrong": 0}
    if correct:
        stats[word]["correct"] += 1
    else:
        stats[word]["wrong"] += 1
    save_stats(stats)
''',

    os.path.join(DATA_DIR, "word_list.txt"): '''apple
banana
cat
dog
book
computer
keyboard
mouse
phone
tree
''',

    os.path.join(DATA_DIR, "stats.json"): '{}',

    os.path.join(PROJECT_NAME, "requirements.txt"): 'requests\n'
}

# 폴더 및 파일 생성
os.makedirs(DATA_DIR, exist_ok=True)
for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"{PROJECT_NAME} 프로젝트 구조가 생성되었습니다.")
