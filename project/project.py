import sqlite3
from tkinter import *
from tkinter import messagebox

# ---------------------- Database Setup ----------------------
conn = sqlite3.connect("bank_transactions.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_no TEXT NOT NULL,
    holder_name TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    balance REAL NOT NULL,
    date TEXT NOT NULL
)
""")
conn.commit()

# ---------------------- Helper Function ----------------------
def get_balance(account_no):
    cursor.execute("SELECT balance FROM transactions WHERE account_no=? ORDER BY id DESC LIMIT 1", (account_no,))
    row = cursor.fetchone()
    return row[0] if row else 0.0

# ---------------------- Main Functions ----------------------
def deposit_money():
    acc_no = entry_acc.get()
    name = entry_name.get()
    amount = entry_amt.get()
    date = entry_date.get()

    if not all([acc_no, name, amount, date]):
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    try:
        amount = float(amount)
    except:
        messagebox.showerror("Error", "Amount must be numeric.")
        return

    balance = get_balance(acc_no) + amount
    cursor.execute("""
        INSERT INTO transactions (account_no, holder_name, transaction_type, amount, balance, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (acc_no, name, "Deposit", amount, balance, date))
    conn.commit()
    messagebox.showinfo("Success", f"₹{amount} deposited successfully!\nNew Balance: ₹{balance}")
    clear_fields()

