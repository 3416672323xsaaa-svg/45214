import os
import json
import subprocess
import threading
import shutil

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.switch import MDSwitch
from kivymd.uix.menu import MDDropdownMenu

from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import mainthread


os.environ["LC_ALL"] = "C.UTF-8"
os.environ["LANG"] = "C.UTF-8"


IS_ANDROID = False
cookie_path = "cookie.json"


try:
    from android.storage import app_storage_path
    from android.storage import primary_external_storage_path
    from android.resources import AssetManager

    IS_ANDROID = True
    cookie_path = os.path.join(
        app_storage_path(),
        "cookie.json"
    )

except ImportError:
    AssetManager = None


class DownloadPage(MDBoxLayout):

    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)

        self.sm = sm
        self.orientation = "vertical"
        self.spacing = 10
        self.padding = 20

        self.is_downloading = False

        self.video_dir = self.get_video_dir()

        self.url_input = MDTextField(
            hint_text="BV号 / B站链接",
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.url_input)

        self.cookie_input = MDTextField(
            hint_text="Cookie：SESSDATA=xxx",
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.cookie_input)

        quality_row = MDBoxLayout(
            size_hint_y=None,
            height=50
        )
        quality_row.add_widget(MDLabel(text="画质"))
        self.quality_btn = MDRaisedButton(text="自动")
        self.quality_btn.bind(on_press=self.open_quality)
        quality_row.add_widget(self.quality_btn)
        self.add_widget(quality_row)

        dan_row = MDBoxLayout(
            size_hint_y=None,
            height=50
        )
        dan_row.add_widget(MDLabel(text="下载弹幕"))
        self.danmaku = MDSwitch()
        dan_row.add_widget(self.danmaku)
        self.add_widget(dan_row)

        self.download_btn = MDRaisedButton(text="开始下载")
        self.download_btn.bind(on_press=self.start_download)
        self.add_widget(self.download_btn)

        self.cookie_btn = MDRaisedButton(text="保存Cookie")
        self.cookie_btn.bind(on_press=lambda x: self.save_cookie())
        self.add_widget(self.cookie_btn)

        self.lib_btn = MDRaisedButton(text="打开已下载")
        self.lib_btn.bind(
            on_press=lambda x: setattr(self.sm, "current", "library")
        )
        self.add_widget(self.lib_btn)

        self.log = TextInput(readonly=True)
        self.add_widget(self.log)

        self.qualities = [
            ("自动", None),
            ("360P", 16),
            ("480P", 32),
            ("720P", 64),
            ("1080P", 80),
            ("4K", 120)
        ]
        self.quality_value = None

        self.menu = MDDropdownMenu(
            caller=self.quality_btn,
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": name,
                    "on_release": lambda n=name, v=value: self.set_quality(n, v)
                }
                for name, value in self.qualities
            ]
        )

        self.bdl = self.get_bdl()
        self.load_cookie()

    def get_video_dir(self):
        if IS_ANDROID:
            path = os.path.join(
                app_storage_path(),
                "BiliPink",
                "Videos"
            )
        else:
            path = "./BiliPink/Videos"
        os.makedirs(path, exist_ok=True)
        return path

    def get_bdl(self):
        if IS_ANDROID:
            folder = os.path.join(app_storage_path(), "bin")
            os.makedirs(folder, exist_ok=True)
            target = os.path.join(folder, "bdl")
            if not os.path.exists(target):
                am = AssetManager()
                data = am.read("assets/bdl-android-aarch64")
                with open(target, "wb") as f:
                    f.write(data)
                os.chmod(target, 0o755)
            return target
        return "./bdl"

    def open_quality(self, x):
        self.menu.open()

    def set_quality(self, name, value):
        self.quality_btn.text = name
        self.quality_value = value
        self.menu.dismiss()

    @mainthread
    def log_add(self, text):
        self.log.text += text + "\n"

    def save_cookie(self):
        with open(
            cookie_path,
            "w",
            encoding="utf8"
        ) as f:
            json.dump(
                {
                    "cookie": self.cookie_input.text
                },
                f,
                ensure_ascii=False
            )
        self.log_add("✅ Cookie已保存")

    def load_cookie(self):
        if os.path.exists(cookie_path):
            try:
                with open(
                    cookie_path,
                    encoding="utf8"
                ) as f:
                    self.cookie_input.text = json.load(f).get(
                        "cookie",
                        ""
                    )
            except:
                pass

    def start_download(self, x):
        url = self.url_input.text.strip()
        if not url:
            self.log_add("⚠️ 请输入B站链接")
            return
        if self.is_downloading:
            self.log_add("⚠️ 下载任务正在运行")
            return
        self.is_downloading = True
        self.download_btn.disabled = True
        threading.Thread(
            target=self.download,
            args=(url,),
            daemon=True
        ).start()

    def download(self, url):
        # 移除 --template 参数，先保证基础功能稳定
        cmd = [
            self.bdl,
            url,
            "--output",
            self.video_dir
        ]

        if self.cookie_input.text.strip():
            cmd.extend([
                "--cookie",
                self.cookie_input.text.strip()
            ])
        if self.quality_value is not None:
            cmd.extend([
                "--quality",
                str(self.quality_value)
            ])
        if self.danmaku.active:
            cmd.append("--danmaku")

        try:
            self.log_add("▶ 开始下载")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf8",
                errors="ignore"
            )
            for line in process.stdout:
                self.log_add(line.rstrip())
            code = process.wait()
            if code == 0:
                self.log_add("✅ 下载完成")
                if self.sm.has_screen("library"):
                    screen = self.sm.get_screen("library")
                    if hasattr(screen, "library_page"):
                        screen.library_page.refresh()
            else:
                self.log_add(f"❌ 下载失败，退出码:{code}")
        except Exception as e:
            self.log_add(f"❌ 错误:{e}")
        finally:
            self.is_downloading = False
            self.download_btn.disabled = False


