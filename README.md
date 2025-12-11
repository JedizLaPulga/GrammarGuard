# GrammarGuard 🛡️

> **A privacy-first AI grammar corrector that runs 100% offline.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Powered by SpaCy](https://img.shields.io/badge/Powered%20by-spaCy-09a3d5)](https://spacy.io/)
[![Status](https://img.shields.io/badge/Status-Beta-orange)]()

**GrammarGuard** is a desktop GUI application designed for those who value data sovereignty. Unlike popular grammar tools that send your keystrokes to the cloud, GrammarGuard processes everything locally on your machine.

Whether you are working on sensitive legal documents, proprietary code comments, or personal journals, GrammarGuard ensures your text never leaves your computer.

![GrammarGuard Screenshot](docs/screenshot_placeholder.png)
*(Note: Add a screenshot of your GUI here)*

---

## ✨ Key Features

* **🔒 100% Offline & Private:** No API calls, no cloud servers, no data tracking. Your data stays on your local drive.
* **🖥️ User-Friendly GUI:** A clean, minimal desktop interface designed for distraction-free editing.
* **⚡ Powered by SpaCy:** Utilizes industrial-strength Natural Language Processing for accurate syntax and grammar analysis.
* **📄 File Support:** Import and correct `.txt`, `.md`, and `.docx` files directly.
* **🚀 Local Inference:** Optimized for local performance to provide fast feedback without network lag.

---

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **NLP Engine:** [spaCy](https://spacy.io/)
* **GUI Framework:** Flutter

---

## 📥 Installation

### Prerequisites

Ensure you have the following installed:
*   [Python 3.9+](https://www.python.org/downloads/)
*   [Git](https://git-scm.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/grammarguard.git
cd grammarguard
```

### 2. Set Up a Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLP Models

GrammarGuard uses `spaCy`'s English model for analysis. Run the following command to download it:

```bash
python -m spacy download en_core_web_sm
```

---

## 🚀 Usage

*(Instructions on how to launch the application will be added here once the entry point is established)*

To run the backend development server (if applicable):
```bash
# Example command
# python main.py
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
