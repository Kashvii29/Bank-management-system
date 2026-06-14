# 🏦 Bank Management System

A full-stack Bank Management System built with **Python (OOP)**, **Flask**, and **HTML/CSS**.

---

## 📁 Project Structure

```
bank_system/
├── app.py              # Flask app + all OOP classes
├── bank_data.json      # Auto-generated data store
├── requirements.txt
└── templates/
    ├── base.html       # Shared layout + all CSS
    ├── index.html      # Landing page
    ├── register.html   # Open account
    ├── login.html      # Login
    ├── dashboard.html  # Account overview
    ├── action.html     # Deposit / Withdraw
    ├── transfer.html   # Fund transfer
    └── history.html    # Full transaction log
```

---

## ⚙️ Setup & Run

```bash
# 1. Install dependencies
pip install flask

# 2. Run the app
cd bank_system
python app.py

# 3. Open browser
http://127.0.0.1:5000
```

---

## 🐍 OOP Concepts Used

| Class         | Responsibility                                      |
|---------------|-----------------------------------------------------|
| `Transaction` | Stores type, amount, balance, timestamp             |
| `BankAccount` | deposit / withdraw / transfer + transaction history |
| `Bank`        | Manages all accounts, JSON persistence, auth        |

---

## ✨ Features

- ✅ Register with initial deposit
- ✅ Secure login (account number + password)
- ✅ Deposit & Withdraw with validation
- ✅ Fund Transfer between accounts
- ✅ Full timestamped transaction history
- ✅ Data persisted to `bank_data.json`
- ✅ Flash messages for success/error feedback
