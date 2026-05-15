import tkinter as tk
import auth
import main_app

class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        tk.Label(root, text="User").pack()
        self.u = tk.Entry(root)
        self.u.pack()

        tk.Label(root, text="Pass").pack()
        self.p = tk.Entry(root, show="*")
        self.p.pack()

        tk.Button(root, text="Login", command=self.check).pack()

        self.msg = tk.Label(root, text="")
        self.msg.pack()

    def check(self):
        if auth.login(self.u.get(), self.p.get()):
            self.root.destroy()
            main_app.start()
        else:
            self.msg.config(text="Error")