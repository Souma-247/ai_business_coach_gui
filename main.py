import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pathlib import Path


class BusinessCoachApp:
    """AI Business Coach – Tkinter GUI (OOP)"""

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("AI Business Coach")
        self.master.geometry("1000x700")

        # ---- DATA HOLDERS ----
        self.df: pd.DataFrame | None = None          # full dataset
        self.filtered_df: pd.DataFrame | None = None # after filters

        # ---- GUI SECTIONS ----
        self._build_topbar()
        self._build_filter_area()
        self._build_summary_area()
        self._build_table()
        self._build_tips_area()

    # ------------------------------------------------------------------ #
    #                       GUI BUILDING HELPERS                          #
    # ------------------------------------------------------------------ #

    def _build_topbar(self) -> None:
        top = ttk.Frame(self.master, padding=5)
        top.pack(fill="x")

        ttk.Button(top, text="Load CSV", command=self.load_csv).pack(side="left")
        ttk.Button(top, text="Apply Filters", command=self.apply_filters).pack(side="left")

        self.file_label = ttk.Label(top, text="No file loaded")
        self.file_label.pack(side="left", padx=10)

    def _build_filter_area(self) -> None:
        filt = ttk.LabelFrame(self.master, text="Filters", padding=10)
        filt.pack(fill="x", padx=5, pady=5)

        # Date range
        ttk.Label(filt, text="Start date (YYYY‑MM‑DD):").grid(row=0, column=0, sticky="w")
        ttk.Label(filt, text="End date (YYYY‑MM‑DD):").grid(row=0, column=2, sticky="w")
        self.start_date = ttk.Entry(filt, width=12)
        self.end_date = ttk.Entry(filt, width=12)
        self.start_date.grid(row=0, column=1, padx=5)
        self.end_date.grid(row=0, column=3, padx=5)

        # Category multiselect
        ttk.Label(filt, text="Categories:").grid(row=1, column=0, sticky="nw", pady=(8, 0))
        self.cat_listbox = tk.Listbox(filt, selectmode="multiple", height=5, exportselection=False)
        self.cat_listbox.grid(row=1, column=1, columnspan=3, sticky="we", pady=(8, 0))

    def _build_summary_area(self) -> None:
        sumf = ttk.Frame(self.master, padding=10)
        sumf.pack(fill="x")

        self.income_var = tk.StringVar(value="₦0")
        self.expense_var = tk.StringVar(value="₦0")
        self.balance_var = tk.StringVar(value="₦0")

        ttk.Label(sumf, text="Total Income:").grid(row=0, column=0, sticky="e")
        ttk.Label(sumf, textvariable=self.income_var, foreground="green").grid(row=0, column=1, sticky="w")

        ttk.Label(sumf, text="Total Expenses:").grid(row=0, column=2, sticky="e", padx=(20, 0))
        ttk.Label(sumf, textvariable=self.expense_var, foreground="red").grid(row=0, column=3, sticky="w")

        ttk.Label(sumf, text="Net Balance:").grid(row=0, column=4, sticky="e", padx=(20, 0))
        ttk.Label(sumf, textvariable=self.balance_var, foreground="blue").grid(row=0, column=5, sticky="w")

    def _build_table(self) -> None:
        table_frame = ttk.Frame(self.master)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        columns = ("Date", "Type", "Amount", "Category", "Description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

    def _build_tips_area(self) -> None:
        tips_frame = ttk.LabelFrame(self.master, text="Smart Financial Tips", padding=10)
        tips_frame.pack(fill="x", padx=5, pady=5)
        self.tips_var = tk.StringVar(value="Load a CSV and apply filters to see tips.")
        self.tips_label = ttk.Label(tips_frame, textvariable=self.tips_var, wraplength=900, justify="left")
        self.tips_label.pack(anchor="w")

    # ------------------------------------------------------------------ #
    #                            FUNCTIONALITY                           #
    # ------------------------------------------------------------------ #

    def load_csv(self) -> None:
        """Open file dialog, load CSV into DataFrame, populate UI."""
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv")]
        )
        if not file_path:
            return

        try:
            self.df = pd.read_csv(file_path)
            self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")
            self.df["Amount"] = pd.to_numeric(self.df["Amount"], errors="coerce")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load CSV:\n{e}")
            return

        self.file_label.config(text=Path(file_path).name)

        # Fill category listbox
        self.cat_listbox.delete(0, "end")
        for cat in sorted(self.df["Category"].dropna().unique()):
            self.cat_listbox.insert("end", cat)
            self.cat_listbox.selection_set("end")  # select all by default

        self.filtered_df = self.df.copy()
        self.refresh_table()
        self.refresh_summary()
        self.refresh_tips()

    def apply_filters(self) -> None:
        """Filter DataFrame by date range and selected categories."""
        if self.df is None:
            messagebox.showinfo("Info", "Load a CSV first.")
            return

        # Date range
        try:
            sd = pd.to_datetime(self.start_date.get()) if self.start_date.get() else self.df["Date"].min()
            ed = pd.to_datetime(self.end_date.get()) if self.end_date.get() else self.df["Date"].max()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY‑MM‑DD.")
            return

        # Categories
        selected_indices = self.cat_listbox.curselection()
        selected_cats = {self.cat_listbox.get(i) for i in selected_indices} if selected_indices else set(self.df["Category"].unique())

        self.filtered_df = self.df[
            (self.df["Date"].between(sd, ed)) &
            (self.df["Category"].isin(selected_cats))
        ]
        self.refresh_table()
        self.refresh_summary()
        self.refresh_tips()

    def refresh_table(self) -> None:
        """Clear and repopulate the Treeview with filtered data."""
        self.tree.delete(*self.tree.get_children())
        if self.filtered_df is None or self.filtered_df.empty:
            return

        for _, row in self.filtered_df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def refresh_summary(self) -> None:
        """Update KPI labels based on filtered data."""
        if self.filtered_df is None or self.filtered_df.empty:
            self.income_var.set("₦0")
            self.expense_var.set("₦0")
            self.balance_var.set("₦0")
            return

        total_income = self.filtered_df[self.filtered_df["Type"] == "Income"]["Amount"].sum()
        total_expense = self.filtered_df[self.filtered_df["Type"] == "Expense"]["Amount"].sum()
        balance = total_income - total_expense

        self.income_var.set(f"₦{total_income:,.0f}")
        self.expense_var.set(f"₦{total_expense:,.0f}")
        self.balance_var.set(f"₦{balance:,.0f}")

    def refresh_tips(self) -> None:
        """Generate and display smart financial tips."""
        if self.filtered_df is None or self.filtered_df.empty:
            self.tips_var.set("No data to analyze.")
            return

        tips = []

        # Tip 1: Dominant category (>50% expenses)
        expense_df = self.filtered_df[self.filtered_df["Type"] == "Expense"]
        if not expense_df.empty:
            cat_sum = expense_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            top_cat = cat_sum.idxmax()
            if cat_sum.iloc[0] > 0.5 * cat_sum.sum():
                tips.append(f"⚠️ Over 50% of your expenses went to **{top_cat}**. Consider cutting back.")

        # Tip 2: Saving rate <20%
        total_income = self.filtered_df[self.filtered_df["Type"] == "Income"]["Amount"].sum()
        total_expense = self.filtered_df[self.filtered_df["Type"] == "Expense"]["Amount"].sum()
        balance = total_income - total_expense
        if total_income > 0 and balance / total_income < 0.2:
            tips.append("💡 Your saving rate is below 20%. Try to save more each month.")

        # Positive encouragement
        tips.append("✅ Great job tracking your transactions! Keep it up!")

        self.tips_var.set("\n".join(tips))


# ------------------------------------------------------------------ #
#                          RUN THE APP                               #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    root = tk.Tk()
    app = BusinessCoachApp(root)
    root.mainloop()
