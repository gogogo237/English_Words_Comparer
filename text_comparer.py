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

        # Prefer subfolder test files if they exist
        test_folder_name = "TestTaggingFolder"
        bilingual_test_file_path_sub = os.path.join(test_folder_name, "BilingualText.txt")
        english_test_file_path_sub = os.path.join(test_folder_name, "EnglishText.txt")

        if os.path.exists(bilingual_test_file_path_sub):
            self.bilingual_file_path.set(os.path.abspath(bilingual_test_file_path_sub))
            self.bilingual_label.config(text=f"Bilingual: {os.path.basename(bilingual_test_file_path_sub)} (in {test_folder_name})")
        elif os.path.exists(bilingual_default):
            self.bilingual_file_path.set(os.path.abspath(bilingual_default))
            self.bilingual_label.config(text=f"Bilingual: {os.path.basename(bilingual_default)}")
        
        if os.path.exists(english_test_file_path_sub):
            self.english_file_path.set(os.path.abspath(english_test_file_path_sub))
            self.english_label.config(text=f"English: {os.path.basename(english_test_file_path_sub)} (in {test_folder_name})")
        elif os.path.exists(english_default):
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

    def _count_words(self, text_line):
        return len(text_line.strip().split())

    def _get_last_word(self, text_line):
        words = text_line.strip().split()
        if words:
            last_word = words[-1]
            last_word_cleaned = last_word.rstrip(string.punctuation)
            return last_word_cleaned
        return ""

    def _tag_paragraphs(self):
        self.results_text.delete('1.0', tk.END)
        detailed_log_messages = ["Starting paragraph tagging process...\n"]

        bilingual_input_path = self.bilingual_file_path.get()
        english_ref_path = self.english_file_path.get()

        if not bilingual_input_path or not english_ref_path:
            error_msg = "ERROR: Input files missing. Please select both bilingual and English text files.\n"
            self.results_text.insert(tk.END, error_msg) # Show error directly
            messagebox.showwarning("Input Missing", "Please select both text files for paragraph tagging.")
            return

        try:
            with open(bilingual_input_path, 'r', encoding='utf-8') as f:
                bilingual_lines_raw = f.readlines()
            with open(english_ref_path, 'r', encoding='utf-8') as f:
                english_ref_lines_raw = f.readlines()
        except Exception as e:
            error_msg = f"Error reading files: {e}"
            self.results_text.insert(tk.END, f"CRITICAL ERROR: {error_msg}\n") # Show error directly
            messagebox.showerror("File Error", error_msg)
            return

        english_ref_paragraphs_info = []
        for line_num, line_text in enumerate(english_ref_lines_raw):
            text = line_text.strip()
            if not text: continue
            word_count = self._count_words(text)
            last_word = self._get_last_word(text)
            if word_count > 0:
                english_ref_paragraphs_info.append({
                    "text": text, "word_count": word_count,
                    "last_word": last_word, "original_line_num": line_num + 1
                })
        # This info is now part of the detailed log, not the matching summary directly
        # detailed_log_messages.append(f"Processed {len(english_ref_paragraphs_info)} non-blank paragraphs from English reference file.\n")

        potential_bilingual_content_lines_info = []
        for original_idx, line_text in enumerate(bilingual_lines_raw):
            if line_text.strip():
                potential_bilingual_content_lines_info.append({
                    "text_content_no_newline": line_text.rstrip('\n'),
                    "original_full_line_text": line_text, "original_idx": original_idx
                })

        bilingual_eng_lines_with_info = []
        for i in range(0, len(potential_bilingual_content_lines_info), 2):
            bilingual_eng_lines_with_info.append(potential_bilingual_content_lines_info[i])

        if not bilingual_eng_lines_with_info:
            detailed_log_messages.append("WARNING: No potential English lines identified in the bilingual file based on 'every other non-blank line' rule.\n")
        else:
            detailed_log_messages.append(f"Identified {len(bilingual_eng_lines_with_info)} potential English lines from bilingual file.\n")

        bilingual_filename_itself = os.path.basename(bilingual_input_path)
        containing_folder_path = os.path.dirname(bilingual_input_path)
        normalized_containing_folder_path = os.path.normpath(containing_folder_path)
        folder_name_for_output_file_base = os.path.basename(normalized_containing_folder_path)
        
        is_special_case_for_naming = False
        if not folder_name_for_output_file_base or folder_name_for_output_file_base == ".":
            is_special_case_for_naming = True
        elif os.name == 'nt' and len(folder_name_for_output_file_base) == 2 and \
             folder_name_for_output_file_base[1] == ':' and folder_name_for_output_file_base[0].isalpha():
            is_special_case_for_naming = True
        elif os.name != 'nt' and folder_name_for_output_file_base == os.sep: # For root path like '/'
            is_special_case_for_naming = True

        if is_special_case_for_naming:
            bilingual_file_name_base, _ = os.path.splitext(bilingual_filename_itself)
            output_file_basename = bilingual_file_name_base + "_Tagged"
            detailed_log_messages.append(
                f"INFO: Bilingual file's containing folder is root, CWD, or ambiguous. Using fallback output name: {output_file_basename}.txt\n"
            )
        else:
            output_file_basename = folder_name_for_output_file_base
        
        output_filename = output_file_basename + ".txt"
        output_dir = containing_folder_path if containing_folder_path else os.getcwd()
        output_filepath = os.path.join(output_dir, output_filename)
        # This info is also part of the detailed log
        # detailed_log_messages.append(f"INFO: Target output file path set to: {output_filepath}\n")

        original_indices_of_lines_to_pre_tag = set()
        bilingual_search_start_idx = 0
        num_successful_matches = 0
        num_last_word_mismatches_for_wc_match = 0
        num_unmatched_ref_paras = 0

        detailed_log_messages.append("\n--- Matching Process ---\n")
        for ref_para_idx, ref_para_info in enumerate(english_ref_paragraphs_info):
            ref_wc = ref_para_info["word_count"]
            ref_lw_cleaned = ref_para_info["last_word"]
            detailed_log_messages.append(f"Attempting to match Ref Para {ref_para_idx + 1} (Line {ref_para_info['original_line_num']}, WC: {ref_wc}, Cleaned LW: '{ref_lw_cleaned}')\n")

            found_match_for_this_ref_para = False
            if bilingual_eng_lines_with_info:
                for i in range(bilingual_search_start_idx, len(bilingual_eng_lines_with_info)):
                    current_block_word_count = 0
                    current_block_lines_info = []
                    for j in range(i, len(bilingual_eng_lines_with_info)):
                        bili_eng_line_info = bilingual_eng_lines_with_info[j]
                        line_text_no_newline = bili_eng_line_info["text_content_no_newline"]
                        line_word_count = self._count_words(line_text_no_newline)

                        if current_block_word_count + line_word_count > ref_wc: break
                        current_block_word_count += line_word_count
                        current_block_lines_info.append(bili_eng_line_info)

                        if current_block_word_count == ref_wc:
                            block_last_line_text = current_block_lines_info[-1]["text_content_no_newline"]
                            block_last_word_cleaned = self._get_last_word(block_last_line_text)
                            if block_last_word_cleaned.lower() == ref_lw_cleaned.lower():
                                first_line_original_idx = current_block_lines_info[0]["original_idx"]
                                original_indices_of_lines_to_pre_tag.add(first_line_original_idx)
                                num_successful_matches += 1
                                bilingual_search_start_idx = j + 1
                                found_match_for_this_ref_para = True
                                detailed_log_messages.append(f"  MATCHED: Bilingual block (Original lines {current_block_lines_info[0]['original_idx']+1} to {bili_eng_line_info['original_idx']+1}) WC: {current_block_word_count}, Cleaned LW: '{block_last_word_cleaned}'.\n")
                                break
                            else:
                                num_last_word_mismatches_for_wc_match +=1
                                detailed_log_messages.append(f"  LAST WORD MISMATCH: Ref Para (Cleaned LW: '{ref_lw_cleaned}') vs Bilingual block (Cleaned LW '{block_last_word_cleaned}', Original last line idx: {bili_eng_line_info['original_idx']+1}). WC ({ref_wc}) matched. Block not chosen.\n")
                    if found_match_for_this_ref_para: break
            
            if not found_match_for_this_ref_para:
                num_unmatched_ref_paras +=1
                detailed_log_messages.append(f"  NO MATCH FOUND for Ref Para {ref_para_idx + 1} in remaining bilingual text.\n")
        
        detailed_log_messages.append("--- Matching Process Complete ---\n\n")

        output_lines_for_tagged_file = []
        for original_idx, original_line_text in enumerate(bilingual_lines_raw):
            if original_idx in original_indices_of_lines_to_pre_tag:
                output_lines_for_tagged_file.append("<paragraph>\n")
            output_lines_for_tagged_file.append(original_line_text)
        num_tags_added = len(original_indices_of_lines_to_pre_tag)

        # --- Assemble and Display Summaries and Logs ---
        overall_summary_lines = []
        matching_summary_lines = []
        detailed_log_header = []

        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.writelines(output_lines_for_tagged_file)

            # 1. Overall Operation Summary
            op_summary_title = "Tagging Operation Summary:"
            op_summary_sep = "-" * len(op_summary_title)
            overall_summary_lines.extend([
                f"{op_summary_title}\n",
                f"{op_summary_sep}\n",
                f"Output File: {output_filepath}\n",
                f"Number of <paragraph> tags added: {num_tags_added}\n",
                f"{op_summary_sep}\n\n"
            ])

            # 2. Summary of Matching
            match_summary_title = "Summary of Matching:"
            match_summary_sep = "-" * len(match_summary_title)
            matching_summary_lines.extend([
                f"{match_summary_title}\n",
                f"{match_summary_sep}\n",
                f"Total English reference paragraphs processed: {len(english_ref_paragraphs_info)}\n",
                f"Successfully matched and tagged: {num_successful_matches}\n",
            ])
            if num_last_word_mismatches_for_wc_match > 0:
                matching_summary_lines.append(
                    f"Word count matches with last word mismatch (not tagged): {num_last_word_mismatches_for_wc_match}\n"
                )
            if num_unmatched_ref_paras > 0:
                matching_summary_lines.append(
                    f"Reference paragraphs with no suitable block found: {num_unmatched_ref_paras}\n"
                )
            if num_tags_added == 0 and len(english_ref_paragraphs_info) > 0 and num_successful_matches == 0:
                matching_summary_lines.append(
                    "(No English paragraphs from the reference file could be matched and tagged based on criteria.)\n"
                )
            matching_summary_lines.append(f"{match_summary_sep}\n\n")

            # 3. Detailed Log Header
            log_header_title = "Detailed Log:"
            log_header_sep = "-" * len(log_header_title)
            detailed_log_header.extend([
                f"{log_header_title}\n",
                f"{log_header_sep}\n"
            ])
            
            # Insert into ScrolledText in desired order
            self.results_text.insert('1.0', "".join(overall_summary_lines))
            self.results_text.insert(tk.END, "".join(matching_summary_lines))
            self.results_text.insert(tk.END, "".join(detailed_log_header))
            self.results_text.insert(tk.END, "".join(detailed_log_messages)) # The actual step-by-step log
            
            if num_successful_matches > 0 :
                 messagebox.showinfo("Success", f"Tagging complete. {num_tags_added} tags added. Output: {output_filepath}\nSee log for details.")
            else:
                 messagebox.showwarning("Tagging Complete (Potential Issues)", f"Tagging process ran. {num_tags_added} tags added. Output: {output_filepath}\nReview 'Summary of Matching' and 'Detailed Log' for details.")

        except Exception as e:
            error_msg = f"Could not write tagged file to {output_filepath}: {e}"
            # Display error prominently if file write fails
            self.results_text.insert('1.0', f"CRITICAL FILE WRITE ERROR: {error_msg}\n{'-'*20}\n\n")
            self.results_text.insert(tk.END, "".join(detailed_log_messages))
            messagebox.showerror("File Write Error", error_msg)


