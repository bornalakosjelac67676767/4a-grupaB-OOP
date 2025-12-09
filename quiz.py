#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, random
from dataclasses import dataclass, asdict, field
from abc import ABC, abstractmethod
from typing import List, Optional

# ============================================================
#                     MODEL (OOP NADOGRADNJA)
# ============================================================
@dataclass
class Pitanje(ABC):
    tekst: str
    tip: str

    @abstractmethod
    def provjeri(self, user_odgovor):
        pass

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        if d["tip"] == "TF":
            return PitanjeTF(d["tekst"], d["tocan"])
        return PitanjeMCQ(d["tekst"], d["opcije"], d["tocan_index"])


@dataclass
class PitanjeTF(Pitanje):
    tocan: bool = False

    def __init__(self, tekst, tocan):
        super().__init__(tekst, "TF")
        self.tocan = bool(tocan)

    def provjeri(self, user_odgovor):
        return (1 if self.tocan else 0) == user_odgovor


@dataclass
class PitanjeMCQ(Pitanje):
    opcije: List[str] = field(default_factory=list)
    tocan_index: int = 0

    def __init__(self, tekst, opcije, tocan_index):
        super().__init__(tekst, "MCQ")
        self.opcije = opcije
        self.tocan_index = int(tocan_index)

    def provjeri(self, user_odgovor):
        return user_odgovor == self.tocan_index


