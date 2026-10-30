RetainIQ - Run locally in VS Code (Windows)

FILES
- app.py: Streamlit user interface
- retainIQ_model.pkl: model uploaded from Google Colab
- requirements.txt: Python dependencies
- customer_churn_prediciton_system.ipynb: original notebook for reference

RUN STEPS
1. Extract this folder.
2. Open the extracted folder in VS Code (File > Open Folder).
3. Open Terminal > New Terminal.
4. Create a virtual environment:
   python -m venv .venv
5. Activate it in PowerShell:
   .\.venv\Scripts\Activate.ps1
   If PowerShell blocks activation, use Command Prompt and run:
   .venv\Scripts\activate.bat
6. Install dependencies:
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
7. Start the app:
   python -m streamlit run app.py
8. Open the local URL printed in the terminal, usually http://localhost:8501.

IMPORTANT
- Keep retainIQ_model.pkl in the same folder as app.py.
- The model was saved from Colab. Loading scikit-learn models across versions is not guaranteed; requirements pins scikit-learn 1.6.1 to match the reported training version.
- The app expects these columns in uploaded CSV files:
  Age, Total_Purchase, Account_Manager, Years, Num_Sites
- Account_Manager accepts Yes/No, True/False, or 1/0 in bulk CSV input.
- Test with the app's downloadable sample CSV template first.
- If you get an error, copy the full terminal traceback and share it for debugging.
