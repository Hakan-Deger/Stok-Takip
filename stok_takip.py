import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stok Takip Sistemi")
        self.root.geometry("1100x680")
        self.root.minsize(980, 620)
        self.root.configure(bg="#f4f6f8")

        self.db_connection = sqlite3.connect("stock.db")
        self.create_table()

        self.products = {}
        self.load_data_from_db()

        self.setup_styles()
        self.create_ui()
        self.refresh_table()
        self.update_summary_cards()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Card.TFrame", background="white")
        style.configure("Header.TLabel", font=(
            "Segoe UI", 18, "bold"), background="#f4f6f8", foreground="#1f2937")
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10),
                        background="#f4f6f8", foreground="#6b7280")
        style.configure("SectionTitle.TLabel", font=(
            "Segoe UI", 11, "bold"), background="white", foreground="#111827")
        style.configure("Info.TLabel", font=("Segoe UI", 10),
                        background="white", foreground="#374151")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Accent.TButton", font=(
            "Segoe UI", 10, "bold"), padding=8)

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            quantity INTEGER NOT NULL,
            min_stock INTEGER NOT NULL
        )
        """
        self.db_connection.execute(query)
        self.db_connection.commit()

    def load_data_from_db(self):
        self.products.clear()
        cursor = self.db_connection.execute(
            "SELECT name, quantity, min_stock FROM products ORDER BY name")
        for name, quantity, min_stock in cursor.fetchall():
            self.products[name] = {
                "quantity": quantity, "min_stock": min_stock}

    def save_data_to_db(self):
        cursor = self.db_connection.cursor()
        cursor.execute("DELETE FROM products")
        for product, data in self.products.items():
            cursor.execute(
                "INSERT INTO products (name, quantity, min_stock) VALUES (?, ?, ?)",
                (product, data["quantity"], data["min_stock"]),
            )
        self.db_connection.commit()

    def create_ui(self):
        container = tk.Frame(self.root, bg="#f4f6f8", padx=18, pady=18)
        container.pack(fill="both", expand=True)

        header_frame = tk.Frame(container, bg="#f4f6f8")
        header_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(header_frame, text="Stok Takip Paneli",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header_frame,
            text="Ürün ekleyin, stok azaltın, düşük stokları takip edin ve kayıtları tablo üzerinden yönetin.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        summary_frame = tk.Frame(container, bg="#f4f6f8")
        summary_frame.pack(fill="x", pady=(0, 14))

        self.total_products_var = tk.StringVar(value="0")
        self.total_stock_var = tk.StringVar(value="0")
        self.low_stock_var = tk.StringVar(value="0")

        self.create_summary_card(summary_frame, "Toplam Ürün", self.total_products_var).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        self.create_summary_card(summary_frame, "Toplam Stok", self.total_stock_var).pack(
            side="left", fill="x", expand=True, padx=8)
        self.create_summary_card(summary_frame, "Kritik Stok", self.low_stock_var).pack(
            side="left", fill="x", expand=True, padx=(8, 0))

        body = tk.Frame(container, bg="#f4f6f8")
        body.pack(fill="both", expand=True)

        left_panel = ttk.Frame(body, style="Card.TFrame", padding=16)
        left_panel.pack(side="left", fill="y", padx=(0, 12))
        left_panel.configure(width=320)
        left_panel.pack_propagate(False)

        right_panel = ttk.Frame(body, style="Card.TFrame", padding=16)
        right_panel.pack(side="left", fill="both", expand=True)

        self.build_left_panel(left_panel)
        self.build_right_panel(right_panel)

    def create_summary_card(self, parent, title, variable):
        frame = tk.Frame(parent, bg="white", bd=0,
                         highlightthickness=1, highlightbackground="#e5e7eb")
        tk.Label(frame, text=title, font=("Segoe UI", 10), bg="white",
                 fg="#6b7280", padx=16, pady=10).pack(anchor="w")
        tk.Label(frame, textvariable=variable, font=("Segoe UI", 18, "bold"),
                 bg="white", fg="#111827", padx=16).pack(anchor="w", pady=(0, 14))
        return frame

    def build_left_panel(self, parent):
        ttk.Label(parent, text="Ürün İşlemleri",
                  style="SectionTitle.TLabel").pack(anchor="w")

        form = tk.Frame(parent, bg="white")
        form.pack(fill="x", pady=(12, 18))

        self.entry_name = self.create_labeled_entry(form, "Ürün Adı")
        self.entry_quantity = self.create_labeled_entry(form, "Stok Miktarı")
        self.entry_min_stock = self.create_labeled_entry(form, "Minimum Stok")

        button_row = tk.Frame(parent, bg="white")
        button_row.pack(fill="x", pady=(0, 20))

        ttk.Button(button_row, text="Ürün Ekle / Güncelle", style="Accent.TButton",
                   command=self.add_product).pack(fill="x", pady=(0, 8))
        ttk.Button(button_row, text="Formu Temizle",
                   command=self.clear_form).pack(fill="x")

        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=8)

        ttk.Label(parent, text="Stok Azalt", style="SectionTitle.TLabel").pack(
            anchor="w", pady=(10, 0))
        self.entry_decrease_name = self.create_labeled_entry(
            parent, "Ürün Adı")
        self.entry_decrease_amount = self.create_labeled_entry(
            parent, "Azaltma Miktarı")
        ttk.Button(parent, text="Stok Azalt", command=self.decrease_stock).pack(
            fill="x", pady=(8, 0))

        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=16)

        ttk.Label(parent, text="Seçili Kayıt",
                  style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Button(parent, text="Seçili Ürünü Sil",
                   command=self.delete_selected_product).pack(fill="x", pady=(10, 6))
        ttk.Button(parent, text="Verileri Kaydet",
                   command=self.save_and_notify).pack(fill="x")

    def build_right_panel(self, parent):
        top_bar = tk.Frame(parent, bg="white")
        top_bar.pack(fill="x")

        ttk.Label(top_bar, text="Ürün Listesi",
                  style="SectionTitle.TLabel").pack(side="left")

        search_wrap = tk.Frame(top_bar, bg="white")
        search_wrap.pack(side="right")
        tk.Label(search_wrap, text="Ara:", font=("Segoe UI", 10),
                 bg="white", fg="#374151").pack(side="left", padx=(0, 6))

        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self.refresh_table())
        self.entry_filter = ttk.Entry(
            search_wrap, textvariable=self.filter_var, width=26)
        self.entry_filter.pack(side="left")

        columns = ("name", "quantity", "min_stock", "status")
        self.tree = ttk.Treeview(
            parent, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Ürün")
        self.tree.heading("quantity", text="Stok")
        self.tree.heading("min_stock", text="Min. Stok")
        self.tree.heading("status", text="Durum")

        self.tree.column("name", width=240)
        self.tree.column("quantity", width=90, anchor="center")
        self.tree.column("min_stock", width=100, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=(14, 0))
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)
        self.tree.bind("<Double-1>", self.fill_form_from_selected)

        self.tree.tag_configure(
            "low_stock", background="#fee2e2", foreground="#991b1b")
        self.tree.tag_configure(
            "normal_stock", background="#ecfdf5", foreground="#065f46")

        info = tk.Label(
            parent,
            text="İpucu: Satıra çift tıklayarak bilgileri sol taraftaki forma taşıyabilirsiniz.",
            font=("Segoe UI", 9),
            bg="white",
            fg="#6b7280",
            anchor="w",
        )
        info.pack(fill="x", pady=(10, 0))

    def create_labeled_entry(self, parent, label_text):
        wrapper = tk.Frame(parent, bg="white")
        wrapper.pack(fill="x", pady=(8, 0))
        tk.Label(wrapper, text=label_text, font=("Segoe UI", 10),
                 bg="white", fg="#374151").pack(anchor="w", pady=(0, 4))
        entry = ttk.Entry(wrapper)
        entry.pack(fill="x")
        return entry

    def validate_non_negative_int(self, value, field_name):
        try:
            number = int(value)
            if number < 0:
                raise ValueError
            return number
        except ValueError:
            raise ValueError(
                f"{field_name} alanına 0 veya daha büyük bir sayı girin.")

    def add_product(self):
        product_name = self.entry_name.get().strip()
        if not product_name:
            messagebox.showerror("Hata", "Ürün adı boş bırakılamaz.")
            return

        try:
            quantity = self.validate_non_negative_int(
                self.entry_quantity.get().strip(), "Stok miktarı")
            min_stock = self.validate_non_negative_int(
                self.entry_min_stock.get().strip(), "Minimum stok")
        except ValueError as exc:
            messagebox.showerror("Hata", str(exc))
            return

        if product_name in self.products:
            self.products[product_name]["quantity"] += quantity
            self.products[product_name]["min_stock"] = min_stock
            messagebox.showinfo("Başarılı", f"{product_name} güncellendi.")
        else:
            self.products[product_name] = {
                "quantity": quantity, "min_stock": min_stock}
            messagebox.showinfo("Başarılı", f"{product_name} eklendi.")

        self.clear_form()
        self.refresh_after_change()

    def decrease_stock(self):
        product_name = self.entry_decrease_name.get().strip()
        if not product_name:
            messagebox.showerror("Hata", "Lütfen ürün adını girin.")
            return

        try:
            decrease_amount = self.validate_non_negative_int(
                self.entry_decrease_amount.get().strip(), "Azaltma miktarı")
        except ValueError as exc:
            messagebox.showerror("Hata", str(exc))
            return

        if product_name not in self.products:
            messagebox.showerror("Hata", f"{product_name} bulunamadı.")
            return

        if self.products[product_name]["quantity"] < decrease_amount:
            messagebox.showerror(
                "Hata", f"{product_name} için yeterli stok yok.")
            return

        self.products[product_name]["quantity"] -= decrease_amount
        messagebox.showinfo("Başarılı", f"{product_name} stoğu azaltıldı.")
        self.entry_decrease_amount.delete(0, tk.END)
        self.refresh_after_change()

    def delete_selected_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Lütfen silmek için bir ürün seçin.")
            return

        product_name = self.tree.item(selected[0], "values")[0]
        if messagebox.askyesno("Onay", f"{product_name} adlı ürünü silmek istiyor musunuz?"):
            self.products.pop(product_name, None)
            self.refresh_after_change()
            messagebox.showinfo("Başarılı", f"{product_name} silindi.")

    def fill_form_from_selected(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        name, quantity, min_stock, _status = self.tree.item(
            selected[0], "values")
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, name)
        self.entry_quantity.delete(0, tk.END)
        self.entry_quantity.insert(0, str(quantity))
        self.entry_min_stock.delete(0, tk.END)
        self.entry_min_stock.insert(0, str(min_stock))

    def on_row_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        name = self.tree.item(selected[0], "values")[0]
        self.entry_decrease_name.delete(0, tk.END)
        self.entry_decrease_name.insert(0, name)

    def clear_form(self):
        for entry in (self.entry_name, self.entry_quantity, self.entry_min_stock):
            entry.delete(0, tk.END)

    def get_filtered_products(self):
        filter_text = self.filter_var.get().strip().lower()
        items = sorted(self.products.items(), key=lambda x: x[0].lower())
        if not filter_text:
            return items
        return [(product, data) for product, data in items if filter_text in product.lower()]

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for product, data in self.get_filtered_products():
            is_low = data["quantity"] < data["min_stock"]
            status = "Kritik" if is_low else "Normal"
            tag = "low_stock" if is_low else "normal_stock"
            self.tree.insert("", "end", values=(
                product, data["quantity"], data["min_stock"], status), tags=(tag,))

    def update_summary_cards(self):
        total_products = len(self.products)
        total_stock = sum(data["quantity"] for data in self.products.values())
        low_stock_count = sum(1 for data in self.products.values(
        ) if data["quantity"] < data["min_stock"])

        self.total_products_var.set(str(total_products))
        self.total_stock_var.set(str(total_stock))
        self.low_stock_var.set(str(low_stock_count))

    def refresh_after_change(self):
        self.refresh_table()
        self.update_summary_cards()

    def save_and_notify(self):
        self.save_data_to_db()
        messagebox.showinfo(
            "Kaydedildi", "Tüm veriler veritabanına kaydedildi.")

    def on_close(self):
        try:
            self.save_data_to_db()
        finally:
            self.db_connection.close()
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