# ============================================================
#                        APLIKACIJA
# ============================================================
class KvizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kviz znanja")
        self.pitanja: List[Pitanje] = []

        # MENU
        meni = tk.Menu(root)
        help_m = tk.Menu(meni, tearoff=0)
        help_m.add_command(label="O aplikaciji", command=self.show_about)
        meni.add_cascade(label="Pomoć", menu=help_m)
        root.config(menu=meni)

        # Notebook
        self.nb = ttk.Notebook(root)
        self.editor = ttk.Frame(self.nb)
        self.kviz = ttk.Frame(self.nb)
        self.nb.add(self.editor, text="Uredi pitanja")
        self.nb.add(self.kviz, text="Igraj kviz")
        self.nb.pack(fill="both", expand=True)

        self._build_editor()
        self._build_quiz()

        self.status_var = tk.StringVar(value="Spremno.")
        ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x")

        self._load_sample()

    # INFO
    def show_about(self):
        w = tk.Toplevel(self.root)
        w.title("O aplikaciji")
        ttk.Label(w, text="Kviz znanja v1.0\nAutor: Aleksej", padding=10).pack()

    # ============================================================
    #                       EDITOR
    # ============================================================
    def _build_editor(self):
        left = ttk.Frame(self.editor)
        right = ttk.Frame(self.editor)
        left.pack(side="left", fill="both", expand=True, padx=10)
        right.pack(side="right", fill="y", padx=10)

        ttk.Label(left, text="Baza pitanja:").pack(anchor="w")

        # TREEVIEW UMJESTO LISTBOXA
        self.tree = ttk.Treeview(left, columns=("tip", "tekst"), show="headings", height=20)
        self.tree.heading("tip", text="Tip")
        self.tree.heading("tekst", text="Tekst")
        self.tree.column("tip", width=60)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_edit)

        # Buttons
        bf = ttk.Frame(left)
        bf.pack(pady=5)
        ttk.Button(bf, text="Obriši", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(bf, text="Učitaj", command=self.load_file).pack(side="left", padx=5)
        ttk.Button(bf, text="Spremi", command=self.save_file).pack(side="left", padx=5)

        # FORM
        ttk.Label(right, text="Dodaj pitanje:", font=("Arial", 11, "bold")).pack(anchor="w")

        self.qtype = tk.StringVar(value="TF")
        fr = ttk.Frame(right)
        ttk.Radiobutton(fr, text="TF", variable=self.qtype, value="TF", command=self.swap_type).pack(side="left")
        ttk.Radiobutton(fr, text="MCQ", variable=self.qtype, value="MCQ", command=self.swap_type).pack(side="left")
        fr.pack(anchor="w", pady=3)

        ttk.Label(right, text="Tekst:").pack(anchor="w")
        self.txt_tekst = tk.Text(right, width=40, height=4)
        self.txt_tekst.pack()

        # TF frame
        self.tf_frame = ttk.Frame(right)
        self.tf_val = tk.StringVar(value="True")
        ttk.Radiobutton(self.tf_frame, text="True", variable=self.tf_val, value="True").pack(side="left")
        ttk.Radiobutton(self.tf_frame, text="False", variable=self.tf_val, value="False").pack(side="left")
        self.tf_frame.pack(anchor="w")

        # MCQ frame
        self.mcq_frame = ttk.Frame(right)
        self.mcq_opts = [tk.StringVar() for _ in range(4)]
        for i, v in enumerate(self.mcq_opts):
            f = ttk.Frame(self.mcq_frame)
            ttk.Label(f, text=f"{chr(65+i)}:").pack(side="left")
            ttk.Entry(f, textvariable=v, width=25).pack(side="left")
            f.pack(anchor="w")
        self.mcq_correct = tk.IntVar(value=0)
        ttk.Spinbox(self.mcq_frame, from_=0, to=3, textvariable=self.mcq_correct, width=5).pack(anchor="w")
        self.mcq_frame.pack_forget()

        ttk.Button(right, text="Dodaj", command=self.add_q).pack(fill="x", pady=5)

    def swap_type(self):
        if self.qtype.get() == "TF":
            self.mcq_frame.pack_forget()
            self.tf_frame.pack(anchor="w")
        else:
            self.tf_frame.pack_forget()
            self.mcq_frame.pack(anchor="w")

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(self.pitanja):
            self.tree.insert("", "end", values=(p.tip, p.tekst[:60]))

    def add_q(self):
        tekst = self.txt_tekst.get("1.0", "end").strip()
        if not tekst:
            messagebox.showwarning("Greška", "Tekst je prazan.")
            return

        if self.qtype.get() == "TF":
            p = PitanjeTF(tekst, self.tf_val.get() == "True")

        else:
            opcije = [v.get().strip() for v in self.mcq_opts]
            if "" in opcije:
                messagebox.showwarning("Greška", "Sve MCQ opcije moraju biti popunjene.")
                return
            if len(set(opcije)) < 4:
                messagebox.showwarning("Greška", "Opcije se ne smiju ponavljati.")
                return
            p = PitanjeMCQ(tekst, opcije, self.mcq_correct.get())

        self.pitanja.append(p)
        self.refresh()
        self.txt_tekst.delete("1.0", "end")
        for v in self.mcq_opts: v.set("")
        self.mcq_correct.set(0)
        self.status_var.set("Dodano.")

    def on_edit(self, event):
        i = self.tree.selection()
        if not i: return
        idx = self.tree.index(i)
        p = self.pitanja[idx]
        self.nb.select(self.editor)
        self.txt_tekst.delete("1.0", "end")
        self.txt_tekst.insert("1.0", p.tekst)

        if p.tip == "TF":
            self.qtype.set("TF")
            self.swap_type()
            self.tf_val.set("True" if p.tocan else "False")
        else:
            self.qtype.set("MCQ")
            self.swap_type()
            for i, v in enumerate(self.mcq_opts):
                v.set(p.opcije[i])
            self.mcq_correct.set(p.tocan_index)

    def delete_selected(self):
        i = self.tree.selection()
        if not i: return
        idx = self.tree.index(i)
        del self.pitanja[idx]
        self.refresh()

    def save_file(self):
        if not self.pitanja:
            messagebox.showinfo("Info", "Nema pitanja.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.pitanja], f, ensure_ascii=False, indent=2)
        self.status_var.set("Spremljeno.")

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path: return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.pitanja = [Pitanje.from_dict(d) for d in data]
        self.refresh()
        self.status_var.set("Učitano.")

    # SAMPLE QUESTION
    def _load_sample(self):
        if self.pitanja: return
        self.pitanja = [
            PitanjeTF("Python je programski jezik.", True),
            PitanjeTF("Zemlja je ravna.", False),
            PitanjeMCQ("Glavni grad RH?", ["Zagreb", "Split", "Rijeka", "Osijek"], 0)
        ]
        self.refresh()

    # ============================================================
    #                       KVIZ
    # ============================================================
    def _build_quiz(self):
        top = ttk.Frame(self.kviz)
        top.pack(pady=5)

        ttk.Label(top, text="Broj pitanja:").pack(side="left")
        self.qcount = tk.IntVar(value=3)
        ttk.Spinbox(top, from_=1, to=50, textvariable=self.qcount, width=5).pack(side="left", padx=5)
        ttk.Button(top, text="Pokreni", command=self.start_quiz).pack(side="left", padx=5)

        self.area = ttk.Frame(self.kviz, padding=10)
        self.area.pack(fill="both", expand=True)

        self.qtext = tk.StringVar(value="")
        ttk.Label(self.area, textvariable=self.qtext, wraplength=600).pack(anchor="w")

        self.answer_frame = ttk.Frame(self.area)
        self.answer_frame.pack(anchor="w", pady=5)

        nav = ttk.Frame(self.kviz)
        nav.pack(pady=5)
        self.btn_prev = ttk.Button(nav, text="<<", command=self.prev, state="disabled")
        self.btn_prev.pack(side="left")
        self.btn_next = ttk.Button(nav, text=">>", command=self.next, state="disabled")
        self.btn_next.pack(side="left", padx=5)
        self.btn_end = ttk.Button(nav, text="Završi", command=self.finish, state="disabled")
        self.btn_end.pack(side="left", padx=5)

        self.quiz_info = tk.StringVar(value="")
        ttk.Label(self.kviz, textvariable=self.quiz_info).pack(anchor="w")

        self.kq = []
        self.idx = 0
        self.answers = []

    def start_quiz(self):
        if not self.pitanja:
            messagebox.showinfo("Info", "Nema pitanja.")
            return
        n = min(self.qcount.get(), len(self.pitanja))
        self.kq = random.sample(self.pitanja, n)
        self.answers = [None] * n
        self.idx = 0
        self.show_q()
        self.btn_prev.config(state="normal")
        self.btn_next.config(state="normal")
        self.btn_end.config(state="normal")

    def show_q(self):
        for w in self.answer_frame.winfo_children():
            w.destroy()

        q = self.kq[self.idx]
        self.qtext.set(f"Pitanje {self.idx+1}/{len(self.kq)}: {q.tekst}")

        if q.tip == "TF":
            var = tk.IntVar(value=-1 if self.answers[self.idx] is None else self.answers[self.idx])
            ttk.Radiobutton(self.answer_frame, text="True", variable=var, value=1,
                            command=lambda: self._save(var.get())).pack(anchor="w")
            ttk.Radiobutton(self.answer_frame, text="False", variable=var, value=0,
                            command=lambda: self._save(var.get())).pack(anchor="w")

        else:
            var = tk.IntVar(value=-1 if self.answers[self.idx] is None else self.answers[self.idx])
            for i, opt in enumerate(q.opcije):
                ttk.Radiobutton(self.answer_frame, text=f"{chr(65+i)}: {opt}", variable=var, value=i,
                                command=lambda i=i: self._save(i)).pack(anchor="w")

    def _save(self, val):
        self.answers[self.idx] = val

    def next(self):
        if self.idx < len(self.kq)-1:
            self.idx += 1
            self.show_q()

    def prev(self):
        if self.idx > 0:
            self.idx -= 1
            self.show_q()

    def finish(self):
        correct = sum(1 for q, a in zip(self.kq, self.answers) if a is not None and q.provjeri(a))
        total = len(self.kq)
        pct = correct / total * 100
        messagebox.showinfo("Rezultat", f"Točno: {correct}/{total}\n({pct:.1f}%)")
        self.quiz_info.set(f"Rezultat: {correct}/{total}")

# RUN
def main():
    r = tk.Tk()
    app = KvizApp(r)
    r.geometry("900x600")
    r.mainloop()

if __name__ == "__main__":
    main()
