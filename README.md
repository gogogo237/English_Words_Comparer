# Text Difference Finder GUI

A simple Tkinter-based desktop application to compare English text extracted from a bilingual (English/Chinese) file against a monolingual English file, highlighting word-by-word differences.

## Features

*   **User-friendly GUI:** Easy selection of input files.
*   **Bilingual Text Extraction:** Specifically designed to extract English sentences from a file where English lines alternate with Chinese lines.
    *   Handles blank lines between English-Chinese pairs.
    *   Assumes English text appears on the 1st, 3rd, 5th... non-blank lines.
*   **Punctuation Normalization:** Cleans text by removing punctuation before comparison, ensuring "word." and "word" are treated as identical.
*   **Word-by-Word Comparison:** Compares the extracted English text with a reference English text, word by word.
*   **Difference Highlighting:** Displays differences found, showing the word from the bilingual extract and the corresponding word from the reference English text, along with their index.
*   **Word Count Display:** Shows total word counts for both processed texts.

## How It Works

1.  **File Selection:** The user selects two `.txt` files:
    *   **Bilingual Text File:** A file containing alternating lines of English and (presumably) Chinese text.
    *   **English Text File:** A file containing only English text, which serves as the reference.
2.  **Bilingual Extraction:** The application reads the bilingual file, filters out any completely blank lines, and then extracts lines at even indices (0, 2, 4, ...) from the remaining content, assuming these are the English sentences. These sentences are then joined into a single string.
3.  **Text Cleaning & Tokenization:** Both the extracted English string and the content of the reference English file are processed:
    *   Punctuation marks (e.g., '.', ',', '!', '?') are replaced with spaces.
    *   The texts are then split into lists of words.
4.  **Comparison:** The two lists of words are compared element by element.
5.  **Results Display:**
    *   Any discrepancies are reported in the results text area, showing the differing words and their position (index) in the word list.
    *   If no differences are found, a confirmation message is displayed.
    *   Word counts for both processed texts are also shown.

## Requirements

*   Python 3.x
*   Tkinter (usually included with standard Python installations)

## How to Run

1.  Save the script as a Python file (e.g., `text_comparer_app.py`).
2.  Ensure you have two text files prepared:
    *   `BilingualText.txt` (or similar): With alternating English and Chinese lines. Example:
        ```
        This is an English sentence.
        这是一句中文。

        Another English line.
        另一行中文。
        ```
    *   `EnglishText.txt` (or similar): With the English text you want to compare against. Example:
        ```
        This is an English sentence. Another English line perhaps with a typo.
        ```
3.  Open a terminal or command prompt.
4.  Navigate to the directory where you saved the script.
5.  Run the script using:
    ```bash
    python text_comparer_app.py
    ```

## How to Use the Application

1.  Launch the application.
2.  Click "Select Bilingual Text File (.txt)" and choose your bilingual file.
3.  Click "Select English Text File (.txt)" and choose your reference English file.
4.  Click the "Compare English Words" button.
5.  View the comparison results in the text area below. Differences will be listed, or a "No differences found" message will appear. Word counts will also be displayed.

## Future Enhancements (Possible To-Do)

*   Option for case-insensitive comparison.
*   More sophisticated diff algorithm (e.g., using `difflib` for a more "diff-like" output showing insertions/deletions/changes).
*   Ability to save the comparison results to a file.
*   Configuration for different bilingual patterns (e.g., Chinese first, or different delimiters).
*   Highlighting differences directly within the displayed text (more complex).

## License

This project is open source. Feel free to use, modify, and distribute. If no specific license is attached, consider it under a permissive license like MIT.
(You can add a specific license file like `LICENSE.md` if you prefer, e.g., MIT License)