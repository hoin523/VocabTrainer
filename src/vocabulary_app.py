import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from datetime import datetime
from .database import VocabularyDatabase

class VocabularyApp:
    def __init__(self):
        self.db = VocabularyDatabase()
        self.root = tk.Tk()
        self.root.title("Daily Vocabulary Learning Program")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize variables
        self.current_session_id = None
        self.current_words = []
        self.current_word_index = 0
        self.quiz_score = 0
        self.quiz_total = 0
        self.quiz_answers = []
        self.question_start_time = None
        
        # Seed the database with some initial vocabulary
        self.seed_vocabulary()
        
        # Create main interface
        self.create_main_interface()
        
    def seed_vocabulary(self):
        """Add initial vocabulary words if database is empty"""
        # Check if vocabulary exists
        words = self.db.get_daily_words(1)
        if not words:
            initial_words = [
                ("abundance", "A very large quantity of something", "There was an abundance of food at the party.", "uh-BUHN-duhns"),
                ("benevolent", "Well meaning and kindly", "The benevolent old man helped the lost child.", "buh-NEV-uh-luhnt"),
                ("candid", "Truthful and straightforward; frank", "She gave a candid assessment of the situation.", "KAN-did"),
                ("diligent", "Having or showing care and conscientiousness", "The diligent student completed all assignments.", "DIL-i-juhnt"),
                ("eloquent", "Fluent or persuasive in speaking or writing", "The eloquent speaker moved the audience.", "EL-uh-kwuhnt"),
                ("feasible", "Possible to do easily or conveniently", "The plan seems feasible given our resources.", "FEE-zuh-buhl"),
                ("gregarious", "Fond of the company of others; sociable", "She has a gregarious personality.", "gri-GAIR-ee-uhs"),
                ("hypothesis", "A supposition or proposed explanation", "The scientist tested her hypothesis carefully.", "hahy-POTH-uh-sis"),
                ("inevitable", "Certain to happen; unavoidable", "Change is inevitable in life.", "in-EV-i-tuh-buhl"),
                ("justify", "Show or prove to be right or reasonable", "Can you justify your decision?", "JUHS-tuh-fahy")
            ]
            
            for word_data in initial_words:
                self.db.add_vocabulary_word(*word_data)
    
    def create_main_interface(self):
        """Create the main application interface"""
        # Title
        title_label = tk.Label(self.root, text="Daily Vocabulary Learning", 
                              font=("Arial", 24, "bold"), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=20)
        
        # Stats frame
        self.stats_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.stats_frame.pack(pady=10)
        self.update_stats_display()
        
        # Main content frame
        self.content_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Navigation buttons
        nav_frame = tk.Frame(self.root, bg='#f0f0f0')
        nav_frame.pack(pady=20)
        
        self.learn_btn = tk.Button(nav_frame, text="Daily Learning", 
                                  command=self.start_daily_session,
                                  font=("Arial", 14), bg='#3498db', fg='white',
                                  padx=20, pady=10)
        self.learn_btn.pack(side='left', padx=10)
        
        self.review_btn = tk.Button(nav_frame, text="Review Words", 
                                   command=self.start_review_session,
                                   font=("Arial", 14), bg='#2ecc71', fg='white',
                                   padx=20, pady=10)
        self.review_btn.pack(side='left', padx=10)
        
        self.quiz_btn = tk.Button(nav_frame, text="Take Quiz", 
                                 command=self.start_quiz,
                                 font=("Arial", 14), bg='#e74c3c', fg='white',
                                 padx=20, pady=10)
        self.quiz_btn.pack(side='left', padx=10)
        
        self.manage_btn = tk.Button(nav_frame, text="Manage Words", 
                                   command=self.show_word_management,
                                   font=("Arial", 14), bg='#9b59b6', fg='white',
                                   padx=20, pady=10)
        self.manage_btn.pack(side='left', padx=10)
        
        # Show welcome screen initially
        self.show_welcome_screen()
    
    def update_stats_display(self):
        """Update the statistics display"""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        stats = self.db.get_user_stats()
        
        stats_text = f"Words Learned: {stats['total_words']} | " \
                    f"Mastered: {stats['mastered_words']} | " \
                    f"Avg Score: {stats['average_score']}% | " \
                    f"Recent Sessions: {stats['recent_sessions']}"
        
        stats_label = tk.Label(self.stats_frame, text=stats_text, 
                              font=("Arial", 12), bg='#f0f0f0', fg='#7f8c8d')
        stats_label.pack()
    
    def clear_content_frame(self):
        """Clear the main content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_welcome_screen(self):
        """Show the welcome screen"""
        self.clear_content_frame()
        
        welcome_label = tk.Label(self.content_frame, 
                                text="Welcome to Daily Vocabulary Learning!",
                                font=("Arial", 20), bg='#f0f0f0', fg='#2c3e50')
        welcome_label.pack(pady=50)
        
        desc_label = tk.Label(self.content_frame,
                             text="Choose an activity to improve your vocabulary:",
                             font=("Arial", 14), bg='#f0f0f0', fg='#34495e')
        desc_label.pack(pady=20)
        
        features_text = """
        📚 Daily Learning: Learn new words with definitions and examples
        🔄 Review Words: Practice previously learned vocabulary
        🎯 Take Quiz: Test your knowledge with multiple-choice questions
        """
        
        features_label = tk.Label(self.content_frame, text=features_text,
                                 font=("Arial", 12), bg='#f0f0f0', fg='#7f8c8d',
                                 justify='left')
        features_label.pack(pady=30)
    
    def start_daily_session(self):
        """Start a daily learning session"""
        self.current_session_id = self.db.create_daily_session()
        self.current_words = self.db.get_daily_words(5)
        
        if not self.current_words:
            messagebox.showinfo("Complete!", "Congratulations! You've learned all available words.")
            return
        
        self.current_word_index = 0
        self.show_word_learning()
    
    def show_word_learning(self):
        """Display word learning interface"""
        self.clear_content_frame()
        
        if self.current_word_index >= len(self.current_words):
            self.complete_learning_session()
            return
        
        word_data = self.current_words[self.current_word_index]
        
        # Progress indicator
        progress_text = f"Word {self.current_word_index + 1} of {len(self.current_words)}"
        progress_label = tk.Label(self.content_frame, text=progress_text,
                                 font=("Arial", 12), bg='#f0f0f0', fg='#7f8c8d')
        progress_label.pack(pady=10)
        
        # Word display
        word_frame = tk.Frame(self.content_frame, bg='#ecf0f1', relief='raised', bd=2)
        word_frame.pack(pady=20, padx=40, fill='x')
        
        word_label = tk.Label(word_frame, text=word_data['word'],
                             font=("Arial", 28, "bold"), bg='#ecf0f1', fg='#2c3e50')
        word_label.pack(pady=20)
        
        if word_data['pronunciation']:
            pron_label = tk.Label(word_frame, text=f"/{word_data['pronunciation']}/",
                                 font=("Arial", 14, "italic"), bg='#ecf0f1', fg='#7f8c8d')
            pron_label.pack(pady=5)
        
        def_label = tk.Label(word_frame, text=word_data['definition'],
                            font=("Arial", 16), bg='#ecf0f1', fg='#34495e',
                            wraplength=600)
        def_label.pack(pady=15)
        
        if word_data['example']:
            example_label = tk.Label(word_frame, text=f"Example: {word_data['example']}",
                                   font=("Arial", 14, "italic"), bg='#ecf0f1', fg='#7f8c8d',
                                   wraplength=600)
            example_label.pack(pady=10, padx=20)
        
        # Navigation buttons
        nav_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        nav_frame.pack(pady=30)
        
        if self.current_word_index > 0:
            prev_btn = tk.Button(nav_frame, text="Previous",
                                command=self.previous_word,
                                font=("Arial", 12), bg='#95a5a6', fg='white',
                                padx=20, pady=5)
            prev_btn.pack(side='left', padx=10)
        
        next_btn = tk.Button(nav_frame, text="Next" if self.current_word_index < len(self.current_words) - 1 else "Finish",
                            command=self.next_word,
                            font=("Arial", 12), bg='#3498db', fg='white',
                            padx=20, pady=5)
        next_btn.pack(side='right', padx=10)
    
    def previous_word(self):
        """Go to previous word"""
        if self.current_word_index > 0:
            self.current_word_index -= 1
            self.show_word_learning()
    
    def next_word(self):
        """Go to next word"""
        self.current_word_index += 1
        self.show_word_learning()
    
    def complete_learning_session(self):
        """Complete the learning session"""
        self.clear_content_frame()
        
        complete_label = tk.Label(self.content_frame,
                                 text="Learning Session Complete!",
                                 font=("Arial", 24, "bold"), bg='#f0f0f0', fg='#27ae60')
        complete_label.pack(pady=50)
        
        words_learned = len(self.current_words)
        summary_text = f"You've studied {words_learned} words today."
        summary_label = tk.Label(self.content_frame, text=summary_text,
                                font=("Arial", 16), bg='#f0f0f0', fg='#34495e')
        summary_label.pack(pady=20)
        
        # Update session in database
        if self.current_session_id:
            self.db.update_session_stats(self.current_session_id, words_learned, 0)
        
        quiz_btn = tk.Button(self.content_frame, text="Take Quiz on These Words",
                            command=self.start_session_quiz,
                            font=("Arial", 14), bg='#e74c3c', fg='white',
                            padx=20, pady=10)
        quiz_btn.pack(pady=20)
        
        home_btn = tk.Button(self.content_frame, text="Back to Home",
                            command=self.show_welcome_screen,
                            font=("Arial", 12), bg='#95a5a6', fg='white',
                            padx=20, pady=5)
        home_btn.pack(pady=10)
        
        self.update_stats_display()
    
    def start_review_session(self):
        """Start reviewing previously learned words"""
        review_words = self.db.get_review_words(10)
        
        if not review_words:
            messagebox.showinfo("No Words", "No words available for review yet. Learn some words first!")
            return
        
        self.current_words = review_words
        self.current_word_index = 0
        self.show_word_learning()
    
    def start_quiz(self):
        """Start a general quiz"""
        words = self.db.get_daily_words(10)
        if len(words) < 4:
            messagebox.showinfo("Not Enough Words", "You need at least 4 words to take a quiz. Learn more words first!")
            return
        
        self.start_quiz_with_words(words)
    
    def start_session_quiz(self):
        """Start quiz with current session words"""
        if len(self.current_words) < 4:
            messagebox.showinfo("Not Enough Words", "You need at least 4 words to take a quiz.")
            return
        
        self.start_quiz_with_words(self.current_words)
    
    def start_quiz_with_words(self, words):
        """Start quiz with specific word list"""
        self.quiz_words = words[:10]  # Limit to 10 questions
        self.quiz_score = 0
        self.quiz_total = 0
        self.quiz_answers = []
        self.current_quiz_index = 0
        self.show_quiz_question()
    
    def show_quiz_question(self):
        """Display a quiz question"""
        self.clear_content_frame()
        
        if self.current_quiz_index >= len(self.quiz_words):
            self.show_quiz_results()
            return
        
        word_data = self.quiz_words[self.current_quiz_index]
        self.question_start_time = time.time()  # Track response time
        
        # Progress
        progress_text = f"Question {self.current_quiz_index + 1} of {len(self.quiz_words)}"
        progress_label = tk.Label(self.content_frame, text=progress_text,
                                 font=("Arial", 12), bg='#f0f0f0', fg='#7f8c8d')
        progress_label.pack(pady=10)
        
        # Question
        question_text = f"What does '{word_data['word']}' mean?"
        question_label = tk.Label(self.content_frame, text=question_text,
                                 font=("Arial", 18, "bold"), bg='#f0f0f0', fg='#2c3e50')
        question_label.pack(pady=30)
        
        # Generate answer choices
        correct_answer = word_data['definition']
        wrong_answers = []
        
        # Get other definitions for wrong answers
        all_words = self.db.get_daily_words(20)
        for w in all_words:
            if w['id'] != word_data['id'] and len(wrong_answers) < 3:
                wrong_answers.append(w['definition'])
        
        # If not enough wrong answers, add generic ones
        while len(wrong_answers) < 3:
            generic_wrong = [
                "A type of musical instrument",
                "A cooking utensil",
                "A building material",
                "A weather phenomenon"
            ]
            for generic in generic_wrong:
                if generic not in wrong_answers and len(wrong_answers) < 3:
                    wrong_answers.append(generic)
        
        choices = [correct_answer] + wrong_answers[:3]
        random.shuffle(choices)
        
        self.quiz_var = tk.StringVar()
        self.correct_answer = correct_answer
        
        # Answer choices
        for i, choice in enumerate(choices):
            rb = tk.Radiobutton(self.content_frame, text=choice,
                               variable=self.quiz_var, value=choice,
                               font=("Arial", 14), bg='#f0f0f0',
                               wraplength=600, justify='left')
            rb.pack(pady=10, padx=40, anchor='w')
        
        # Submit button
        submit_btn = tk.Button(self.content_frame, text="Submit Answer",
                              command=self.submit_quiz_answer,
                              font=("Arial", 14), bg='#3498db', fg='white',
                              padx=20, pady=10)
        submit_btn.pack(pady=30)
    
    def submit_quiz_answer(self):
        """Submit and check quiz answer"""
        selected = self.quiz_var.get()
        if not selected:
            messagebox.showwarning("No Answer", "Please select an answer.")
            return
        
        is_correct = selected == self.correct_answer
        word_data = self.quiz_words[self.current_quiz_index]
        
        # Calculate response time
        response_time = time.time() - self.question_start_time if self.question_start_time else 0.0
        
        # Update database
        self.db.update_word_progress(word_data['id'], is_correct, response_time)
        
        # Track quiz progress
        self.quiz_total += 1
        if is_correct:
            self.quiz_score += 1
        
        self.quiz_answers.append({
            'word': word_data['word'],
            'correct': is_correct,
            'selected': selected,
            'correct_answer': self.correct_answer
        })
        
        # Show feedback
        feedback_text = "Correct!" if is_correct else f"Incorrect. The answer is: {self.correct_answer}"
        feedback_color = "#27ae60" if is_correct else "#e74c3c"
        
        feedback_label = tk.Label(self.content_frame, text=feedback_text,
                                 font=("Arial", 14, "bold"), bg='#f0f0f0', fg=feedback_color)
        feedback_label.pack(pady=20)
        
        # Next button
        next_btn = tk.Button(self.content_frame, text="Next Question",
                            command=self.next_quiz_question,
                            font=("Arial", 12), bg='#95a5a6', fg='white',
                            padx=20, pady=5)
        next_btn.pack(pady=10)
    
    def next_quiz_question(self):
        """Move to next quiz question"""
        self.current_quiz_index += 1
        self.show_quiz_question()
    
    def show_quiz_results(self):
        """Show quiz results"""
        self.clear_content_frame()
        
        score_percentage = (self.quiz_score / self.quiz_total * 100) if self.quiz_total > 0 else 0
        
        result_label = tk.Label(self.content_frame, text="Quiz Complete!",
                               font=("Arial", 24, "bold"), bg='#f0f0f0', fg='#2c3e50')
        result_label.pack(pady=30)
        
        score_text = f"Score: {self.quiz_score}/{self.quiz_total} ({score_percentage:.1f}%)"
        score_label = tk.Label(self.content_frame, text=score_text,
                              font=("Arial", 18), bg='#f0f0f0', fg='#34495e')
        score_label.pack(pady=20)
        
        # Update session if this was a session quiz
        if hasattr(self, 'current_session_id') and self.current_session_id:
            self.db.update_session_stats(self.current_session_id, len(self.current_words), score_percentage)
        
        # Performance feedback
        if score_percentage >= 80:
            feedback = "Excellent work! You're mastering these words."
            color = "#27ae60"
        elif score_percentage >= 60:
            feedback = "Good job! Keep practicing to improve."
            color = "#f39c12"
        else:
            feedback = "Keep studying. Review the words and try again."
            color = "#e74c3c"
        
        feedback_label = tk.Label(self.content_frame, text=feedback,
                                 font=("Arial", 14), bg='#f0f0f0', fg=color)
        feedback_label.pack(pady=15)
        
        # Action buttons
        button_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        button_frame.pack(pady=30)
        
        retry_btn = tk.Button(button_frame, text="Retake Quiz",
                             command=lambda: self.start_quiz_with_words(self.quiz_words),
                             font=("Arial", 12), bg='#e74c3c', fg='white',
                             padx=15, pady=5)
        retry_btn.pack(side='left', padx=10)
        
        home_btn = tk.Button(button_frame, text="Back to Home",
                            command=self.show_welcome_screen,
                            font=("Arial", 12), bg='#95a5a6', fg='white',
                            padx=15, pady=5)
        home_btn.pack(side='left', padx=10)
        
        self.update_stats_display()
    
    def show_word_management(self):
        """Show word management interface"""
        self.clear_content_frame()
        
        title_label = tk.Label(self.content_frame, text="Manage Vocabulary Words",
                              font=("Arial", 20, "bold"), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=20)
        
        # Add new word section
        add_frame = tk.LabelFrame(self.content_frame, text="Add New Word", 
                                 font=("Arial", 14), bg='#f0f0f0', fg='#2c3e50',
                                 padx=20, pady=15)
        add_frame.pack(fill='x', padx=20, pady=10)
        
        # Word input
        tk.Label(add_frame, text="Word:", font=("Arial", 12), bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        self.word_entry = tk.Entry(add_frame, font=("Arial", 12), width=30)
        self.word_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Definition input
        tk.Label(add_frame, text="Definition:", font=("Arial", 12), bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        self.def_entry = tk.Entry(add_frame, font=("Arial", 12), width=50)
        self.def_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Example input
        tk.Label(add_frame, text="Example:", font=("Arial", 12), bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=5)
        self.example_entry = tk.Entry(add_frame, font=("Arial", 12), width=50)
        self.example_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Pronunciation input
        tk.Label(add_frame, text="Pronunciation:", font=("Arial", 12), bg='#f0f0f0').grid(row=3, column=0, sticky='w', pady=5)
        self.pron_entry = tk.Entry(add_frame, font=("Arial", 12), width=30)
        self.pron_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Add button
        add_btn = tk.Button(add_frame, text="Add Word", command=self.add_new_word,
                           font=("Arial", 12), bg='#27ae60', fg='white',
                           padx=20, pady=5)
        add_btn.grid(row=4, column=1, pady=15, sticky='e')
        
        # Back button
        back_btn = tk.Button(self.content_frame, text="Back to Home",
                            command=self.show_welcome_screen,
                            font=("Arial", 12), bg='#95a5a6', fg='white',
                            padx=20, pady=5)
        back_btn.pack(pady=20)
    
    def add_new_word(self):
        """Add a new vocabulary word"""
        word = self.word_entry.get().strip()
        definition = self.def_entry.get().strip()
        example = self.example_entry.get().strip()
        pronunciation = self.pron_entry.get().strip()
        
        if not word or not definition:
            messagebox.showwarning("Missing Information", "Please provide at least a word and definition.")
            return
        
        result = self.db.add_vocabulary_word(word, definition, example, pronunciation)
        
        if result:
            messagebox.showinfo("Success", f"Added '{word}' to vocabulary!")
            # Clear entries
            self.word_entry.delete(0, tk.END)
            self.def_entry.delete(0, tk.END)
            self.example_entry.delete(0, tk.END)
            self.pron_entry.delete(0, tk.END)
            self.update_stats_display()
        else:
            messagebox.showwarning("Duplicate Word", f"'{word}' already exists in the vocabulary.")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = VocabularyApp()
    app.run()