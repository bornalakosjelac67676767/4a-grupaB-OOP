import database as db

def prosjek(tip):
    data = db.dohvati_podatke()
    vals = [x[4] for x in data if x[3] == tip]
    return sum(vals) / len(vals) if vals else 0


def anomalije(prag=150):
    data = db.dohvati_podatke()
    return [x for x in data if x[4] > prag]