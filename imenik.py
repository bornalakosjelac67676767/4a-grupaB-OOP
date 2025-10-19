
import tkinter as tk


class Kontakt:
    def __init__(self, ime, email, telefon):
        self.ime = ime
        self.email = email
        self.telefon = telefon

    def __str__(self):
        return f"{self.ime} - {self.email} - {self.telefon}"

class ImenikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digitalni imenik")
        self.kontakti = []

        frame_unos = tk.Frame(root)
        frame_unos.pack(padx=10, pady=10)

        tk.Label(frame_unos, text="Ime i prezime:").grid(row=0, column=0)
        tk.Label(frame_unos, text="Email:").grid(row=1, column=0)
        tk.Label(frame_unos, text="Telefon:").grid(row=2, column=0)

        self.entry_ime = tk.Entry(frame_unos)
        self.entry_email = tk.Entry(frame_unos)
        self.entry_telefon = tk.Entry(frame_unos)

        self.entry_ime.grid(row=0, column=1)
        self.entry_email.grid(row=1, column=1)
        self.entry_telefon.grid(row=2, column=1)

        tk.Button(frame_unos, text="Dodaj", command=self.dodaj).grid(row=3, column=0, pady=5)
        tk.Button(frame_unos, text="Obriši", command=self.obrisi).grid(row=3, column=1, pady=5)

        frame_lista = tk.Frame(root)
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        self.listbox = tk.Listbox(frame_lista, width=50, height=10)
        self.listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar = tk.Scrollbar(frame_lista, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        frame_gumbi = tk.Frame(root)
        frame_gumbi.pack(padx=10, pady=10)

        tk.Button(frame_gumbi, text="Spremi kontakte", command=self.spremi).grid(row=0, column=0, padx=5)
        tk.Button(frame_gumbi, text="Učitaj kontakte", command=self.ucitaj).grid(row=0, column=1, padx=5)

        self.ucitaj()

    def dodaj(self):
        ime = self.entry_ime.get()
        email = self.entry_email.get()
        telefon = self.entry_telefon.get()
        if ime and email and telefon:
            self.kontakti.append(Kontakt(ime, email, telefon))
            self.osvjezi()
            self.entry_ime.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_telefon.delete(0, tk.END)

    def obrisi(self):
        odabrani = self.listbox.curselection()
        if odabrani:
            indeks = odabrani[0]
            self.kontakti.pop(indeks)
            self.osvjezi()

    def spremi(self):
        with open("kontakti.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for k in self.kontakti:
                writer.writerow([k.ime, k.email, k.telefon])

    def ucitaj(self):
        try:
            with open("kontakti.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.kontakti = [Kontakt(r[0], r[1], r[2]) for r in reader]
                self.osvjezi()
        except FileNotFoundError:
            pass

    def osvjezi(self):
        self.listbox.delete(0, tk.END)
        for k in self.kontakti:
            self.listbox.insert(tk.END, str(k))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImenikApp(root)
    root.mainloop()
