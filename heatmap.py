import matplotlib.pyplot as plt
import database as db
import random

def show_heatmap():
    data = db.dohvati_podatke()

    x = [random.randint(0, 10) for _ in data]
    y = [random.randint(0, 10) for _ in data]
    c = [d[4] for d in data]

    plt.scatter(x, y, c=c, cmap="hot", s=200)
    plt.colorbar()
    plt.title("AEGIS GRID Heatmap")
    plt.show()