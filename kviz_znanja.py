#!/usr/bin/env python3
"""
Kviz znanja - Desktop aplikacija (Tkinter)
Funkcionalnosti:
- Dodavanje PitanjeTF (True/False)
- Dodavanje PitanjeMCQ (4 odgovora)
- Prikaz pitanja u Listbox-u (oznaka tipa)
- Brisanje pitanja
- Spremanje i učitavanje baze pitanja (JSON)
- Pokretanje kviza s nasumično odabranim pitanjima i bodovanjem
- Prikaz rezultata (točni, postotak)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import random
from dataclasses import dataclass, asdict, field
from typing import List, Optional

# ========== Model ==========
@dataclass
class Pitanje:
    tekst: str
    tip: str  # "TF" ili "MCQ"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        tip = d.get("tip")
        if tip == "TF":
            return PitanjeTF(tekst=d["tekst"], tocan=d["tocan"])
        elif tip == "MCQ":
            return PitanjeMCQ(tekst=d["tekst"], opcije=d["opcije"], tocan_index=d["tocan_index"])
        else:
            raise ValueError("Nepoznati tip pitanja")


@dataclass
class PitanjeTF(Pitanje):
    tocan: bool = False

    def __init__(self, tekst: str, tocan: bool):
        super().__init__(tekst=tekst, tip="TF")
        self.tocan = tocan

    def __str__(self):
        return f"[T/F] {self.tekst} (Točno: {'True' if self.tocan else 'False'})"


@dataclass
class PitanjeMCQ(Pitanje):
    opcije: List[str] = field(default_factory=list)
    tocan_index: int = 0

    def __init__(self, tekst: str, opcije: List[str], tocan_index: int):
        super().__init__(tekst=tekst, tip="MCQ")
        if len(opcije) != 4:
            raise ValueError("MCQ mora imati točno 4 opcije")
        self.opcije = opcije
        self.tocan_index = int(tocan_index)

    def __str__(self):
        return f"[MCQ] {self.tekst} (A) {self.opcije[0]} (B) {self.opcije[1]} (C) {self.opcije[2]} (D) {self.opcije[3]} (Točno: {chr(65+self.tocan_index)})"


# ========== Application ==========
class KvizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kviz znanja")
        self.pitanja: List[Pitanje] = []

        # Main layout: notebook with two tabs: Editor i Kviz
        self.notebook = ttk.Notebook(root)
        self.frame_editor = ttk.Frame(self.notebook)
        self.frame_quiz = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_editor, text="Uredi bazu pitanja")
        self.notebook.add(self.frame_quiz, text="Igraj kviz")
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_editor()
        self._build_quiz()

        # status bar
        self.status_var = tk.StringVar(value="Dobrodošli u Kviz znanja!")
        status = ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w")
        status.pack(fill="x", side="bottom")

        # sample questions
        self._load_sample_questions()

    # ========== Editor tab ==========
    def _build_editor(self):
        left = ttk.Frame(self.frame_editor)
        right = ttk.Frame(self.frame_editor)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))
        right.pack(side="right", fill="y")

        # Listbox for questions
        lbl = ttk.Label(left, text="Baza pitanja:")
        lbl.pack(anchor="w")
        self.lb_pitanja = tk.Listbox(left, height=20)
        self.lb_pitanja.pack(fill="both", expand=True)
        self.lb_pitanja.bind("<Double-1>", self.on_edit_selected)

        # Buttons under listbox
        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill="x", pady=6)
        ttk.Button(btn_frame, text="Obriši odabrano", command=self.delete_selected).pack(side="left")
        ttk.Button(btn_frame, text="Učitaj iz datoteke", command=self.load_from_file).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Spremi u datoteku", command=self.save_to_file).pack(side="left")

        # Right side: form for adding questions
        form_lbl = ttk.Label(right, text="Dodaj novo pitanje", font=("TkDefaultFont", 11, "bold"))
        form_lbl.pack(anchor="w", pady=(0,6))

        # Tip pitanja radiobuttons
        self.qtype = tk.StringVar(value="TF")
        type_frame = ttk.Frame(right)
        ttk.Radiobutton(type_frame, text="True/False", value="TF", variable=self.qtype, command=self.on_qtype_change).pack(side="left")
        ttk.Radiobutton(type_frame, text="Multiple Choice", value="MCQ", variable=self.qtype, command=self.on_qtype_change).pack(side="left", padx=8)
        type_frame.pack(fill="x", pady=(0,6))

        # Common: tekst
        ttk.Label(right, text="Tekst pitanja:").pack(anchor="w")
        self.entry_tekst = tk.Text(right, width=40, height=4)
        self.entry_tekst.pack()

        # TF controls
        self.tf_frame = ttk.Frame(right)
        ttk.Label(self.tf_frame, text="Točan odgovor:").pack(anchor="w")
        self.tf_answer = tk.StringVar(value="True")
        ttk.Radiobutton(self.tf_frame, text="True", value="True", variable=self.tf_answer).pack(side="left")
        ttk.Radiobutton(self.tf_frame, text="False", value="False", variable=self.tf_answer).pack(side="left", padx=6)
        self.tf_frame.pack(fill="x", pady=6)

        # MCQ controls
        self.mcq_frame = ttk.Frame(right)
        ttk.Label(self.mcq_frame, text="Opcije (točno označi):").pack(anchor="w")
        self.option_vars = [tk.StringVar() for _ in range(4)]
        for i, var in enumerate(self.option_vars):
            row = ttk.Frame(self.mcq_frame)
            ttk.Label(row, text=f"{chr(65+i)}:").pack(side="left")
            ttk.Entry(row, textvariable=var, width=30).pack(side="left", padx=4)
            row.pack(anchor="w", pady=2)
        ttk.Label(self.mcq_frame, text="Index točnog odgovora (0=A,1=B,2=C,3=D):").pack(anchor="w", pady=(6,0))
        self.mcq_correct = tk.IntVar(value=0)
        ttk.Spinbox(self.mcq_frame, from_=0, to=3, textvariable=self.mcq_correct, width=5).pack(anchor="w")
        # default hide MCQ frame
        self.mcq_frame.pack_forget()

        # Add button
        ttk.Button(right, text="Dodaj pitanje", command=self.add_question).pack(pady=8, fill="x")

        # Populate listbox initially
        self.refresh_listbox()

    def on_qtype_change(self):
        t = self.qtype.get()
        if t == "TF":
            self.mcq_frame.pack_forget()
            self.tf_frame.pack(fill="x", pady=6)
        else:
            self.tf_frame.pack_forget()
            self.mcq_frame.pack(fill="x", pady=6)

    def add_question(self):
        tekst = self.entry_tekst.get("1.0", "end").strip()
        if not tekst:
            messagebox.showwarning("Greška", "Tekst pitanja ne smije biti prazan.")
            return
        if self.qtype.get() == "TF":
            tocan = True if self.tf_answer.get() == "True" else False
            p = PitanjeTF(tekst=tekst, tocan=tocan)
        else:
            opcije = [v.get().strip() for v in self.option_vars]
            if any(not o for o in opcije):
                messagebox.showwarning("Greška", "Sve opcije moraju biti popunjene za MCQ.")
                return
            tocan_index = int(self.mcq_correct.get())
            try:
                p = PitanjeMCQ(tekst=tekst, opcije=opcije, tocan_index=tocan_index)
            except ValueError as e:
                messagebox.showerror("Greška", str(e))
                return
        self.pitanja.append(p)
        self.entry_tekst.delete("1.0", "end")
        for v in self.option_vars:
            v.set("")
        self.mcq_correct.set(0)
        self.status_var.set("Pitanje dodano.")
        self.refresh_listbox()

    def refresh_listbox(self):
        self.lb_pitanja.delete(0, "end")
        for i, p in enumerate(self.pitanja):
            display = f"{i+1}. {'[TF]' if p.tip=='TF' else '[MCQ]'} {p.tekst[:80]}"
            self.lb_pitanja.insert("end", display)

    def delete_selected(self):
        sel = self.lb_pitanja.curselection()
        if not sel:
            messagebox.showinfo("Info", "Nema odabranog pitanja za brisanje.")
            return
        idx = sel[0]
        confirmed = messagebox.askyesno("Potvrda", "Obrisati odabrano pitanje?")
        if confirmed:
            del self.pitanja[idx]
            self.refresh_listbox()
            self.status_var.set("Pitanje obrisano.")

    def on_edit_selected(self, event=None):
        sel = self.lb_pitanja.curselection()
        if not sel:
            return
        idx = sel[0]
        p = self.pitanja[idx]
        # switch to editor form and load values
        self.notebook.select(self.frame_editor)
        self.entry_tekst.delete("1.0", "end")
        self.entry_tekst.insert("1.0", p.tekst)
        if p.tip == "TF":
            self.qtype.set("TF")
            self.on_qtype_change()
            self.tf_answer.set("True" if p.tocan else "False")
        else:
            self.qtype.set("MCQ")
            self.on_qtype_change()
            for i, v in enumerate(self.option_vars):
                v.set(p.opcije[i])
            self.mcq_correct.set(p.tocan_index)

    def save_to_file(self):
        if not self.pitanja:
            messagebox.showinfo("Info", "Nema pitanja za spremiti.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if not path:
            return
        data = [p.to_dict() for p in self.pitanja]
        # ensure proper fields for each type
        export = []
        for p in data:
            if p["tip"] == "TF":
                export.append({"tip":"TF","tekst":p["tekst"], "tocan": p.get("tocan", False)})
            else:
                export.append({"tip":"MCQ","tekst":p["tekst"], "opcije": p.get("opcije",[]), "tocan_index": p.get("tocan_index",0)})
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(export, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"Spremljeno u {path}")
        except Exception as e:
            messagebox.showerror("Greška", f"Ne mogu spremiti datoteku: {e}")

    def load_from_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files","*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded = []
            for item in data:
                loaded.append(Pitanje.from_dict(item))
            self.pitanja = loaded
            self.refresh_listbox()
            self.status_var.set(f"Učitano {len(self.pitanja)} pitanja iz {path}")
        except Exception as e:
            messagebox.showerror("Greška", f"Ne mogu učitati datoteku: {e}")

    def _load_sample_questions(self):
        # add few sample questions for quick testing
        s = [
            PitanjeTF("Zemlja je ravna ploča.", False),
            PitanjeTF("Python je programski jezik.", True),
            PitanjeMCQ("Koji je glavni grad Hrvatske?", ["Zagreb","Split","Rijeka","Osijek"], 0),
            PitanjeMCQ("Koji je rezultat 2+2?", ["3","4","5","22"], 1)
        ]
        # only add if empty to avoid duplicates
        if not self.pitanja:
            self.pitanja.extend(s)
            self.refresh_listbox()

    # ========== Quiz tab ==========
    def _build_quiz(self):
        top = ttk.Frame(self.frame_quiz)
        top.pack(fill="x", padx=6, pady=6)

        ttk.Label(top, text="Broj pitanja u kvizu:").pack(side="left")
        self.quiz_count = tk.IntVar(value=5)
        ttk.Spinbox(top, from_=1, to=50, textvariable=self.quiz_count, width=6).pack(side="left", padx=6)

        ttk.Button(top, text="Pokreni kviz", command=self.start_quiz).pack(side="left", padx=6)
        ttk.Button(top, text="Reset", command=self.reset_quiz).pack(side="left")

        # area for question display
        self.quiz_area = ttk.Frame(self.frame_quiz, relief="ridge", padding=8)
        self.quiz_area.pack(fill="both", expand=True, padx=6, pady=6)

        self.quiz_question_var = tk.StringVar(value="Niste pokrenuli kviz.")
        ttk.Label(self.quiz_area, textvariable=self.quiz_question_var, wraplength=600, font=("TkDefaultFont", 11)).pack(anchor="w", pady=(0,8))

        # dynamic area for answer controls
        self.answer_controls = ttk.Frame(self.quiz_area)
        self.answer_controls.pack(anchor="w")

        # navigation and feedback
        nav = ttk.Frame(self.frame_quiz)
        nav.pack(fill="x", padx=6, pady=(0,6))
        self.btn_next = ttk.Button(nav, text="Sljedeće", command=self.next_question, state="disabled")
        self.btn_next.pack(side="right")
        self.btn_prev = ttk.Button(nav, text="Prethodno", command=self.prev_question, state="disabled")
        self.btn_prev.pack(side="right", padx=(0,6))
        self.btn_submit = ttk.Button(nav, text="Završi kviz", command=self.finish_quiz, state="disabled")
        self.btn_submit.pack(side="right", padx=(0,6))

        self.quiz_info_var = tk.StringVar(value="Status kviza: nije započet")
        ttk.Label(self.frame_quiz, textvariable=self.quiz_info_var).pack(anchor="w", padx=6)

        # internal quiz state
        self.current_quiz_questions: List[Pitanje] = []
        self.current_index: int = 0
        self.user_answers: List[Optional[int]] = []  # for MCQ store index 0-3, for TF store 0/1

    def start_quiz(self):
        if not self.pitanja:
            messagebox.showinfo("Info", "Nema dostupnih pitanja u bazi.")
            return
        n = min(self.quiz_count.get(), len(self.pitanja))
        self.current_quiz_questions = random.sample(self.pitanja, n)
        self.user_answers = [None]*n
        self.current_index = 0
        self.show_question(0)
        self.btn_next.config(state="normal")
        self.btn_prev.config(state="normal")
        self.btn_submit.config(state="normal")
        self.quiz_info_var.set(f"Kviz pokrenut: {n} pitanja")

    def reset_quiz(self):
        self.current_quiz_questions = []
        self.user_answers = []
        self.current_index = 0
        self.quiz_question_var.set("Kviz resetiran.")
        for widget in self.answer_controls.winfo_children():
            widget.destroy()
        self.btn_next.config(state="disabled")
        self.btn_prev.config(state="disabled")
        self.btn_submit.config(state="disabled")
        self.quiz_info_var.set("Status kviza: nije započet")

    def show_question(self, index):
        # clear answer controls
        for widget in self.answer_controls.winfo_children():
            widget.destroy()
        if index < 0 or index >= len(self.current_quiz_questions):
            return
        q = self.current_quiz_questions[index]
        self.quiz_question_var.set(f"Pitanje {index+1}/{len(self.current_quiz_questions)}: {q.tekst}")
        if q.tip == "TF":
            # Radiobuttons True/False
            self.tf_ans_var = tk.IntVar(value=-1 if self.user_answers[index] is None else self.user_answers[index])
            ttk.Radiobutton(self.answer_controls, text="True", variable=self.tf_ans_var, value=1, command=lambda:self._record_answer(index, self.tf_ans_var.get())).pack(anchor="w")
            ttk.Radiobutton(self.answer_controls, text="False", variable=self.tf_ans_var, value=0, command=lambda:self._record_answer(index, self.tf_ans_var.get())).pack(anchor="w")
            # preselect if answered
            if self.user_answers[index] is not None:
                self.tf_ans_var.set(self.user_answers[index])
        else:
            # MCQ - radiobuttons for options
            self.mcq_ans_var = tk.IntVar(value=-1 if self.user_answers[index] is None else self.user_answers[index])
            for i, opt in enumerate(q.opcije):
                ttk.Radiobutton(self.answer_controls, text=f"{chr(65+i)}: {opt}", variable=self.mcq_ans_var, value=i, command=lambda i=i: self._record_answer(index, i)).pack(anchor="w", pady=2)
            if self.user_answers[index] is not None:
                self.mcq_ans_var.set(self.user_answers[index])

    def _record_answer(self, qindex, val):
        # val for TF: 1=True,0=False ; for MCQ: index 0-3
        self.user_answers[qindex] = int(val)
        self.status_var.set(f"Odgovor za pitanje {qindex+1} spremljen.")

    def next_question(self):
        if not self.current_quiz_questions:
            return
        if self.current_index < len(self.current_quiz_questions)-1:
            self.current_index += 1
            self.show_question(self.current_index)

    def prev_question(self):
        if not self.current_quiz_questions:
            return
        if self.current_index > 0:
            self.current_index -= 1
            self.show_question(self.current_index)

    def finish_quiz(self):
        if not self.current_quiz_questions:
            return
        # Confirm finish
        confirmed = messagebox.askyesno("Potvrda", "Jeste li sigurni da želite završiti kviz?")
        if not confirmed:
            return
        correct = 0
        total = len(self.current_quiz_questions)
        for i, q in enumerate(self.current_quiz_questions):
            ans = self.user_answers[i]
            if ans is None:
                continue
            if q.tip == "TF":
                expected = 1 if q.tocan else 0
                if ans == expected:
                    correct += 1
            else:
                if ans == q.tocan_index:
                    correct += 1
        pct = (correct/total)*100 if total>0 else 0
        messagebox.showinfo("Rezultat kviza", f"Točnih odgovora: {correct}/{total}\nPostotak: {pct:.1f}%")
        self.quiz_info_var.set(f"Kviz završen: {correct}/{total} točno ({pct:.1f}%)")
        # disable navigation
        self.btn_next.config(state="disabled")
        self.btn_prev.config(state="disabled")
        self.btn_submit.config(state="disabled")

# ========== Run app ==========
def main():
    root = tk.Tk()
    app = KvizApp(root)
    root.geometry("900x600")
    root.mainloop()

if __name__ == '__main__':
    main()
