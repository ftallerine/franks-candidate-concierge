# 🛡️ Security Guidelines for Candidate Concierge

This document outlines the security architecture and best practices for this project. The system is designed to be forked and used by others, keeping personal data secure and out of version control.

## 🏛️ Core Security Architecture: Environment-Based Data Loading

This project follows the [Twelve-Factor App methodology](https://12factor.net/config) by storing all sensitive data and configuration in the environment.

**No sensitive information (API keys, database passwords, personal data) is stored in files within the repository.**

Here’s how it works:
1.  **Data Structure Template (`resume_data_template.py`):** The structure of the resume data is defined in this template file using placeholders (e.g., `ENV::CONTACT_NAME`). This file is safe to commit to Git.
2.  **Secure Data Loader (`data_loader.py`):** At application startup, this module reads the template.
3.  **Environment Injection:** The data loader then scans the template and replaces every placeholder with a corresponding value from an **environment variable** (e.g., `os.getenv("CONTACT_NAME")`).
4.  **Runtime Only:** Your personal data exists **only in memory** on the running server and is never written to disk in the deployed environment.

This ensures that your GitHub repository remains free of personal data, and the deployed application loads sensitive information securely at runtime.

---

## 🚀 Quick Setup & Configuration

### Step 1: Clone and Configure Environment

First, create a `.env` file in the project root. This file is listed in `.gitignore` and will never be committed.

You can create it by copying the template: `cp .env.example .env` (if the file exists) or creating it manually.

Your `.env` file should contain the following variables. Fill them out with your actual data.

```bash
# --- Core Application Config ---
DATABASE_URL=postgresql://user:password@host:port/database # For cloud deployment
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_32_byte_hex_secret_key_here # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
DEBUG_MODE=False

# ================================================
# --- PERSONAL RESUME DATA ENVIRONMENT VARIABLES ---
# ================================================

# --- Contact Information ---
CONTACT_NAME="Your Full Name"
CONTACT_LOCATION="Your City, State"
# ... (and so on for all variables defined in resume_data_template.py)
```
*(For a full list of all personal data variables, please see `src/models/resume_data_template.py`)*

### Step 2: Install Dependencies & Run

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app:app --reload
```

### Step 3: Verify Security

```bash
# Check that sensitive files are properly ignored by Git
git status

# The output should NOT show your .env file.
# If it does, ensure '.env' is listed in your .gitignore file.
```

---

## 🔐 Security Best Practices for Contributors

*   **Never Hardcode Secrets:** Do not write API keys, passwords, or personal data directly in the code. Use the established environment variable system.
*   **Update the Template:** If you add new data points to the resume, add a corresponding `ENV::` placeholder to `src/models/resume_data_template.py`.
*   **Keep `.env` Local:** Your `.env` file should never be committed to Git.
*   **Use Strong Secrets:** For `SECRET_KEY` and database passwords, use long, randomly generated strings.

### Production Deployment

When deploying to a hosting provider like Render, Heroku, or Azure:
1.  Do **not** upload your `.env` file.
2.  Use the provider's web interface to set the environment variables. They are often found under a "Secrets" or "Environment" section. This is a much more secure way to manage production credentials.

---

## 📞 Security Resources

*   [OWASP Security Guidelines](https://owasp.org/)
*   [The Twelve-Factor App](https://12factor.net/)
*   [Python Security Best Practices](https://python-security.readthedocs.io/) 