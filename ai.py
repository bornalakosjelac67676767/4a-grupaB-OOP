import database as db

def predict_co2():
    data = db.dohvati_podatke()
    co2 = [x[4] for x in data if x[3] == "CO2"]

    if len(co2) < 2:
        return 0

    trend = (co2[-1] - co2[0]) / len(co2)
    return round(co2[-1] + trend * 5, 2)