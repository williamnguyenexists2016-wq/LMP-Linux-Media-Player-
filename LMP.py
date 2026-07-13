import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import mpv
import os
import glob
import subprocess
import json
import tempfile

from PIL import Image
import pillow_heif


APP = "LMP (Linux Media Player)"

SETTINGS_FILE = "lmp_settings.json"



# ================= PATHS =================

HOME = os.path.expanduser("~")

DOWNLOADS = os.path.join(HOME, "Downloads")
VIDEOS = os.path.join(HOME, "Videos")
MUSIC = os.path.join(HOME, "Music")
PICTURES = os.path.join(HOME, "Pictures")
DOCUMENTS = os.path.join(HOME, "Documents")





# ================= THEMES =================

THEMES = {


    "dark": {

        "background": "#0b1d3a",
        "bar": "#123b66",
        "button": "#164b7a",
        "text": "white",
        "slider": "#071426"

    },


    "light": {

        "background": "#b9ddff",
        "bar": "#75baff",
        "button": "#9bd0ff",
        "text": "black",
        "slider": "#d7ecff"

    }


}





# ================= SETTINGS =================


def load_settings():

    if os.path.exists(SETTINGS_FILE):

        try:

            with open(
                SETTINGS_FILE,
                "r"
            ) as f:

                return json.load(f)

        except:

            pass


    return {

        "theme": "dark"

    }




def save_settings(data):

    with open(
        SETTINGS_FILE,
        "w"
    ) as f:

        json.dump(

            data,

            f,

            indent=4

        )





# ================= MAIN APP =================