if __name__ == "__main__":
    # Create dummy files for testing all features, including paragraph tagging
    bilingual_test_content = """This is an English sentence.
Ceci est une phrase française.
It has seven words in total.
Il a sept mots au total.
This should be the start of another paragraph.
Cela devrait être le début d'un autre paragraphe.
And this continues it, having ten words combined.
Et cela continue, ayant dix mots combinés.
A short one.
Un court.
Another final English sentence.
Une autre dernière phrase anglaise.
"""
    english_test_content = """This is an English sentence. It has seven words in total.
This should be the start of another paragraph. And this continues it, having ten words combined.
A short one.
A different paragraph not matching bilingual exactly.
"""

    test_folder_name = "TestTaggingFolder"
    if not os.path.exists(test_folder_name):
        os.makedirs(test_folder_name)

    bilingual_test_file_path = os.path.join(test_folder_name, "BilingualText.txt")
    english_test_file_path = os.path.join(test_folder_name, "EnglishText.txt")

    if not os.path.exists(bilingual_test_file_path):
        with open(bilingual_test_file_path, "w", encoding="utf-8") as f:
            f.write(bilingual_test_content)
        print(f"Created dummy file: {bilingual_test_file_path}")

    if not os.path.exists(english_test_file_path):
        with open(english_test_file_path, "w", encoding="utf-8") as f:
            f.write(english_test_content)
        print(f"Created dummy file: {english_test_file_path}")

    if not os.path.exists("BilingualText_CWD.txt"):
         with open("BilingualText_CWD.txt", "w", encoding="utf-8") as f:
            f.write("English line in CWD.\nFrench line in CWD.")
         print("Created dummy file: BilingualText_CWD.txt")
    if not os.path.exists("EnglishText_CWD.txt"):
         with open("EnglishText_CWD.txt", "w", encoding="utf-8") as f:
            f.write("English line in CWD.")
         print("Created dummy file: EnglishText_CWD.txt")

    root = tk.Tk()
    app = TextComparerApp(root)
    # _preload_file_paths is called in __init__, which now prefers the subfolder test files
    root.mainloop()