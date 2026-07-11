import tkinter as tk
from tkinter import filedialog
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


# ================= FOLDERS =================

HOME = os.path.expanduser("~")

DOWNLOADS = os.path.join(HOME, "Downloads")
DOCUMENTS = os.path.join(HOME, "Documents")
PICTURES = os.path.join(HOME, "Pictures")
MUSIC = os.path.join(HOME, "Music")
VIDEOS = os.path.join(HOME, "Videos")


# Downloads is first priority

PRIORITY_FOLDERS = [

    DOWNLOADS,
    VIDEOS,
    MUSIC,
    PICTURES,
    DOCUMENTS,
    HOME

]



# ================= THEMES =================

THEMES = {


    "dark": {

        "home": "#0b1d3a",

        "bar": "#12345b",

        "text": "white"

    },


    "light": {

        "home": "#b7dcff",

        "bar": "#7fbfff",

        "text": "black"

    }

}




def load_settings():

    if os.path.exists(SETTINGS_FILE):

        try:

            with open(
                SETTINGS_FILE,
                "r"
            ) as file:

                return json.load(file)

        except:

            pass


    return {

        "theme": "dark"

    }




def save_settings(data):

    with open(
        SETTINGS_FILE,
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )




class LMP:


    def __init__(self, root):


        self.root = root


        self.settings = load_settings()


        self.theme_name = self.settings["theme"]


        self.theme = THEMES[self.theme_name]



        self.video_loaded = False



        self.root.title(APP)


        self.root.geometry(
            "1100x700"
        )



        # ================= VIDEO =================


        self.video = tk.Frame(

            root,

            bg=self.theme["home"]

        )


        self.video.pack(

            fill="both",

            expand=True

        )



        # ================= MPV =================


        self.player = mpv.MPV(

            osc=False,

            ytdl=False,

            input_default_bindings=True,

            input_vo_keyboard=True

        )


        self.player.volume = 70


        self.root.update()


        self.player.wid = self.video.winfo_id()



        # ================= TASKBAR =================


        self.bar = tk.Frame(

            root,

            bg=self.theme["bar"]

        )


        self.bar.pack(

            side="bottom",

            fill="x"

        )


        # Start BIG

        self.set_large_bar()


        self.create_controls()    # ================= TASKBAR SIZE =================


    def set_large_bar(self):

        self.bar.configure(
            height=75
        )


    def set_small_bar(self):

        self.bar.configure(
            height=35
        )



    # ================= CONTROLS =================


    def create_controls(self):

        buttons = [

            ("Open", self.open_file),

            ("Browse", self.browse_files),

            ("▶", self.play),

            ("⏸", self.pause),

            ("⏹", self.stop),

            ("CD", self.play_cd),

            ("DVD", self.play_dvd),

            ("💿", self.eject_disc),

            ("☀/🌙", self.toggle_theme)

        ]


        for text, command in buttons:

            tk.Button(

                self.bar,

                text=text,

                command=command,

                padx=5,

                pady=3

            ).pack(

                side="left",

                padx=2

            )



        self.volume = tk.Scale(

            self.bar,

            from_=0,

            to=100,

            orient="horizontal",

            length=120,

            command=self.set_volume

        )


        self.volume.set(70)


        self.volume.pack(

            side="right"

        )



    # ================= BROWSER =================


    def browse_files(self):

        window = tk.Toplevel(

            self.root

        )


        window.title(

            "LMP Browser"

        )


        window.geometry(

            "700x450"

        )


        self.browser_folder = DOWNLOADS



        folder_box = tk.Frame(

            window

        )


        folder_box.pack(

            side="left",

            fill="y"

        )


        self.file_list = tk.Listbox(

            window

        )


        self.file_list.pack(

            side="right",

            fill="both",

            expand=True

        )



        folders = [

            ("⬇ Downloads", DOWNLOADS),

            ("🎬 Videos", VIDEOS),

            ("🎵 Music", MUSIC),

            ("🖼 Pictures", PICTURES),

            ("📄 Documents", DOCUMENTS),

            ("🏠 Home", HOME)

        ]



        for name, path in folders:

            tk.Button(

                folder_box,

                text=name,

                width=15,

                command=lambda p=path:
                    self.show_files(p)

            ).pack(

                pady=3

            )



        self.file_list.bind(

            "<Double-Button-1>",

            self.open_browser_file

        )


        # Open Downloads automatically

        self.show_files(

            DOWNLOADS

        )



    def show_files(self, folder):

        self.browser_folder = folder


        self.file_list.delete(

            0,

            tk.END

        )


        if not os.path.exists(folder):

            return



        for item in os.listdir(folder):

            path = os.path.join(

                folder,

                item

            )


            if os.path.isfile(path):

                if item.lower().endswith(

                    (

                        ".mp4",

                        ".mkv",

                        ".avi",

                        ".mov",

                        ".mp3",

                        ".wav",

                        ".flac",

                        ".heic",

                        ".heif"

                    )

                ):

                    self.file_list.insert(

                        tk.END,

                        item

                    )



    def open_browser_file(self, event=None):

        selected = self.file_list.curselection()


        if not selected:

            return



        filename = self.file_list.get(

            selected[0]

        )


        path = os.path.join(

            self.browser_folder,

            filename

        )


        path = self.handle_heic(

            path

        )


        if path:

            self.load(

                path

            )



    # ================= OPEN =================


    def open_file(self):

        file = filedialog.askopenfilename(

            initialdir=DOWNLOADS,

            filetypes=[

                (

                    "Media Files",

                    "*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.flac *.heic *.heif"

                ),

                (

                    "All Files",

                    "*.*"

                )

            ]

        )


        if file:

            file = self.handle_heic(

                file

            )


            if file:

                self.load(

                    file

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


            except:

                return None


        return path
            # ================= MEDIA =================


    def load(self, path):

        self.current = path


        self.player.loadfile(

            path

        )


        self.video_loaded = True



        # Video becomes black

        self.video.configure(

            bg="black"

        )


        # Shrink taskbar

        self.set_small_bar()



    def stop(self):

        self.player.stop()


        self.video_loaded = False



        # Return home screen

        self.video.configure(

            bg=self.theme["home"]

        )


        # Bring back large taskbar

        self.set_large_bar()




    # ================= PLAYBACK =================


    def play(self):

        self.player.pause = False



    def pause(self):

        self.player.pause = True




    # ================= VOLUME =================


    def set_volume(self, value):

        self.player.volume = int(value)




    # ================= CD / DVD =================


    def find_drive(self):

        drives = (

            glob.glob("/dev/sr*")

            +

            [

                "/dev/cdrom"

            ]

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

        drive = self.find_drive()


        try:

            if drive:

                subprocess.run(

                    [

                        "eject",

                        drive

                    ],

                    check=False

                )

            else:

                subprocess.run(

                    [

                        "eject"

                    ],

                    check=False

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


        # Update home screen color

        if not self.video_loaded:

            self.video.configure(

                bg=self.theme["home"]

            )


        # Update taskbar

        self.bar.configure(

            bg=self.theme["bar"]

        )



# ================= START =================


root = tk.Tk()


app = LMP(

    root

)


root.mainloop()