class LMP:


    def __init__(self, root):


        self.root = root


        self.settings = load_settings()


        self.theme_name = self.settings.get(

            "theme",

            "dark"

        )


        self.theme = THEMES[

            self.theme_name

        ]



        self.current = None

        self.duration = 0

        self.video_playing = False



        self.root.title(APP)


        self.root.geometry(

            "1100x700"

        )



        # VIDEO AREA

        self.video = tk.Frame(

            self.root,

            bg=self.theme["background"]

        )


        self.video.pack(

            fill="both",

            expand=True

        )



        self.root.update()



        # NO VIDEO MESSAGE


        self.no_video_label = tk.Label(

            self.video,

            text="",

            font=(

                "Arial",

                22

            ),

            bg=self.theme["background"],

            fg=self.theme["text"]

        )


        self.no_video_label.place(

            relx=0.5,

            rely=0.5,

            anchor="center"

        )



        # MPV

        self.player = mpv.MPV(

            osc=False,

            ytdl=False,

            input_default_bindings=True,

            input_vo_keyboard=True

        )


        self.player.wid = self.video.winfo_id()


        self.player.volume = 70


        self.player.speed = 1.0
                # ================= TASKBAR =================


        self.bar = tk.Frame(

            self.root,

            bg=self.theme["bar"]

        )


        self.bar.pack(

            side="bottom",

            fill="x"

        )


        self.create_controls()


        self.set_large_bar()



        self.root.bind(

            "<space>",

            self.toggle_play

        )


        self.root.bind(

            "<Escape>",

            self.stop

        )



        self.progress_loop()





    # ================= WIDGET THEME =================


    def style_button(self, button):


        button.configure(

            bg=self.theme["button"],

            fg=self.theme["text"],

            activebackground=self.theme["bar"],

            activeforeground=self.theme["text"]

        )





    def set_large_bar(self):

        self.bar.configure(

            height=70

        )





    def set_small_bar(self):

        self.bar.configure(

            height=45

        )







    # ================= CONTROLS =================


    def create_controls(self):


        buttons = [

            ("Open", self.open_file),

            ("Browse", self.browse_files),

            ("▶ Play", self.play),

            ("⏸ Pause", self.pause),

            ("⏹ Stop", self.stop),

            ("CD", self.play_cd),

            ("DVD", self.play_dvd),

            ("💿 Eject", self.eject_disc),

            ("☀/🌙", self.toggle_theme)

        ]



        self.buttons = []



        for text, command in buttons:


            b = tk.Button(

                self.bar,

                text=text,

                command=command

            )


            self.style_button(b)


            b.pack(

                side="left",

                padx=3,

                pady=5

            )


            self.buttons.append(b)






        # ================= PROGRESS =================


        self.progress = ttk.Scale(

            self.bar,

            from_=0,

            to=100,

            orient="horizontal",

            length=260,

            command=self.seek

        )


        self.progress.pack(

            side="left",

            padx=10

        )





        self.time_label = tk.Label(

            self.bar,

            text="00:00 / 00:00",

            bg=self.theme["bar"],

            fg=self.theme["text"]

        )


        self.time_label.pack(

            side="left"

        )





        # ================= VOLUME =================


        self.volume = tk.Scale(

            self.bar,

            from_=0,

            to=100,

            orient="horizontal",

            length=120,

            label="Volume",

            command=self.set_volume,

            bg=self.theme["bar"],

            fg=self.theme["text"],

            troughcolor=self.theme["slider"],

            highlightthickness=0

        )


        self.volume.set(70)


        self.volume.pack(

            side="right"

        )





        # ================= SPEED =================


        self.speed = tk.Scale(

            self.bar,

            from_=50,

            to=200,

            orient="horizontal",

            length=120,

            label="Speed",

            command=self.set_speed,

            bg=self.theme["bar"],

            fg=self.theme["text"],

            troughcolor=self.theme["slider"],

            highlightthickness=0

        )


        self.speed.set(100)


        self.speed.pack(

            side="right"

        )
            # ================= TIME / PROGRESS =================


    def format_time(self, seconds):

        try:

            seconds = int(seconds)

            minutes = seconds // 60

            seconds = seconds % 60

            return f"{minutes:02}:{seconds:02}"


        except:

            return "00:00"




    def progress_loop(self):

        try:

            if self.player.duration:

                self.duration = self.player.duration



            current = self.player.time or 0



            if self.duration > 0:


                self.progress.set(

                    (

                        current /

                        self.duration

                    )

                    * 100

                )


                self.time_label.configure(

                    text=

                    self.format_time(current)

                    +

                    " / "

                    +

                    self.format_time(self.duration)

                )


        except:

            pass



        self.root.after(

            500,

            self.progress_loop

        )





    def seek(self, value):

        try:

            if self.duration:


                self.player.time = (

                    float(value)

                    /

                    100

                ) * self.duration


        except:

            pass





    # ================= OPEN FILE =================


    def open_file(self):


        file = filedialog.askopenfilename(

            initialdir=DOWNLOADS,

            filetypes=[

                (

                    "Media",

                    "*.mp4 *.mkv *.avi *.mov *.webm "
                    "*.mp3 *.wav *.flac *.aac "
                    "*.heic *.heif"

                ),

                (

                    "All Files",

                    "*.*"

                )

            ]

        )


        if file:


            self.load(

                self.handle_heic(file)

            )





    # ================= HEIC =================


    def handle_heic(self, path):


        if path.lower().endswith(

            (

                ".heic",

                ".heif"

            )

        ):


            try:


                heif = pillow_heif.read_heif(

                    path

                )


                image = Image.frombytes(

                    heif.mode,

                    heif.size,

                    heif.data,

                    "raw"

                )


                temp = tempfile.NamedTemporaryFile(

                    delete=False,

                    suffix=".png"

                )


                image.save(

                    temp.name,

                    "PNG"

                )


                return temp.name



            except Exception as e:


                print(e)


                return None



        return path





    # ================= LOAD MEDIA =================


    def load(self, path):


        if not path:

            return



        self.current = path



        self.no_video_label.configure(

            text=""

        )



        self.player.loadfile(

            path

        )


        self.video_playing = True


        self.video.configure(

            bg="black"

        )


        self.set_small_bar()



        self.root.after(

            1500,

            self.detect_video

        )





    def detect_video(self):


        try:


            if not self.player.video_params:


                self.no_video_label.configure(

                    text="There is no detected video for this file.",

                    bg="black",

                    fg="white"

                )


        except:


            pass





    # ================= PLAYBACK =================


    def play(self):


        self.player.pause = False


        if self.current:

            self.video_playing = True


            self.set_small_bar()





    def pause(self):

        self.player.pause = True





    def stop(self, event=None):


        self.player.stop()


        self.current = None


        self.video_playing = False


        self.progress.set(0)


        self.time_label.configure(

            text="00:00 / 00:00"

        )


        self.no_video_label.configure(

            text=""

        )


        self.video.configure(

            bg=self.theme["background"]

        )


        self.set_large_bar()





    def toggle_play(self,event=None):


        self.player.pause = not self.player.pause





    def set_volume(self,value):

        self.player.volume = int(value)





    def set_speed(self,value):

        self.player.speed = float(value)/100
            # ================= FILE BROWSER =================


    def browse_files(self):


        browser = tk.Toplevel(

            self.root

        )


        browser.title(

            "LMP Browser"

        )


        browser.geometry(

            "700x450"

        )


        browser.configure(

            bg=self.theme["background"]

        )



        self.browser_folder = DOWNLOADS



        left = tk.Frame(

            browser,

            bg=self.theme["bar"]

        )


        left.pack(

            side="left",

            fill="y"

        )



        self.file_list = tk.Listbox(

            browser,

            bg=self.theme["background"],

            fg=self.theme["text"]

        )


        self.file_list.pack(

            side="right",

            fill="both",

            expand=True

        )



        folders = [

            ("Downloads", DOWNLOADS),

            ("Videos", VIDEOS),

            ("Music", MUSIC),

            ("Pictures", PICTURES),

            ("Documents", DOCUMENTS),

            ("Home", HOME)

        ]



        for name, path in folders:


            b = tk.Button(

                left,

                text=name,

                command=lambda p=path:

                self.show_files(p)

            )


            self.style_button(b)


            b.pack(

                pady=3,

                padx=5

            )



        self.file_list.bind(

            "<Double-Button-1>",

            self.open_browser_file

        )



        self.show_files(

            DOWNLOADS

        )





    def show_files(self, folder):


        self.browser_folder = folder


        self.file_list.delete(

            0,

            tk.END

        )



        extensions = (

            ".mp4",

            ".mkv",

            ".avi",

            ".mov",

            ".webm",

            ".wmv",

            ".mp3",

            ".wav",

            ".flac",

            ".aac",

            ".m4a",

            ".heic",

            ".heif"

        )



        if os.path.exists(folder):


            for file in os.listdir(folder):


                if file.lower().endswith(extensions):


                    self.file_list.insert(

                        tk.END,

                        file

                    )





    def open_browser_file(self,event=None):


        selected = self.file_list.curselection()


        if selected:


            filename = self.file_list.get(

                selected[0]

            )


            path = os.path.join(

                self.browser_folder,

                filename

            )


            self.load(

                self.handle_heic(path)

            )





    # ================= CD / DVD =================


    def find_drive(self):


        drives = glob.glob(

            "/dev/sr*"

        )


        for drive in drives:


            if os.path.exists(drive):

                return drive



        return None





    def play_cd(self):


        drive = self.find_drive()


        if drive:


            self.load(

                f"cdda://{drive}"

            )





    def play_dvd(self):


        drive = self.find_drive()


        if drive:


            self.load(

                f"dvd://{drive}"

            )





    def eject_disc(self):


        try:

            subprocess.run(

                [

                    "eject"

                ]

            )


        except:

            pass





    # ================= THEME =================


    def toggle_theme(self):


        if self.theme_name == "dark":

            self.theme_name = "light"


        else:

            self.theme_name = "dark"



        self.theme = THEMES[

            self.theme_name

        ]


        self.settings["theme"] = self.theme_name


        save_settings(

            self.settings

        )


        self.apply_theme()





    def apply_theme(self):


        self.video.configure(

            bg=self.theme["background"]

        )


        self.bar.configure(

            bg=self.theme["bar"]

        )


        self.no_video_label.configure(

            bg=self.theme["background"],

            fg=self.theme["text"]

        )


        self.time_label.configure(

            bg=self.theme["bar"],

            fg=self.theme["text"]

        )


        self.volume.configure(

            bg=self.theme["bar"],

            fg=self.theme["text"],

            troughcolor=self.theme["slider"]

        )


        self.speed.configure(

            bg=self.theme["bar"],

            fg=self.theme["text"],

            troughcolor=self.theme["slider"]

        )



        for button in self.buttons:


            self.style_button(button)





# ================= START =================


if __name__ == "__main__":


    root = tk.Tk()


    app = LMP(

        root

    )


    root.mainloop()
