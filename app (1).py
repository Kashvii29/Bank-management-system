from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import json, os

app = Flask(__name__)
app.secret_key = "bank_secret_key_2024"

# ──────────────────────────────────────────
#  OOP Core Classes
# ──────────────────────────────────────────

class Transaction:
    def __init__(self, txn_type, amount, balance_after):
        self.txn_type = txn_type
        self.amount = amount
        self.balance_after = balance_after
        self.timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

    def to_dict(self):
        return {
            "txn_type": self.txn_type,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "timestamp": self.timestamp
        }


class BankAccount:
    def __init__(self, account_number, holder_name, password, balance=0.0):
        self.account_number = account_number
        self.holder_name = holder_name
        self.password = password
        self.balance = balance
        self.transactions = []

    def deposit(self, amount):
        if amount <= 0:
            return False, "Amount must be positive."
        self.balance += amount
        self.transactions.append(Transaction("Deposit", amount, self.balance).to_dict())
        return True, f"₹{amount:,.2f} deposited successfully."

    def withdraw(self, amount):
        if amount <= 0:
            return False, "Amount must be positive."
        if amount > self.balance:
            return False, "Insufficient balance."
        self.balance -= amount
        self.transactions.append(Transaction("Withdrawal", amount, self.balance).to_dict())
        return True, f"₹{amount:,.2f} withdrawn successfully."

    def transfer(self, amount, target_account):
        ok, msg = self.withdraw(amount)
        if not ok:
            return False, msg
        target_account.deposit(amount)
        # Replace last deposit entry with Transfer label
        target_account.transactions[-1]["txn_type"] = f"Transfer from {self.account_number}"
        self.transactions[-1]["txn_type"] = f"Transfer to {target_account.account_number}"
        return True, f"₹{amount:,.2f} transferred to {target_account.account_number}."

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "holder_name": self.holder_name,
            "password": self.password,
            "balance": self.balance,
            "transactions": self.transactions
        }


class Bank:
    DATA_FILE = "bank_data.json"

    def __init__(self):
        self.accounts = {}
        self._load()

    def _load(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE) as f:
                data = json.load(f)
            for acc_no, acc_data in data.items():
                acc = BankAccount(
                    acc_data["account_number"],
                    acc_data["holder_name"],
                    acc_data["password"],
                    acc_data["balance"]
                )
                acc.transactions = acc_data.get("transactions", [])
                self.accounts[acc_no] = acc

    def save(self):
        with open(self.DATA_FILE, "w") as f:
            json.dump({k: v.to_dict() for k, v in self.accounts.items()}, f, indent=2)

    def create_account(self, name, password, initial=0.0):
        acc_no = f"ACC{1000 + len(self.accounts) + 1}"
        acc = BankAccount(acc_no, name, password, initial)
        if initial > 0:
            acc.transactions.append(Transaction("Initial Deposit", initial, initial).to_dict())
        self.accounts[acc_no] = acc
        self.save()
        return acc_no

    def get_account(self, acc_no):
        return self.accounts.get(acc_no)

    def authenticate(self, acc_no, password):
        acc = self.get_account(acc_no)
        return acc and acc.password == password


bank = Bank()

# ──────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        password = request.form["password"]
        initial = float(request.form.get("initial", 0) or 0)
        if not name or not password:
            flash("Name and password are required.", "error")
            return redirect(url_for("register"))
        acc_no = bank.create_account(name, password, initial)
        flash(f"Account created! Your Account Number: {acc_no}", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        acc_no = request.form["acc_no"].strip().upper()
        password = request.form["password"]
        if bank.authenticate(acc_no, password):
            session["acc_no"] = acc_no
            return redirect(url_for("dashboard"))
        flash("Invalid account number or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "acc_no" not in session:
        return redirect(url_for("login"))
    acc = bank.get_account(session["acc_no"])
    recent = list(reversed(acc.transactions))[:5]
    return render_template("dashboard.html", acc=acc, recent=recent)


@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if "acc_no" not in session:
        return redirect(url_for("login"))
    acc = bank.get_account(session["acc_no"])
    if request.method == "POST":
        amount = float(request.form["amount"] or 0)
        ok, msg = acc.deposit(amount)
        bank.save()
        flash(msg, "success" if ok else "error")
        return redirect(url_for("dashboard"))
    return render_template("action.html", acc=acc, action="Deposit", icon="⬇️")


@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if "acc_no" not in session:
        return redirect(url_for("login"))
    acc = bank.get_account(session["acc_no"])
    if request.method == "POST":
        amount = float(request.form["amount"] or 0)
        ok, msg = acc.withdraw(amount)
        bank.save()
        flash(msg, "success" if ok else "error")
        return redirect(url_for("dashboard"))
    return render_template("action.html", acc=acc, action="Withdraw", icon="⬆️")


@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if "acc_no" not in session:
        return redirect(url_for("login"))
    acc = bank.get_account(session["acc_no"])
    if request.method == "POST":
        target_no = request.form["target"].strip().upper()
        amount = float(request.form["amount"] or 0)
        if target_no == acc.account_number:
            flash("Cannot transfer to your own account.", "error")
        else:
            target = bank.get_account(target_no)
            if not target:
                flash("Target account not found.", "error")
            else:
                ok, msg = acc.transfer(amount, target)
                bank.save()
                flash(msg, "success" if ok else "error")
        return redirect(url_for("dashboard"))
    return render_template("transfer.html", acc=acc)


@app.route("/history")
def history():
    if "acc_no" not in session:
        return redirect(url_for("login"))
    acc = bank.get_account(session["acc_no"])
    all_txns = list(reversed(acc.transactions))
    return render_template("history.html", acc=acc, transactions=all_txns)


if __name__ == "__main__":
    app.run(debug=True)
