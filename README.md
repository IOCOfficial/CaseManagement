# 🕵️‍♂️ IOC - Investigation Case Manager

A terminal-based investigation case management system with integrated Obsidian vault creation and optional ChatGPT-powered report generation.

---

## 🚀 Features

- 📁 Automatically creates a case folder with subdirectories
- ✍️ Adds Markdown files and metadata per case
- 🧠 Optionally uses ChatGPT to summarize evidence and generate full reports
- 💼 Each case is opened as a dedicated Obsidian vault with your preconfigured template
- 📊 View a dynamic terminal UI with tables, colors, summaries, and deep-dive options
- 🔐 Works offline, but ChatGPT-enhanced features require OpenAI access

---

## 📂 Folder Structure (Auto-Generated Per Case)

~/Investigations/ 
    └── Case_<ID>/ 
    ├── 0. Introduction/ 
    ├── 1. Blockchain Analysis/ 
    ├── 2. OSINT/ 
    ├── 3. Evidence/ 
    ├── 4. Report/ 
    ├── 99. Tasks/ 
    ├── notes.txt 
    └── .obsidian/

---
```
pip install -r requirements.txt
```
---

## 🛠️ Setup Instructions

### 1. Clone the Repo

```
git clone https://github.com/your-username/investigation-case-manager.git
cd investigation-case-manager
```

---

## 🧠 Optional: Enable ChatGPT Integration

To use AI-powered summaries in your reports:

Get your API key from OpenAI: https://platform.openai.com/account/api-keys

Add it to your terminal environment:

```
export OPENAI_API_KEY="sk-..."
```
Restart the terminal or your Python script

---

## 📦 Vault Template Setup (Obsidian)

1. Export Your Obsidian Vault Template
```
mkdir -p ~/vault_template
cp -R "/path/to/your/vault/.obsidian" ~/vault_template/
```

Example (iCloud Path):
```
mkdir -p ~/vault_template
cp -R "/Users/b52/Library/Mobile Documents/iCloud~md~obsidian/Documents/IOC Vault/211024EA CRYPTOBOSSUK/.obsidian" ~/vault_template/
```

You can also use:
```
rsync -avh "/path/to/vault/.obsidian/" ~/vault_template/.obsidian/
```
This prevents issues with extended file attributes on macOS.

### 2. Point the script to this template folder:
In your Python script:
```
VAULT_TEMPLATE = os.path.expanduser("~/vault_template/.obsidian")
```

## 📝 Usage
Run the script:
```
python3 main.py
```

## Main Menu:
 -------------------------------------------
| Option | Action                           |
|--------|----------------------------------|
| 1      | Create Case                      |
| 2      | List Cases                       |
| 3      | View Case + Deep Dive Summary    |
| 4      | Update Case Status & Payment     |
| 5      | Delete Case                      |
| 6      | Generate Case Report             |
| 7      | Open Case in Obsidian            |
| 99     | Exit                             |
 -------------------------------------------

## 📑 Report Generation Options
You will be prompted to choose:
  1. Traditional Summary (basic text parsing)
  2. AI Summary via ChatGPT (uses GPT-4 to summarize each folder’s notes)

Output report is saved to:
```
Case_<ID>/4. Report/Case_<ID>_Report.md
```
## ✨ Optional Enhancements Already Supported

- Auto-apply vault layout, plugins, and themes from your template
- Open Obsidian directly to 0. Introduction.md
- Prevent duplicate case creation 
- Truncate long URLs for clean terminal display
- Summarize and extract key content across folders

## 🛡️ Disclaimer
This tool supports investigation case management, but should not be used as a sole source of truth.
All reports must be reviewed by a qualified analyst or investigator.

# 📄 License
Licensed under the MIT License


