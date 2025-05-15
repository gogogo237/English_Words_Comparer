import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import string # For string.punctuation

class TextComparerApp:
    def __init__(self, master):
        self.master = master
        master.title("Text Difference Finder")
        master.geometry("700x650") # Increased height for the new button

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
        tk.Button(action_frame, text="Tag Paragraphs", command=self._tag_paragraphs, pady=5).pack(side=tk.LEFT, padx=5) # New button

        # --- Results Display ---
        tk.Label(master, text="Comparison Results / Log:").pack() # Changed label slightly
        self.results_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=20, width=80)
        self.results_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self._preload_file_paths() # Preload after all UI elements are defined

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
                content_lines = [line.rstrip('\n') for line in all_lines if line.strip()]
                for i in range(0, len(content_lines), 2):
                    english_lines_extracted.append(content_lines[i])
            return "\n".join(english_lines_extracted)
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
        if not text:
            return []
        punctuation_marks = []
        lines = text.splitlines() 
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

            if word_b.lower() != word_e.lower():
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

        extracted_bilingual_eng_raw = self._extract_english_from_bilingual(bilingual_path)
        if extracted_bilingual_eng_raw is None: return

        pure_english_text_raw = self._read_english_text(english_path)
        if pure_english_text_raw is None: return

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
                diff_type = "EnglishText.txt has fewer punctuation marks."

            if i < len(puncts_english):
                p_e_char, p_e_line, p_e_col = puncts_english[i]
            else:
                diff_type = "Bilingual Extract has fewer punctuation marks."
            
            if p_b_char is not None and p_e_char is not None:
                if p_b_char != p_e_char:
                    diff_type = "Punctuation characters differ."
            
            if diff_type: 
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
        elif not differences_found:
             self.results_text.insert(tk.END, f"(Punctuation counts match: {len(puncts_bilingual)})\n")

    def _tag_paragraphs(self):
        self.results_text.delete('1.0', tk.END)
        bilingual_path = self.bilingual_file_path.get()
        english_path = self.english_file_path.get()

        if not bilingual_path or not english_path:
            messagebox.showwarning("Input Missing", "Please select both text files for paragraph tagging.")
            return

        try:
            with open(bilingual_path, 'r', encoding='utf-8') as f:
                bilingual_lines_raw = f.readlines() # Keep original newlines
            with open(english_path, 'r', encoding='utf-8') as f:
                english_content_full = f.read()
        except Exception as e:
            error_msg = f"Error reading files: {e}"
            self.results_text.insert(tk.END, f"ERROR: {error_msg}\n")
            messagebox.showerror("File Error", error_msg)
            return

        # Step 1: Identify "English sentences" from BilingualText.txt by their original indices.
        potential_content_lines_info = []
        for original_idx, line_text in enumerate(bilingual_lines_raw):
            if line_text.strip(): 
                potential_content_lines_info.append({
                    "text_content_no_newline": line_text.rstrip('\n'), 
                    "original_full_line_text": line_text,              
                    "original_idx": original_idx                       
                })

        identified_bilingual_eng_lines_info = []
        for i in range(0, len(potential_content_lines_info), 2):
            identified_bilingual_eng_lines_info.append(potential_content_lines_info[i])

        # Step 2: Determine which of these English lines need a <paragraph> tag before them.
        original_indices_of_lines_to_pre_tag = set()
        for eng_line_info in identified_bilingual_eng_lines_info:
            sentence_to_search = eng_line_info["text_content_no_newline"].strip()

            if not sentence_to_search: 
                continue
            
            current_search_pos_in_eng_text = 0
            found_at_line_start_in_eng_text = False
            while True:
                idx_in_english_text = english_content_full.find(sentence_to_search, current_search_pos_in_eng_text)
                if idx_in_english_text == -1: 
                    break
                if idx_in_english_text == 0 or \
                   (idx_in_english_text > 0 and english_content_full[idx_in_english_text - 1] == '\n'):
                    found_at_line_start_in_eng_text = True
                    break 
                current_search_pos_in_eng_text = idx_in_english_text + 1 

            if found_at_line_start_in_eng_text:
                original_indices_of_lines_to_pre_tag.add(eng_line_info["original_idx"])

        # Step 3: Construct the new bilingual text content with tags
        output_lines_for_taged_file = []
        for original_idx, original_line_text in enumerate(bilingual_lines_raw):
            if original_idx in original_indices_of_lines_to_pre_tag:
                output_lines_for_taged_file.append("<paragraph>\n")
            output_lines_for_taged_file.append(original_line_text)
        
        # Step 4: Write to the output file "TagedBilingualText.txt"
        output_filename = "TagedBilingualText.txt"
        output_dir = os.path.dirname(bilingual_path) if bilingual_path and os.path.dirname(bilingual_path) else os.getcwd()
        output_filepath = os.path.join(output_dir, output_filename)

        # MODIFIED SECTION STARTS HERE
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.writelines(output_lines_for_taged_file)
            
            num_tags_added = len(original_indices_of_lines_to_pre_tag)
            
            log_message = f"Paragraph tagging complete.\n"
            log_message += f"Tagged file saved as: {output_filepath}\n"
            log_message += f"Number of <paragraph> tags added: {num_tags_added}\n"
            
            if num_tags_added == 0:
                 log_message += "(No English sentences from BilingualText.txt (matching criteria) were found at the start of lines in EnglishText.txt to warrant tagging.)\n"
            
            # --- Confirmation part ---
            # Count non-blank lines in EnglishText.txt (using english_content_full read earlier)
            english_lines_in_file = english_content_full.splitlines() # Use splitlines() for consistency
            num_non_blank_lines_in_english_text = sum(1 for line in english_lines_in_file if line.strip())

            log_message += "\n--- Confirmation Check ---\n"
            log_message += f"Number of <paragraph> tags added (based on current logic): {num_tags_added}\n"
            log_message += f"Number of non-blank text lines in EnglishText.txt: {num_non_blank_lines_in_english_text}\n"
            
            comparison_message_for_popup = ""
            if num_tags_added == num_non_blank_lines_in_english_text:
                log_message += "Result: Counts match. This aligns with the confirmation criterion that these two numbers should be the same.\n"
                comparison_message_for_popup = "Counts match."
            else:
                log_message += "Result: Counts DO NOT match the confirmation criterion.\n"
                log_message += "This discrepancy occurs because the tagging logic (adding a tag if an English sentence from BilingualText.txt is found starting a line in EnglishText.txt) "
                log_message += "does not necessarily result in one tag for every non-blank line in EnglishText.txt.\n"
                log_message += "Potential reasons for mismatch include:\n"
                log_message += "  1. Not all non-blank lines in EnglishText.txt correspond to English sentences that are present in (and extracted from) BilingualText.txt.\n"
                log_message += "  2. English sentences from BilingualText.txt, even if present in EnglishText.txt, might not all start new lines there (and thus wouldn't be tagged by current rules).\n"
                log_message += "  3. The number of English segments in BilingualText.txt that meet all tagging criteria simply differs from the total count of non-blank lines in EnglishText.txt.\n"
                comparison_message_for_popup = "Counts DO NOT match. See log for details."
            # --- End of Confirmation part ---
            
            self.results_text.insert(tk.END, log_message)
            
            
        except Exception as e:
            error_msg = f"Could not write tagged file to {output_filepath}: {e}"
            self.results_text.insert(tk.END, f"ERROR: {error_msg}\n")
            messagebox.showerror("File Write Error", error_msg)
        # MODIFIED SECTION ENDS HERE


if __name__ == "__main__":
    # Create dummy files for testing all features, including paragraph tagging
    bilingual_test_content = """This is the first sentence.
Ceci est la première phrase.
This is the second sentence.
Ceci est la deuxième phrase.

This sentence starts a paragraph in English text.
Cette phrase commence un paragraphe dans le texte anglais.
Another sentence here.
Une autre phrase ici.
  Spaced sentence.  
  Phrase espacée.  
This sentence also starts a paragraph.
Cette phrase commence aussi un paragraphe.
Final English line with no pair.
"""
    english_test_content = """Some introductory text.
This is the first sentence, but not at the start.
This is the second sentence, also not at the start.
This sentence starts a paragraph in English text. And it continues.
Some other text. Spaced sentence. here.
This sentence also starts a paragraph.
And a final line.
"""

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