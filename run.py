import threading
import tkinter as tk

import database as db
import auth
import iot_simulator
import login_gui


# 🚀 BOOT SCREEN (ЗАГРУЗКА СИСТЕМЫ)
def boot_screen():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.configure(bg="black")

    label = tk.Label(
        splash,
        text="AEGIS GRID\nINITIALIZING SYSTEM...",
        fg="#4cc9f0",
        bg="black",
        font=("Arial", 18, "bold")
    )
    label.pack(padx=60, pady=60)

    splash.after(2000, splash.destroy)
    splash.mainloop()


# 🌐 IoT SIMULATION START
def start_simulation():
    iot_simulator.init_senzori()
    iot_simulator.pokreni_simulaciju()


# 🚀 MAIN START
if __name__ == "__main__":

    # 🗄️ init database
    db.init_db()

    # 🔐 init users
    auth.init_users()

    # 🚀 boot animation
    boot_screen()

    # 🌐 start IoT in background
    threading.Thread(target=start_simulation, daemon=True).start()

    # 🖥️ start login window
    root = tk.Tk()
    login_gui.Login(root)

    root.mainloop()