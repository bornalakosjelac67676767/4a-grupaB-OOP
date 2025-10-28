
# Kratka provjera – Evidencija učenika (CSV fokus, XML bonus)
# Vrijeme: 20 min

import tkinter as tk
from tkinter import messagebox
import csv
# XML bonus:
import xml.etree.ElementTree as ET

#  RAM se briše kada se program zatvori, dok datoteke omogućuju da podaci sačuvani trajno.

#  CSV je jednostavan i tablični (redovi/stupci), XML je hijerarhijski i opisuje strukturu podacima pomoću tagova.

#  Automatski zatvara datoteku i u slučaju greške, pa je sigurnija i čitljivija od manualnog f.close().

# Da se stari podaci ne dupliciraju i da prikaz odražava stvarni sadržaj datoteke.

#  Automatski prepoznaje zaglavlja i pretvara retke u rječnike, što olakšava rad i čini kod čitljivijim.

# --- MODEL ---
class Ucenik:
    def __init__(self, ime, prezime, razred):
        self.ime = ime
        self.prezime = prezime
        self.razred = razred

    def __str__(self):
        return f"{self.ime} {self.prezime} ({self.razred})"


# --- APP ---
class EvidencijaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📘 Evidencija učenika – provjera")
        self.root.geometry("620x420")
        self.root.configure(bg="#f4f8ff")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.ucenici = []
        self.odabrani_index = None

        self.kreiraj_gui()

        # Automatski pokušaj učitati CSV pri pokretanju
        if os.path.exists("ucenici.csv"):
            self.ucitaj_iz_csv(silent=True)

    def kreiraj_gui(self):
        unos = tk.Frame(self.root, padx=10, pady=10, bg="#e6f0ff", relief="groove", bd=2)
        unos.grid(row=0, column=0, sticky="EW")
        unos.columnconfigure(1, weight=1)

        tk.Label(unos, text="Ime:", bg="#e6f0ff", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="W")
        self.e_ime = tk.Entry(unos, font=("Arial", 10)); self.e_ime.grid(row=0, column=1, sticky="EW", pady=2)

        tk.Label(unos, text="Prezime:", bg="#e6f0ff", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="W")
        self.e_prezime = tk.Entry(unos, font=("Arial", 10)); self.e_prezime.grid(row=1, column=1, sticky="EW", pady=2)

        tk.Label(unos, text="Razred:", bg="#e6f0ff", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="W")
        self.e_razred = tk.Entry(unos, font=("Arial", 10)); self.e_razred.grid(row=2, column=1, sticky="EW", pady=2)

        gumbi = tk.Frame(unos, bg="#e6f0ff")
        gumbi.grid(row=3, column=0, columnspan=2, pady=10)

        # --- Gumbi s bojama ---
        def btn(t, c, cmd):
            return tk.Button(gumbi, text=t, bg=c, fg="white", relief="raised",
                             activebackground="#333", padx=10, pady=5, command=cmd)

        btn("➕ Dodaj", "#4CAF50", self.dodaj_ucenika).pack(side="left", padx=5)
        btn("💾 Spremi CSV", "#1976D2", self.spremi_u_csv).pack(side="left", padx=5)
        btn("📂 Učitaj CSV", "#0288D1", self.ucitaj_iz_csv).pack(side="left", padx=5)
        btn("💾 XML", "#9C27B0", self.spremi_u_xml).pack(side="left", padx=5)
        btn("📂 XML", "#7B1FA2", self.ucitaj_iz_xml).pack(side="left", padx=5)

        # --- Prikaz učenika ---
        prikaz = tk.Frame(self.root, padx=10, pady=10, bg="#f4f8ff")
        prikaz.grid(row=1, column=0, sticky="NSEW")
        prikaz.columnconfigure(0, weight=1)
        prikaz.rowconfigure(0, weight=1)

        self.lb = tk.Listbox(prikaz, font=("Consolas", 11), bg="#ffffff", fg="#333",
                             selectbackground="#cce5ff", selectforeground="#000")
        self.lb.grid(row=0, column=0, sticky="NSEW")

        sc = tk.Scrollbar(prikaz, orient="vertical", command=self.lb.yview)
        sc.grid(row=0, column=1, sticky="NS")
        self.lb.configure(yscrollcommand=sc.set)

        self.lb.bind("<<ListboxSelect>>", self.odaberi)

    def osvjezi(self):
        self.lb.delete(0, tk.END)
        for u in self.ucenici:
            self.lb.insert(tk.END, str(u))

    def ocisti_unos(self):
        self.e_ime.delete(0, tk.END)
        self.e_prezime.delete(0, tk.END)
        self.e_razred.delete(0, tk.END)

    def dodaj_ucenika(self):
        ime = self.e_ime.get().strip()
        prezime = self.e_prezime.get().strip()
        razred = self.e_razred.get().strip()
        if not (ime and prezime and razred):
            messagebox.showwarning("Upozorenje", "Sva polja moraju biti popunjena.")
            return
        self.ucenici.append(Ucenik(ime, prezime, razred))
        self.osvjezi()
        self.ocisti_unos()

    def odaberi(self, _e):
        sel = self.lb.curselection()
        self.odabrani_index = sel[0] if sel else None

    # --- CSV ---
    def spremi_u_csv(self):
        """Spremanje učenika u CSV pomoću DictWriter."""
        try:
            with open("ucenici.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["ime", "prezime", "razred"])
                writer.writeheader()
                for u in self.ucenici:
                    writer.writerow({"ime": u.ime, "prezime": u.prezime, "razred": u.razred})
            messagebox.showinfo("Info", "✅ Podaci su spremljeni u ucenici.csv")
        except Exception as e:
            messagebox.showerror("Greška", f"Nije moguće spremiti CSV: {e}")

    def ucitaj_iz_csv(self, silent=False):
        """Učitavanje učenika iz CSV-a pomoću DictReader."""
        try:
            self.ucenici.clear()
            self.lb.delete(0, tk.END)
            with open("ucenici.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.ucenici.append(Ucenik(row["ime"], row["prezime"], row["razred"]))
            self.osvjezi()
            if not silent:
                messagebox.showinfo("Info", "📂 Podaci su učitani iz ucenici.csv")
        except FileNotFoundError:
            if not silent:
                messagebox.showwarning("Upozorenje", "Datoteka ucenici.csv ne postoji.")
        except Exception as e:
            messagebox.showerror("Greška", f"Nije moguće učitati CSV: {e}")

    # --- XML (BONUS) ---
    def spremi_u_xml(self):
        """BONUS: Spremi u XML koristeći ElementTree."""
        try:
            root = ET.Element("evidencija")
            for u in self.ucenici:
                e = ET.SubElement(root, "ucenik")
                ET.SubElement(e, "ime").text = u.ime
                ET.SubElement(e, "prezime").text = u.prezime
                ET.SubElement(e, "razred").text = u.razred
            tree = ET.ElementTree(root)
            tree.write("ucenici.xml", encoding="utf-8", xml_declaration=True)
            messagebox.showinfo("Info", "💾 XML spremljen u ucenici.xml")
        except Exception as e:
            messagebox.showerror("Greška", f"Nije moguće spremiti XML: {e}")

    def ucitaj_iz_xml(self):
        """BONUS: Učitaj iz XML datoteke."""
        try:
            self.ucenici.clear()
            self.lb.delete(0, tk.END)
            tree = ET.parse("ucenici.xml")
            root = tree.getroot()
            for e in root.findall("ucenik"):
                ime = e.findtext("ime", default="")
                prezime = e.findtext("prezime", default="")
                razred = e.findtext("razred", default="")
                if ime and prezime and razred:
                    self.ucenici.append(Ucenik(ime, prezime, razred))
            self.osvjezi()
            messagebox.showinfo("Info", "📂 XML učitan iz ucenici.xml")
        except FileNotFoundError:
            messagebox.showwarning("Upozorenje", "Datoteka ucenici.xml ne postoji.")
        except Exception as e:
            messagebox.showerror("Greška", f"Nije moguće učitati XML: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = EvidencijaApp(root)
    root.mainloop()
