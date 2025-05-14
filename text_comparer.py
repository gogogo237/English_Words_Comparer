import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import string # For string.punctuation

class TextComparerApp:
    def __init__(self, master):
        self.master = master
        master.title("Text Difference Finder")
        master.geometry("700x600") # Increased height a bit for the new button

        self.bilingual_file_path = tk.StringVar()
        self.english_file_path = tk.StringVar()

        # --- File Selection Frame ---
        file_frame = tk.Frame(master, pady=10)
        file_frame.pack(fill=tk.X)

        tk.Button(file_frame, text="Select Bilingual Text File (.txt)", command=self._select_bilingual_file).pack(side=tk.LEFT, padx=5)
        self.bilingual_label = tk.Label(file_frame, text="No bilingual file selected")
        self.bilingual_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        file_frame2 = tk.Frame(master, pady=5)
        file_frame2.pack(fill=tk.X)

        tk.Button(file_frame2, text="Select English Text File (.txt)", command=self._select_english_file).pack(side=tk.LEFT, padx=5)
        self.english_label = tk.Label(file_frame2, text="No English file selected")
        self.english_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- Action Buttons Frame ---
        action_frame = tk.Frame(master, pady=5)
        action_frame.pack()

        tk.Button(action_frame, text="Compare English Words", command=self._compare_texts, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Compare Punctuation", command=self._compare_punctuation, pady=5).pack(side=tk.LEFT, padx=5)


        # --- Results Display ---
        tk.Label(master, text="Comparison Results:").pack()
        self.results_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=20, width=80)
        self.results_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def _preload_file_paths(self):
        bilingual_default = "BilingualText.txt"
        english_default = "EnglishText.txt"

        if os.path.exists(bilingual_default):
            self.bilingual_file_path.set(os.path.abspath(bilingual_default))
            self.bilingual_label.config(text=f"Bilingual: {os.path.basename(bilingual_default)}")
        if os.path.exists(english_default):
            self.english_file_path.set(os.path.abspath(english_default))
            self.english_label.config(text=f"English: {os.path.basename(english_default)}")

    def _select_bilingual_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Bilingual Text File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filepath:
            self.bilingual_file_path.set(filepath)
            self.bilingual_label.config(text=f"Bilingual: {os.path.basename(filepath)}")
        else:
            self.bilingual_file_path.set("")
            self.bilingual_label.config(text="No bilingual file selected")

    def _select_english_file(self):
        filepath = filedialog.askopenfilename(
            title="Select English Text File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filepath:
            self.english_file_path.set(filepath)
            self.english_label.config(text=f"English: {os.path.basename(filepath)}")
        else:
            self.english_file_path.set("")
            self.english_label.config(text="No English file selected")

    def _extract_english_from_bilingual(self, filepath):
        english_lines_extracted = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                content_lines = [line.rstrip('\n') for line in all_lines if line.strip()] # Keep original line endings for now
                for i in range(0, len(content_lines), 2):
                    english_lines_extracted.append(content_lines[i])
            return "\n".join(english_lines_extracted) # Join with \n to preserve line structure for punctuation analysis
        except Exception as e:
            messagebox.showerror("Error Reading Bilingual File", f"Could not read or parse bilingual file: {e}")
            return None

    def _read_english_text(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            messagebox.showerror("Error Reading English File", f"Could not read English file: {e}")
            return None

    def _tokenize_and_clean_text(self, text):
        if not text:
            return []
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        text_no_punct_attached = text.translate(translator)
        words = text_no_punct_attached.split()
        return words

    def _extract_punctuation_with_location(self, text, text_source_name="Unknown"):
        """
        Extracts all punctuation marks from the text with their line and char positions.
        Returns a list of tuples: (punctuation_char, line_number, char_pos_in_line)
        Line and char positions are 1-based.
        """
        if not text:
            return []

        punctuation_marks = []
        lines = text.splitlines() # Preserves line structure
        for line_idx, line_content in enumerate(lines):
            for char_idx, char in enumerate(line_content):
                if char in string.punctuation:
                    punctuation_marks.append((char, line_idx + 1, char_idx + 1))
        return punctuation_marks

    def _compare_texts(self):
        self.results_text.delete('1.0', tk.END)

        bilingual_path = self.bilingual_file_path.get()
        english_path = self.english_file_path.get()

        if not bilingual_path or not english_path:
            messagebox.showwarning("Input Missing", "Please select both text files.")
            return

        # For word comparison, we still join with spaces after extraction to make it one sequence
        extracted_bilingual_eng_raw_lines = self._extract_english_from_bilingual(bilingual_path)
        if extracted_bilingual_eng_raw_lines is None: return
        extracted_bilingual_eng_for_words = extracted_bilingual_eng_raw_lines.replace('\n', ' ')


        pure_english_text_raw = self._read_english_text(english_path)
        if pure_english_text_raw is None: return
        pure_english_text_for_words = pure_english_text_raw.replace('\n', ' ')


        bilingual_words = self._tokenize_and_clean_text(extracted_bilingual_eng_for_words)
        english_words = self._tokenize_and_clean_text(pure_english_text_for_words)

        if not bilingual_words and not english_words:
            self.results_text.insert(tk.END, "Both texts are empty or contain no valid words after cleaning punctuation.\n")
            return
        if not bilingual_words:
            self.results_text.insert(tk.END, "Extracted English from BilingualText is empty or has no valid words after cleaning punctuation.\n")
            if english_words:
                self.results_text.insert(tk.END, f"EnglishText.txt contains {len(english_words)} words after cleaning punctuation.\n")
            return
        if not english_words:
            self.results_text.insert(tk.END, "EnglishText.txt is empty or has no valid words after cleaning punctuation.\n")
            if bilingual_words:
                 self.results_text.insert(tk.END, f"Bilingual extract contains {len(bilingual_words)} words after cleaning punctuation.\n")
            return

        differences_found = False
        max_len = max(len(bilingual_words), len(english_words))

        for i in range(max_len):
            word_b = bilingual_words[i] if i < len(bilingual_words) else "<END_OF_BILINGUAL_EXTRACT>"
            word_e = english_words[i] if i < len(english_words) else "<END_OF_ENGLISHTEXT>"

            if word_b.lower() != word_e.lower(): # Case-insensitive comparison for words
                differences_found = True
                self.results_text.insert(tk.END, f"Difference at word index {i}:\n")
                self.results_text.insert(tk.END, f"  Bilingual Extracted: '{word_b}'\n")
                self.results_text.insert(tk.END, f"  EnglishText.txt:     '{word_e}'\n\n")

        if not differences_found:
            self.results_text.insert(tk.END, "No differences found between the English words (case-insensitive, after cleaning punctuation).\n")
        
        if len(bilingual_words) != len(english_words):
                self.results_text.insert(tk.END, f"(Note: Cleaned word counts differ - Bilingual Extract: {len(bilingual_words)}, EnglishText: {len(english_words)})\n")
        else:
            if not differences_found:
                 self.results_text.insert(tk.END, f"(Cleaned word counts match: {len(bilingual_words)})\n")

    def _compare_punctuation(self):
        self.results_text.delete('1.0', tk.END)

        bilingual_path = self.bilingual_file_path.get()
        english_path = self.english_file_path.get()

        if not bilingual_path or not english_path:
            messagebox.showwarning("Input Missing", "Please select both text files.")
            return

        # Get raw English content (with newlines preserved from extraction for bilingual)
        extracted_bilingual_eng_raw = self._extract_english_from_bilingual(bilingual_path)
        if extracted_bilingual_eng_raw is None: return

        pure_english_text_raw = self._read_english_text(english_path)
        if pure_english_text_raw is None: return

        # Extract punctuation sequences with locations
        puncts_bilingual = self._extract_punctuation_with_location(extracted_bilingual_eng_raw, "Bilingual Extract")
        puncts_english = self._extract_punctuation_with_location(pure_english_text_raw, "EnglishText.txt")

        if not puncts_bilingual and not puncts_english:
            self.results_text.insert(tk.END, "No punctuation found in either text.\n")
            return

        self.results_text.insert(tk.END, "Punctuation Comparison:\n\n")
        differences_found = False
        max_len = max(len(puncts_bilingual), len(puncts_english))

        for i in range(max_len):
            p_b_char, p_b_line, p_b_col = (None, None, None)
            p_e_char, p_e_line, p_e_col = (None, None, None)
            diff_type = ""

            if i < len(puncts_bilingual):
                p_b_char, p_b_line, p_b_col = puncts_bilingual[i]
            else:
                diff_type = "EnglishText has fewer punctuation marks."

            if i < len(puncts_english):
                p_e_char, p_e_line, p_e_col = puncts_english[i]
            else:
                diff_type = "Bilingual Extract has fewer punctuation marks."

            if p_b_char is not None and p_e_char is not None:
                if p_b_char != p_e_char:
                    diff_type = "Punctuation characters differ."
                # Optional: Could also check if p_b_line != p_e_line or p_b_col != p_e_col
                # and report as "Same punctuation, different location" if chars are same.
                # For now, focusing on differing characters or missing ones.
            
            if diff_type: # If there's any kind of mismatch (char, or one is missing)
                differences_found = True
                self.results_text.insert(tk.END, f"Difference in punctuation sequence at occurrence #{i+1}:\n")
                if p_b_char is not None:
                    self.results_text.insert(tk.END, f"  Bilingual Extract: '{p_b_char}' (Line {p_b_line}, Char {p_b_col})\n")
                else:
                    self.results_text.insert(tk.END, f"  Bilingual Extract: <NO PUNCTUATION AT THIS POSITION>\n")

                if p_e_char is not None:
                    self.results_text.insert(tk.END, f"  EnglishText.txt:     '{p_e_char}' (Line {p_e_line}, Char {p_e_col})\n")
                else:
                    self.results_text.insert(tk.END, f"  EnglishText.txt:     <NO PUNCTUATION AT THIS POSITION>\n")
                self.results_text.insert(tk.END, f"  Reason: {diff_type}\n\n")


        if not differences_found:
            self.results_text.insert(tk.END, "No differences found in the sequence of punctuation marks.\n")

        if len(puncts_bilingual) != len(puncts_english):
            self.results_text.insert(tk.END, f"(Note: Punctuation counts differ - Bilingual Extract: {len(puncts_bilingual)}, EnglishText: {len(puncts_english)})\n")
        elif not differences_found: # only if counts match and no diffs
             self.results_text.insert(tk.END, f"(Punctuation counts match: {len(puncts_bilingual)})\n")


if __name__ == "__main__":
    # Create dummy files for testing
    bilingual_test_content = """Hello, world!
中文
This is a test?
中文
How are you;
"""
    # EnglishText.txt will have different punctuation
    english_test_content = """Hello world.
This is a test!
How are you: I am fine.
"""
    # Expected Punctuation (Bilingual Extracted):
    # Line 1: Hello, world! -> (',', 1, 6), ('!', 1, 12)
    # Line 2: This is a test? -> ('?', 2, 16)
    # Line 3: How are you; -> (';', 3, 12)
    # Bilingual Puncts: [ (',',1,6), ('!',1,12), ('?',2,16), (';',3,12) ]

    # Expected Punctuation (EnglishText.txt):
    # Line 1: Hello world. -> ('.', 1, 12)
    # Line 2: This is a test! -> ('!', 2, 16)
    # Line 3: How are you: I am fine. -> (':', 3, 12), ('.', 3, 23)
    # English Puncts: [ ('.',1,12), ('!',2,16), (':',3,12), ('.',3,23) ]

    if not os.path.exists("BilingualText.txt"):
        with open("BilingualText.txt", "w", encoding="utf-8") as f:
            f.write(bilingual_test_content)

    if not os.path.exists("EnglishText.txt"):
        with open("EnglishText.txt", "w", encoding="utf-8") as f:
            f.write(english_test_content)

    root = tk.Tk()
    app = TextComparerApp(root)
    app._preload_file_paths()
    root.mainloop()