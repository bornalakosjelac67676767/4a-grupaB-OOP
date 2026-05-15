import random
import time
from datetime import datetime
import database as db

def init_senzori():
    senzori = [
        ("CO2 senzor", "Centar"),
        ("Buka senzor", "Škola"),
        ("Promet senzor", "Autocesta"),
        ("Energija senzor", "Industrija")
    ]

    for s in senzori:
        db.dodaj_senzor(s[0], s[1])


def pokreni_simulaciju():
    while True:
        sensor_id = random.randint(1, 4)
        tip = random.choice(["CO2", "BUKA", "PROMET", "ENERGIJA"])
        vrijednost = round(random.uniform(20, 200), 2)

        db.dodaj_mjerenje(
            sensor_id,
            datetime.now().isoformat(),
            tip,
            vrijednost
        )

        time.sleep(1.5)