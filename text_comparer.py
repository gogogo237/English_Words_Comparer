import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import string # For string.punctuation

class TextComparerApp:
    def __init__(self, master):
        self.master = master
        master.title("Text Difference Finder")
        master.geometry("700x550")

        self.bilingual_file_path = tk.StringVar()
        self.english_file_path = tk.StringVar()

        # --- File Selection Frame ---
        file_frame = tk.Frame(master, pady=10)
        file_frame.pack(fill=tk.X)

        tk.Button(file_frame, text="Select Bilingual Text File (.txt)", command=self._select_bilingual_file).pack(side=tk.LEFT, padx=5)
        self.bilingual_label = tk.Label(file_frame, text="No bilingual file selected")
        self.bilingual_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # New row for the second file selector to avoid crowding
        file_frame2 = tk.Frame(master, pady=5)
        file_frame2.pack(fill=tk.X)

        tk.Button(file_frame2, text="Select English Text File (.txt)", command=self._select_english_file).pack(side=tk.LEFT, padx=5)
        self.english_label = tk.Label(file_frame2, text="No English file selected")
        self.english_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- Compare Button ---
        tk.Button(master, text="Compare English Words", command=self._compare_texts, pady=5).pack(pady=10)

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
                # Filter out blank lines and strip whitespace from non-blank ones
                content_lines = [line.strip() for line in all_lines if line.strip()]
                # Assuming English is on 0, 2, 4... (even indices) of the content_lines
                for i in range(0, len(content_lines), 2):
                    english_lines_extracted.append(content_lines[i])
            return " ".join(english_lines_extracted)
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
        """
        Tokenizes text by splitting on whitespace after normalizing punctuation.
        Punctuation marks are replaced by spaces to separate them from words or remove them if standalone.
        """
        if not text:
            return []
        
        # Create a translation table: map each punctuation char (from string.punctuation) to a space.
        # string.punctuation is '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        
        # Apply the translation, replacing punctuation with spaces.
        # E.g., "word." becomes "word ", "word ." becomes "word  "
        text_no_punct_attached = text.translate(translator)
        
        # Split into words based on whitespace. This naturally handles multiple spaces
        # created by punctuation replacement and removes empty strings that would result.
        # E.g., "word ".split() -> ['word']
        # E.g., "word  ".split() -> ['word']
        words = text_no_punct_attached.split()
        
        return words

    def _compare_texts(self):
        self.results_text.delete('1.0', tk.END) # Clear previous results

        bilingual_path = self.bilingual_file_path.get()
        english_path = self.english_file_path.get()

        if not bilingual_path or not english_path:
            messagebox.showwarning("Input Missing", "Please select both text files.")
            return

        extracted_bilingual_eng_raw = self._extract_english_from_bilingual(bilingual_path)
        if extracted_bilingual_eng_raw is None: # Error occurred during extraction
            return

        pure_english_text_raw = self._read_english_text(english_path)
        if pure_english_text_raw is None: # Error occurred during reading
            return

        # Tokenize using the new cleaning function
        bilingual_words = self._tokenize_and_clean_text(extracted_bilingual_eng_raw)
        english_words = self._tokenize_and_clean_text(pure_english_text_raw)

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

            # Compare (case-sensitive)
            if word_b != word_e:
                differences_found = True
                # The index 'i' refers to the index in the cleaned word list.
                self.results_text.insert(tk.END, f"Difference at word index {i}:\n")
                self.results_text.insert(tk.END, f"  Bilingual Extracted: '{word_b}'\n")
                self.results_text.insert(tk.END, f"  EnglishText.txt:     '{word_e}'\n\n")

        if not differences_found:
            self.results_text.insert(tk.END, "No differences found between the English words after cleaning punctuation.\n")
        
        # Always show word counts if comparison was performed
        if len(bilingual_words) != len(english_words):
                self.results_text.insert(tk.END, f"(Note: Cleaned word counts differ - Bilingual Extract: {len(bilingual_words)}, EnglishText: {len(english_words)})\n")
        else: # if lengths are same
            if not differences_found: # and no diffs found, they are identical in content
                 self.results_text.insert(tk.END, f"(Cleaned word counts match: {len(bilingual_words)})\n")


if __name__ == "__main__":
    # Create dummy files for testing the punctuation handling
    bilingual_test_content = """It was pandaemonium.
中文
The place was buzzing.
中文
"""
    # EnglishText.txt will have a period separated by space, and an extra word
    english_test_content = """It was pandaemonium .
The place was buzzing .
And one more word.
"""
    # Expected outcome after _tokenize_and_clean_text:
    # Bilingual: ['It', 'was', 'pandaemonium', 'The', 'place', 'was', 'buzzing']
    # English:   ['It', 'was', 'pandaemonium', 'The', 'place', 'was', 'buzzing', 'And', 'one', 'more', 'word']
    # Difference will be found when 'And' is compared to <END_OF_BILINGUAL_EXTRACT>

    if not os.path.exists("BilingualText.txt"):
        with open("BilingualText.txt", "w", encoding="utf-8") as f:
            f.write(bilingual_test_content)

    if not os.path.exists("EnglishText.txt"):
        with open("EnglishText.txt", "w", encoding="utf-8") as f:
            f.write(english_test_content)

    root = tk.Tk()
    app = TextComparerApp(root)
    app._preload_file_paths() # Call after creating/checking files
    root.mainloop()