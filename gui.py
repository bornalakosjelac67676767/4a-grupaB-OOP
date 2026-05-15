import tkinter as tk
import database as db
import analytics as an
import ai
import heatmap
import charts

# 🎨 COLORS (NASA / DARK MODE)
BG = "#0b0f17"
FG = "#d6e4ff"
ACCENT = "#4cc9f0"
CARD = "#151a24"


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AEGIS GRID CONTROL CENTER")
        self.root.configure(bg=BG)

        # 📌 TITLE
        self.title = tk.Label(
            root,
            text="AEGIS GRID • CONTROL CENTER",
            bg=BG,
            fg=ACCENT,
            font=("Arial", 18, "bold")
        )
        self.title.pack(pady=10)

        # 📊 TEXT AREA
        self.text = tk.Text(
            root,
            width=110,
            height=25,
            bg=CARD,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=("Consolas", 10)
        )
        self.text.pack(padx=20, pady=10)

        # 🎛 BUTTON AREA
        self.btn_frame = tk.Frame(root, bg=BG)
        self.btn_frame.pack(pady=10)

        self.btn_style("📡 Podaci", self.load)
        self.btn_style("⚠ Anomalije", self.anom)
        self.btn_style("📊 Prosjek CO2", self.avg)
        self.btn_style("🤖 AI predikcija", self.pred)
        self.btn_style("🌍 Heatmap", heatmap.show_heatmap)
        self.btn_style("📈 Graf", charts.show_chart)
        self.btn_style("🏙 Status grada", self.city_status)

        # 🔄 LIVE UPDATE
        self.live_update()

    # 🎨 BUTTON STYLE
    def btn_style(self, text, command):
        btn = tk.Button(
            self.btn_frame,
            text=text,
            command=command,
            bg=CARD,
            fg=FG,
            activebackground=ACCENT,
            activeforeground="black",
            relief="flat",
            padx=12,
            pady=6,
            font=("Arial", 10)
        )

        btn.bind("<Enter>", lambda e: btn.config(bg="#222a3a"))
        btn.bind("<Leave>", lambda e: btn.config(bg=CARD))

        btn.pack(side="left", padx=6)

    # 📡 LOAD DATA
    def load(self):
        self.text.delete("1.0", tk.END)
        data = db.dohvati_podatke()

        for row in data:
            self.text.insert(tk.END, str(row) + "\n")

    # ⚠ ANOMALIES
    def anom(self):
        self.text.delete("1.0", tk.END)
        data = an.anomalije()

        for row in data:
            self.text.insert(tk.END, "⚠ " + str(row) + "\n")

    # 📊 AVG
    def avg(self):
        self.text.delete("1.0", tk.END)
        avg = an.prosjek("CO2")
        self.text.insert(tk.END, f"CO2 PROSJEK: {avg:.2f}")

    # 🤖 AI
    def pred(self):
        self.text.delete("1.0", tk.END)
        pred = ai.predict_co2()
        self.text.insert(tk.END, f"AI PREDIKCIJA CO2: {pred}")

    # 🏙 CITY STATUS
    def city_status(self):
        data = db.dohvati_podatke()

        if not data:
            status = "🟢 STABLE"
        else:
            avg = sum([x[4] for x in data]) / len(data)

            if avg < 70:
                status = "🟢 STABLE"
            elif avg < 130:
                status = "🟡 WARNING"
            else:
                status = "🔴 DANGER"

        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, f"CITY STATUS: {status}")

    # 🔄 LIVE UPDATE
    def live_update(self):
        try:
            self.load()
        except:
            pass

        self.root.after(4000, self.live_update)