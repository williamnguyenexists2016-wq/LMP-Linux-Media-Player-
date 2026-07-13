#!/usr/bin/env python3

import tkinter as tk
from tkinter import filedialog
import mpv
import os
import glob
import tempfile
import subprocess
from PIL import Image
import pillow_heif

APP = "LMP (Linux Media Player)"

DOWNLOADS = os.path.expanduser("~/Downloads")
MUSIC = os.path.expanduser("~/Music")
VIDEOS = os.path.expanduser("~/Videos")


class LMP:
    def __init__(self, root):
        self.root = root
        self.root.title(APP)
        self.root.geometry("1000x650")
        self.root.configure(bg="#cfe3ff")

        # ================= MPV =================
        self.player = mpv.MPV(
            ytdl=False,
            osc=False,
            input_default_bindings=True,
            input_vo_keyboard=True
        )

        self.player.volume = 70
        self.player.speed = 1.0

        self.files = []
        self.current = None

        # ================= VIDEO =================
        self.video = tk.Frame(root, bg="black")
        self.video.pack(fill="both", expand=True)

        self.root.update()
        self.player.wid = self.video.winfo_id()

        # ================= STATUS =================
        self.status = tk.Label(root, text="Ready", bg="#bcd6ff", anchor="w")
        self.status.pack(fill="x")

        # ================= PLAYLIST =================
        self.listbox = tk.Listbox(root, height=6)
        self.listbox.pack(fill="x")
        self.listbox.bind("<Double-Button-1>", self.play_selected)

        # ================= CONTROLS =================
        bar = tk.Frame(root, bg="#cfe3ff")
        bar.pack(fill="x")

        tk.Button(bar, text="Open", command=self.open_file).pack(side="left")
        tk.Button(bar, text="Play", command=self.play).pack(side="left")
        tk.Button(bar, text="Pause", command=self.pause).pack(side="left")
        tk.Button(bar, text="Stop", command=self.stop).pack(side="left")
        tk.Button(bar, text="Scan", command=self.scan).pack(side="left")

        tk.Button(bar, text="CD", command=self.play_cd).pack(side="left")
        tk.Button(bar, text="DVD", command=self.play_dvd).pack(side="left")
        tk.Button(bar, text="Eject 💿", command=self.eject_disc).pack(side="left")

        # ================= SLIDERS =================
        self.volume = tk.Scale(
            bar, from_=0, to=100,
            orient="horizontal",
            label="Vol",
            command=self.set_volume
        )
        self.volume.set(70)
        self.volume.pack(side="right")

        self.speed = tk.Scale(
            bar, from_=50, to=200,
            orient="horizontal",
            label="Speed",
            command=self.set_speed
        )
        self.speed.set(100)
        self.speed.pack(side="right")

        # ================= KEYBOARD =================
        self.root.bind("<space>", self.toggle_play)
        self.root.bind("<r>", self.reset_settings)
        self.root.bind("<R>", self.reset_settings)

        # ================= START =================
        self.scan()

    # ================= FILE =================
    def open_file(self):
        file = filedialog.askopenfilename(
            initialdir=DOWNLOADS,
            filetypes=[
                ("Media Files",
                 "*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.flac *.heic *.heif"),
                ("All Files", "*.*")
            ]
        )

        if file:
            file = self.handle_heic(file)
            if file:
                self.add(file)
                self.load(file)

    def add(self, file):
        self.files.append(file)
        self.listbox.insert(tk.END, os.path.basename(file))

    def play_selected(self, event):
        i = self.listbox.curselection()
        if i:
            self.load(self.files[i[0]])
            self.play()

    # ================= HEIC =================
    def handle_heic(self, path):
        if path.lower().endswith((".heic", ".heif")):
            try:
                heif_file = pillow_heif.read_heif(path)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw"
                )

                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                image.save(tmp.name, "PNG")
                return tmp.name

            except:
                self.status.config(text="HEIC failed to load")
                return None

        return path

    # ================= MEDIA =================
    def load(self, path):
        self.current = path
        self.player.loadfile(path)
        self.status.config(text=f"Loaded: {os.path.basename(path)}")

    # ================= PLAYBACK =================
    def play(self):
        self.player.pause = False
        self.status.config(text="Playing")

    def pause(self):
        self.player.pause = True
        self.status.config(text="Paused")

    def stop(self):
        self.player.stop()
        self.status.config(text="Stopped")

    def toggle_play(self, event=None):
        self.player.pause = not self.player.pause

    # ================= SCAN =================
    def scan(self):
        self.listbox.delete(0, tk.END)
        self.files.clear()

        for folder in [DOWNLOADS, MUSIC, VIDEOS]:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if f.lower().endswith(
                        (".mp4", ".mkv", ".avi", ".mov",
                         ".mp3", ".wav", ".flac",
                         ".heic", ".heif")
                    ):
                        self.add(os.path.join(folder, f))

        self.status.config(text="Library scanned")

    # ================= CD / DVD =================
    def find_drive(self):
        for d in glob.glob("/dev/sr*") + ["/dev/cdrom"]:
            if os.path.exists(d):
                return d
        return None

    def play_cd(self):
        dev = self.find_drive()
        if not dev:
            self.status.config(text="No CD found")
            return

        self.player.loadfile(f"cdda://{dev}")
        self.status.config(text="Playing CD")

    def play_dvd(self):
        dev = self.find_drive()
        if not dev:
            self.status.config(text="No DVD found")
            return

        self.player.loadfile(f"dvd://{dev}")
        self.status.config(text="Playing DVD")

    # ================= NEW: EJECT =================
    def eject_disc(self):
        dev = self.find_drive()

        try:
            if dev:
                subprocess.run(["eject", dev], check=False)
                self.status.config(text="Disc ejected 💿")
            else:
                subprocess.run(["eject"], check=False)
                self.status.config(text="Eject command sent 💿")
        except:
            self.status.config(text="Eject failed")

    # ================= CONTROLS =================
    def set_volume(self, v):
        self.player.volume = int(v)

    def set_speed(self, v):
        self.player.speed = float(v) / 100

    # ================= RESET =================
    def reset_settings(self, event=None):
        self.volume.set(70)
        self.speed.set(100)

        self.player.volume = 70
        self.player.speed = 1.0

        self.status.config(text="Reset: Volume & Speed")


# ================= RUN =================
root = tk.Tk()
app = LMP(root)
root.mainloop()