class LibraryPage(MDBoxLayout):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.sm = sm
        self.orientation = "vertical"
        self.spacing = 10
        self.padding = 20

        back = MDFlatButton(text="返回下载")
        back.bind(
            on_press=lambda x: setattr(self.sm, "current", "download")
        )
        self.add_widget(back)

        self.list_box = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )
        self.list_box.bind(
            minimum_height=self.list_box.setter("height")
        )
        self.add_widget(self.list_box)

    def refresh(self):
        self.list_box.clear_widgets()
        folder = self.get_folder()
        if not os.path.exists(folder):
            return
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            if os.path.isfile(path) and name.lower().endswith((".mp4", ".mkv", ".m4a", ".mp3")):
                row = MDBoxLayout(size_hint_y=None, height=60)
                row.add_widget(MDLabel(text=name))
                btn = MDRaisedButton(text="导出到手机")
                btn.bind(on_press=lambda x, n=name: self.export_file(n))
                row.add_widget(btn)
                self.list_box.add_widget(row)

    def get_folder(self):
        if IS_ANDROID:
            return os.path.join(
                app_storage_path(),
                "BiliPink",
                "Videos"
            )
        return "./BiliPink/Videos"

    def export_file(self, name):
        src = os.path.join(self.get_folder(), name)
        if not os.path.exists(src):
            return
        if IS_ANDROID:
            dst_dir = os.path.join(
                primary_external_storage_path(),
                "Download",
                "BiliPink"
            )
        else:
            dst_dir = "./Export"
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, os.path.join(dst_dir, name))


class DownloadScreen(Screen):
    pass


class LibraryScreen(Screen):
    def on_enter(self):
        if hasattr(self, "library_page"):
            self.library_page.refresh()


class BiliPinkApp(MDApp):
    def build(self):
        self.title = "BiliPink"
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.theme_style = "Light"

        sm = ScreenManager()

        download_screen = DownloadScreen(name="download")
        download_page = DownloadPage(sm)
        download_screen.add_widget(download_page)

        library_screen = LibraryScreen(name="library")
        library_page = LibraryPage(sm)
        library_screen.library_page = library_page
        library_screen.add_widget(library_page)

        sm.add_widget(download_screen)
        sm.add_widget(library_screen)
        return sm


if __name__ == "__main__":
    BiliPinkApp().run()