def withdraw_money():
    acc_no = entry_acc.get()
    name = entry_name.get()
    amount = entry_amt.get()
    date = entry_date.get()

    if not all([acc_no, name, amount, date]):
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    try:
        amount = float(amount)
    except:
        messagebox.showerror("Error", "Amount must be numeric.")
        return

    current_balance = get_balance(acc_no)
    if amount > current_balance:
        messagebox.showerror("Insufficient Funds", f"Your balance is ₹{current_balance}")
        return

    new_balance = current_balance - amount
    cursor.execute("""
        INSERT INTO transactions (account_no, holder_name, transaction_type, amount, balance, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (acc_no, name, "Withdrawal", amount, new_balance, date))
    conn.commit()
    messagebox.showinfo("Success", f"₹{amount} withdrawn successfully!\nNew Balance: ₹{new_balance}")
    clear_fields()

def check_balance():
    acc_no = entry_acc.get()
    if acc_no == "":
        messagebox.showwarning("Input Error", "Please enter account number.")
        return
    balance = get_balance(acc_no)
    messagebox.showinfo("Account Balance", f"Account No: {acc_no}\nCurrent Balance: ₹{balance}")

# ---------------------- View Transactions ----------------------
def view_transactions():
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
    rows = cursor.fetchall()

    view_window = Toplevel(root)
    view_window.title("All Transactions")
    view_window.geometry("950x550")
    view_window.config(bg="#E8F5E9")

    Label(view_window, text="All Transactions", font=("Poppins", 20, "bold"),
          bg="#E8F5E9", fg="#2E7D32").pack(pady=10)

    if not rows:
        Label(view_window, text="No transactions found.", bg="#E8F5E9", font=("Poppins", 14)).pack()
        return

    # Scrollable Frame
    canvas = Canvas(view_window, bg="#E8F5E9", highlightthickness=0)
    scrollbar = Scrollbar(view_window, orient=VERTICAL, command=canvas.yview)
    scroll_frame = Frame(canvas, bg="#E8F5E9")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=LEFT, fill="both", expand=True, padx=10)
    scrollbar.pack(side=RIGHT, fill="y")

    for i, row in enumerate(rows):
        frame = Frame(scroll_frame, bg="#F1F8E9", bd=1, relief="solid")
        frame.pack(fill="x", padx=15, pady=6)

        Label(frame, text=f"{i+1}. {row[2]} | Acc: {row[1]} | {row[3]} ₹{row[4]} | Bal: ₹{row[5]} | Date: {row[6]}",
              font=("Poppins", 11), bg="#F1F8E9", anchor="w").pack(side=LEFT, padx=10, pady=8, fill="x", expand=True)

        Button(frame, text="Update", bg="#D4A373", fg="black", font=("Poppins", 9, "bold"), width=10,
               command=lambda rid=row[0]: update_transaction(rid)).pack(side=RIGHT, padx=5)
        Button(frame, text="Delete", bg="#A52A2A", fg="white", font=("Poppins", 9, "bold"), width=10,
               command=lambda rid=row[0], vw=view_window: delete_transaction(rid, vw)).pack(side=RIGHT, padx=5)

def delete_transaction(trans_id, view_window):
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?")
    if confirm:
        cursor.execute("DELETE FROM transactions WHERE id=?", (trans_id,))
        conn.commit()
        messagebox.showinfo("Deleted", "Transaction deleted successfully.")
        view_window.destroy()
        view_transactions()

def update_transaction(trans_id):
    cursor.execute("SELECT * FROM transactions WHERE id=?", (trans_id,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("Error", "Transaction not found.")
        return

    update_win = Toplevel(root)
    update_win.title("Update Transaction")
    update_win.geometry("400x400")
    update_win.config(bg="#FAEED1")

    Label(update_win, text="Update Transaction", font=("Poppins", 18, "bold"),
          bg="#5B3A29", fg="white", pady=10).pack(fill=X)

    labels = ["Transaction Type:", "Amount (₹):", "Date (YYYY-MM-DD):"]
    entries = []

    trans_type_var = StringVar(value=row[3])
    amount_entry = Entry(update_win, width=30, font=("Poppins", 12))
    date_entry = Entry(update_win, width=30, font=("Poppins", 12))

    # Fill with current data
    amount_entry.insert(0, row[4])
    date_entry.insert(0, row[6])

    Label(update_win, text="Transaction Type:", bg="#FAEED1", font=("Poppins", 12)).pack(pady=5)
    OptionMenu(update_win, trans_type_var, "Deposit", "Withdrawal").pack(pady=5)
    Label(update_win, text="Amount (₹):", bg="#FAEED1", font=("Poppins", 12)).pack(pady=5)
    amount_entry.pack(pady=5)
    Label(update_win, text="Date (YYYY-MM-DD):", bg="#FAEED1", font=("Poppins", 12)).pack(pady=5)
    date_entry.pack(pady=5)

    def save_update():
        try:
            amt = float(amount_entry.get())
        except:
            messagebox.showerror("Error", "Amount must be numeric.")
            return

        new_type = trans_type_var.get()
        new_date = date_entry.get()
        cursor.execute("""
            UPDATE transactions
            SET transaction_type=?, amount=?, date=?
            WHERE id=?
        """, (new_type, amt, new_date, trans_id))
        conn.commit()
        messagebox.showinfo("Updated", "Transaction updated successfully!")
        update_win.destroy()
        view_transactions()

    Button(update_win, text="Save Changes", bg="#8B5E3C", fg="white",
           font=("Poppins", 12, "bold"), width=20, command=save_update).pack(pady=20)

def clear_fields():
    entry_acc.delete(0, END)
    entry_name.delete(0, END)
    entry_amt.delete(0, END)
    entry_date.delete(0, END)

# ---------------------- GUI Setup ----------------------
root = Tk()
root.title("BankEase ATM System")
root.geometry("600x720")
root.config(bg="#E8F5E9")

Label(root, text="🏦 BankEase ATM System", font=("Poppins", 22, "bold"),
      bg="#2E7D32", fg="white", pady=15).pack(fill=X)

Label(root, text="Enter Transaction Details Below", font=("Poppins", 13),
      bg="#E8F5E9", fg="#1B5E20").pack(pady=10)

entry_acc = Entry(root, width=40, font=("Poppins", 12))
entry_name = Entry(root, width=40, font=("Poppins", 12))
entry_amt = Entry(root, width=40, font=("Poppins", 12))
entry_date = Entry(root, width=40, font=("Poppins", 12))

fields = [
    ("Account Number:", entry_acc),
    ("Account Holder Name:", entry_name),
    ("Amount:", entry_amt),
    ("Date (YYYY-MM-DD):", entry_date)
]

for label, widget in fields:
    Label(root, text=label, font=("Poppins", 12, "bold"), bg="#E8F5E9", fg="#1B5E20").pack()
    widget.pack(pady=4)

Button(root, text="Deposit", command=deposit_money, bg="#43A047", fg="white",
       font=("Poppins", 13, "bold"), width=25).pack(pady=10)
Button(root, text="Withdraw", command=withdraw_money, bg="#F57C00", fg="white",
       font=("Poppins", 13, "bold"), width=25).pack(pady=10)
Button(root, text="Check Balance", command=check_balance, bg="#1976D2", fg="white",
       font=("Poppins", 13, "bold"), width=25).pack(pady=10)
Button(root, text="View All Transactions", command=view_transactions, bg="#C0CA33", fg="black",
       font=("Poppins", 13, "bold"), width=25).pack(pady=10)
Button(root, text="Clear Fields", command=clear_fields, bg="#A1887F", fg="white",
       font=("Poppins", 13, "bold"), width=25).pack(pady=10)

root.mainloop()
