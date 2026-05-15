import matplotlib.pyplot as plt
import database as db

def show_chart():
    data = db.dohvati_podatke()
    values = [x[4] for x in data]

    plt.plot(values)
    plt.title("AEGIS GRID Data")
    plt.show()