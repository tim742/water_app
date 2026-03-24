import tkinter as tk
from tkinter import messagebox
import pygame
import threading
import time
import os
import sys
from PIL import Image, ImageTk

# Funkcija failu ceļu atrašanai (nepieciešama EXE failam)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class WaterProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hydration Pro Tracker")
        self.root.geometry("320x520")
        self.root.resizable(False, False)

        # Galvenie mainīgie
        self.current_water = 0
        self.goal = 2000
        self.is_running = False
        self.remaining_seconds = 0
        
        pygame.mixer.init()

        # 1. Attēlu ielāde
        self.load_images()

        # 2. Galvenais laukums (Canvas) fonam
        self.canvas = tk.Canvas(root, width=320, height=520, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

        # 3. Interfeisa izveide
        self.create_custom_ui()

    def load_images(self):
        # Ielādējam fonu un pogas ar izmēru pielāgošanu
        self.bg_img = ImageTk.PhotoImage(Image.open(resource_path("bg_main.png")).resize((320, 520)))
        self.glass_n = ImageTk.PhotoImage(Image.open(resource_path("glass_empty.png")).resize((130, 130)))
        self.glass_p = ImageTk.PhotoImage(Image.open(resource_path("glass_pressed.png")).resize((130, 130)))
        self.start_n = ImageTk.PhotoImage(Image.open(resource_path("btn_start.png")).resize((160, 45)))
        self.start_c = ImageTk.PhotoImage(Image.open(resource_path("btn_start_click.png")).resize((160, 45)))
        self.stop_n = ImageTk.PhotoImage(Image.open(resource_path("btn_stop.png")).resize((160, 45)))
        self.stop_c = ImageTk.PhotoImage(Image.open(resource_path("btn_stop_click.png")).resize((160, 45)))

    def create_custom_ui(self):
        # Ūdens skaitītājs ar Aristotelica Pro šriftu
        self.counter_label = self.canvas.create_text(
            160, 60, text="0 / 2000 ml", fill="white", 
            font=("Aristotelica Pro", 26, "bold")
        )

        # Galvenā poga (Stikls)
        self.glass_btn = tk.Label(self.root, image=self.glass_n, bg="#1a1a1a", bd=0, cursor="hand2")
        self.glass_btn.bind("<Button-1>", lambda e: self.glass_btn.config(image=self.glass_p))
        self.glass_btn.bind("<ButtonRelease-1>", self.on_glass_click)
        self.canvas.create_window(160, 180, window=self.glass_btn)

        # Taimera teksts (Krāsa #1a1a1a)
        self.timer_display = self.canvas.create_text(
            160, 290, text="Next reminder: --:--", 
            fill="#1a1a1a", font=("Consolas", 14, "bold") 
        )

        # Ievades lauka apraksts un pats lauks
        tk.Label(self.root, text="Set interval (min):", bg="#1a1a1a", fg="gray").place(x=110, y=315)
        self.time_entry = tk.Entry(self.root, width=5, font=("Arial", 14), justify="center")
        self.time_entry.insert(0, "30")
        self.canvas.create_window(160, 350, window=self.time_entry)

        # START poga
        self.start_btn = tk.Label(self.root, image=self.start_n, bg="#1a1a1a", bd=0, cursor="hand2")
        self.start_btn.bind("<Button-1>", self.on_start_click)
        self.canvas.create_window(160, 410, window=self.start_btn)

        # STOP poga
        self.stop_btn = tk.Label(self.root, image=self.stop_n, bg="#1a1a1a", bd=0, cursor="hand2")
        self.stop_btn.bind("<Button-1>", self.on_stop_click)
        self.canvas.create_window(160, 470, window=self.stop_btn)

    def on_glass_click(self, event):
        # Funkcija, kas nostrādā, kad nospiež uz stikla
        self.glass_btn.config(image=self.glass_n)
        if self.current_water < self.goal:
            self.current_water += 200
            self.canvas.itemconfig(self.counter_label, text=f"{self.current_water} / {self.goal} ml")

    def update_timer_loop(self):
        # Taimera atjaunošanas loģika sekundēs
        if self.is_running:
            if self.remaining_seconds > 0:
                mins, secs = divmod(self.remaining_seconds, 60)
                self.canvas.itemconfig(self.timer_display, text=f"Next reminder: {mins:02d}:{secs:02d}")
                self.remaining_seconds -= 1
                self.root.after(1000, self.update_timer_loop)
            else:
                self.play_alert()
                # Restartējam taimeri jaunam ciklam
                try:
                    self.remaining_seconds = int(self.time_entry.get()) * 60
                    self.update_timer_loop()
                except:
                    self.is_running = False

    def play_alert(self):
        # Skaņas signāls un paziņojums
        try:
            pygame.mixer.music.load(resource_path("ring.mp3"))
            pygame.mixer.music.play()
        except: pass
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        messagebox.showinfo("Reminder", "Hey! Drink some water! 💧")
        self.root.attributes("-topmost", False)

    def on_start_click(self, event):
        # Starta pogas nospiešana
        if not self.is_running:
            try:
                mins = int(self.time_entry.get())
                if mins <= 0: raise ValueError
                self.is_running = True
                self.remaining_seconds = mins * 60
                
                self.start_btn.config(image=self.start_c)
                self.root.after(200, lambda: self.start_btn.config(image=self.start_n))
                self.update_timer_loop()
            except ValueError:
                messagebox.showerror("Error", "Enter valid minutes!")

    def on_stop_click(self, event):
        # Stop pogas nospiešana
        self.is_running = False
        self.canvas.itemconfig(self.timer_display, text="Timer stopped")
        self.stop_btn.config(image=self.stop_c)
        self.root.after(200, lambda: self.stop_btn.config(image=self.stop_n))

if __name__ == "__main__":
    root = tk.Tk()
    app = WaterProApp(root)
    root.mainloop()