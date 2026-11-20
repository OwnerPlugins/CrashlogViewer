#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import time
from os.path import exists, isfile, basename

from enigma import getDesktop, eTimer
from Components.config import config
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from Tools.LoadPixmap import LoadPixmap

from . import _, __version__ as version


def isMountReadonly(mnt):
    """Check if a mount point is read-only."""
    try:
        with open("/proc/mounts", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) < 4:
                    continue
                device, mp, fs, flags = parts[:4]
                if mp == mnt:
                    return "ro" in flags
    except Exception as e:
        print("isMountReadonly error: %s" % str(e))
    return False


def get_log_path():
    """Get the primary log directory from Enigma2 config, or fallback."""
    try:
        path = config.crash.debug_path.value
        if path and exists(path) and not isMountReadonly(path):
            return path.rstrip('/') + '/'
    except (KeyError, AttributeError):
        pass

    for path in [
        "/media/hdd",
        "/media/usb",
        "/media/mmc",
        "/home/root",
        "/home/root/logs/",
        "/media/hdd/logs",
        "/media/usb/logs",
        "/ba/",
        "/ba/logs",
        "/tmp/"
    ]:
        if exists(path) and not isMountReadonly(path):
            return path.rstrip('/') + '/'
    return "/tmp/"


def find_log_files():
    """Return a list of all crash log files (full paths)."""
    log_files = []
    search_patterns = [
        "/tmp/*crash*.log",
        "/tmp/*.log",
        "/home/root/*crash*.log",
        "/home/root/logs/*crash*.log",
        "/media/hdd/*crash*.log",
        "/media/hdd/logs/*crash*.log",
        "/media/usb/*crash*.log",
        "/media/usb/logs/*crash*.log",
        "/media/mmc/*crash*.log",
        "/ba/*crash*.log",
        "/ba/logs/*crash*.log"
    ]

    primary = get_log_path()
    if primary and primary not in ["/tmp/", "/home/root/"]:
        search_patterns.extend([
            primary + "*crash*.log",
            primary + "logs/*crash*.log",
            primary + "twisted.log"
        ])

    for pattern in search_patterns:
        try:
            for path in glob.glob(pattern):
                if isfile(path) and path not in log_files:
                    # Accept all .log files (avoid filtering too strictly)
                    log_files.append(path)
        except Exception:
            pass

    # Additional known specific files
    specific = [
        "/tmp/enigma2_crash.log",
        "/home/root/enigma2_crash.log",
        "/tmp/Enigma2-Crash.log",
        "/tmp/crash.log",
        "/tmp/crash_log.log"
    ]
    for path in specific:
        if isfile(path) and path not in log_files:
            log_files.append(path)

    return log_files


class CrashLogScreen(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w == 2560:
        skin = """
        <screen name="crashlogscreen" position="center,center" size="2560,1440" title="View or Remove Crashlog files">
        <widget source="Redkey" render="Label" position="120,1280" size="460,80" zPosition="11" font="Regular; 52" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="590,1280" size="460,80" zPosition="11" font="Regular; 52" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Yellowkey" render="Label" position="1060,1280" size="460,80" zPosition="11" font="Regular; 52" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Bluekey" render="Label" position="1530,1280" size="460,80" zPosition="11" font="Regular; 52" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="120,1360" size="460,10" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="590,1360" size="460,10" zPosition="12" />
        <eLabel backgroundColor="#00ffff00" position="1060,1360" size="460,10" zPosition="12" />
        <eLabel backgroundColor="#000000ff" position="1530,1360" size="460,10" zPosition="12" />
        <eLabel name="" position="2020,1275" size="380,100" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" cornerRadius="26" font="Regular; 30" zPosition="1" text="INFO" />
        <widget source="menu" render="Listbox" position="160,140" size="2240,1100" scrollbarMode="showOnDemand">
        <convert type="TemplatedMultiContent">
        {"template": [
            MultiContentEntryText(pos = (160, 8), size = (1160, 74), font=0, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 0),
            MultiContentEntryText(pos = (160, 88), size = (1160, 60), font=1, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 1),
            MultiContentEntryPixmapAlphaTest(pos = (10, 56), size = (82, 64), png = 2),
                ],
        "fonts": [gFont("Regular", 68),gFont("Regular", 56)],
        "itemHeight": 160
        }
                </convert>
            </widget>
        </screen>
        """
    elif sz_w == 1920:
        skin = """
        <screen name="crashlogscreen" position="center,center" size="1920,1080" title="View or Remove Crashlog files">
        <widget source="Redkey" render="Label" position="90,960" size="345,60" zPosition="11" font="Regular; 40" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="445,960" size="345,60" zPosition="11" font="Regular; 40" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Yellowkey" render="Label" position="800,960" size="345,60" zPosition="11" font="Regular; 40" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Bluekey" render="Label" position="1155,960" size="345,60" zPosition="11" font="Regular; 40" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="90,1020" size="345,8" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="445,1020" size="345,8" zPosition="12" />
        <eLabel backgroundColor="#00ffff00" position="800,1020" size="345,8" zPosition="12" />
        <eLabel backgroundColor="#000000ff" position="1155,1020" size="345,8" zPosition="12" />
        <eLabel name="" position="1520,955" size="260,75" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" cornerRadius="26" font="Regular; 24" zPosition="1" text="INFO" />
        <widget source="menu" render="Listbox" position="120,105" size="1680,825" scrollbarMode="showOnDemand">
        <convert type="TemplatedMultiContent">
        {"template": [
            MultiContentEntryText(pos = (120, 6), size = (870, 56), font=0, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 0),
            MultiContentEntryText(pos = (120, 66), size = (870, 46), font=1, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 1),
            MultiContentEntryPixmapAlphaTest(pos = (8, 42), size = (60, 48), png = 2),
                ],
        "fonts": [gFont("Regular", 50),gFont("Regular", 40)],
        "itemHeight": 120
        }
                </convert>
            </widget>
        </screen>
        """
    else:
        skin = """
        <screen name="crashlogscreen" position="center,center" size="1280,720" title="View or Remove Crashlog files">
        <widget source="Redkey" render="Label" position="60,640" size="230,40" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="300,640" size="230,40" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Yellowkey" render="Label" position="540,640" size="230,40" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Bluekey" render="Label" position="780,640" size="230,40" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="60,680" size="230,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="300,680" size="230,6" zPosition="12" />
        <eLabel backgroundColor="#00ffff00" position="540,680" size="230,6" zPosition="12" />
        <eLabel backgroundColor="#000000ff" position="780,680" size="230,6" zPosition="12" />
        <eLabel name="" position="1025,640" size="180,48" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" cornerRadius="26" font="Regular; 17" zPosition="1" text="INFO" />
        <widget source="menu" render="Listbox" position="80,70" size="1120,550" scrollbarMode="showOnDemand">
        <convert type="TemplatedMultiContent">
        {"template": [
            MultiContentEntryText(pos = (80, 4), size = (580, 36), font=0, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 0),
            MultiContentEntryText(pos = (80, 44), size = (580, 30), font=1, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 1),
            MultiContentEntryPixmapAlphaTest(pos = (5, 28), size = (40, 32), png = 2),
                ],
        "fonts": [gFont("Regular", 34),gFont("Regular", 28)],
        "itemHeight": 80
        }
                </convert>
            </widget>
        </screen>
        """

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self["shortcuts"] = ActionMap(
            ["ShortcutActions", "WizardActions", "EPGSelectActions"],
            {
                "ok": self.ok,
                "cancel": self.exit,
                "back": self.exit,
                "red": self.exit,
                "green": self.ok,
                "yellow": self.yellow_key,
                "blue": self.blue_key,
                "info": self.info_key,
                "up": self.page_up,
                "down": self.page_down,
            }
        )
        self["Redkey"] = StaticText(_("Close"))
        self["Greenkey"] = StaticText(_("View"))
        self["Yellowkey"] = StaticText(_("Remove"))
        self["Bluekey"] = StaticText(_("Remove All"))

        self.in_info_mode = False
        self.timer = None
        self.list = []
        self["menu"] = List(self.list)
        self.refresh_menu()

    def refresh_menu(self):
        """Build the list of crash logs using find_log_files() and os.stat."""
        self.list = []
        log_files = find_log_files()

        # Choose icon based on screen width
        sz_w = getDesktop(0).size().width()
        if sz_w == 2560:
            icon = LoadPixmap(
                cached=True,
                path=resolveFilename(
                    SCOPE_PLUGINS,
                    "Extensions/CrashlogViewer/images/crashminiwq.png"))
        elif sz_w == 1920:
            icon = LoadPixmap(
                cached=True,
                path=resolveFilename(
                    SCOPE_PLUGINS,
                    "Extensions/CrashlogViewer/images/crashmini.png"))
        else:
            icon = LoadPixmap(
                cached=True,
                path=resolveFilename(
                    SCOPE_PLUGINS,
                    "Extensions/CrashlogViewer/images/crashmini1.png"))

        for path in log_files:
            try:
                st = os.stat(path)
                size_bytes = st.st_size
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"

                mtime = st.st_mtime
                date_str = time.strftime(
                    "%Y-%m-%d %H:%M", time.localtime(mtime))

                display_tuple = (
                    basename(path),
                    f"{_('Size')}: {size_str} - {_('Date')}: {date_str}",
                    icon,
                    path)
                self.list.append(display_tuple)
            except Exception as e:
                print(f"Error reading {path}: {e}")

        self["menu"].setList(self.list)

    def ok(self):
        if self.in_info_mode:
            self.exit_info_mode()
            return
        item = self["menu"].getCurrent()
        if not item or len(item) < 4:
            self.show_temp_message(_("No file selected"), 1500)
            return
        file_path = str(item[3])
        self.session.openWithCallback(
            self.refresh_menu, CrashLogView, file_path)

    def page_up(self):
        if self.in_info_mode:
            return
        idx = self["menu"].getIndex()
        if idx > 0:
            self["menu"].setIndex(idx - 1)

    def page_down(self):
        if self.in_info_mode:
            return
        idx = self["menu"].getIndex()
        if idx < len(self.list) - 1:
            self["menu"].setIndex(idx + 1)

    def yellow_key(self):
        if self.in_info_mode:
            return
        item = self["menu"].getCurrent()
        if not item or len(item) < 4:
            self.show_temp_message(_("No file selected"), 1500)
            return
        file_path = str(item[3])
        if not exists(file_path):
            self.show_temp_message(_("File already removed"), 1500)
            self.refresh_menu()
            return
        try:
            os.remove(file_path)
            original_title = self.getTitle()
            self.setTitle(_("Removed: %s") % basename(file_path))
            self.refresh_menu()
            self._restore_title_after(1500, original_title)
        except Exception as e:
            original_title = self.getTitle()
            self.setTitle(_("Error: %s") % str(e))
            self._restore_title_after(2000, original_title)

    def blue_key(self):
        if self.in_info_mode:
            return
        log_files = find_log_files()
        if not log_files:
            self.show_temp_message(_("No crash logs found"), 2000)
            return
        deleted = 0
        for path in log_files:
            try:
                if exists(path):
                    os.remove(path)
                    deleted += 1
            except Exception:
                pass
        original_title = self.getTitle()
        if deleted > 0:
            self.setTitle(_("Deleted %d files") % deleted)
        else:
            self.setTitle(_("No files deleted"))
        self.refresh_menu()
        self._restore_title_after(1500, original_title)

    def show_temp_message(self, message, duration):
        if self.in_info_mode:
            return
        original = self.getTitle()
        self.setTitle(message)
        self._restore_title_after(duration, original)

    def _restore_title_after(self, ms, original_title):
        if self.timer and self.timer.isActive():
            self.timer.stop()
        self.timer = eTimer()
        self.timer.callback.append(
            lambda: self._set_title_safe(original_title))
        self.timer.start(ms, True)

    def _set_title_safe(self, title):
        if self and hasattr(self, 'setTitle'):
            self.setTitle(title)

    def info_key(self):
        if self.in_info_mode:
            return
        self.in_info_mode = True

        # Store original list and button texts
        self.original_list = self.list.copy()
        self.original_red = self["Redkey"].getText()
        self.original_green = self["Greenkey"].getText()
        self.original_yellow = self["Yellowkey"].getText()
        self.original_blue = self["Bluekey"].getText()

        info_items = [
            ("=" * 50, "", None, ""),
            ("CRASHLOG VIEWER - INFO", "", None, ""),
            ("=" * 50, "", None, ""),
            (f"{_('Version')}: {version}", "", None, ""),
            (f"{_('Developer')}: 2boom", "", None, ""),
            (f"{_('Modifier')}: Evg77734", "", None, ""),
            (f"{_('Update from')}: Lululla", "", None, ""),
            ("=" * 50, "", None, ""),
            (_("Press OK or RED to return"), "", None, "")
        ]
        self["menu"].setList(info_items)

        self["Redkey"].setText(_("Back"))
        self["Greenkey"].setText("")
        self["Yellowkey"].setText("")
        self["Bluekey"].setText("")

        # Remap keys temporarily
        self["shortcuts"].actions.update({
            "ok": self.exit_info_mode,
            "cancel": self.exit_info_mode,
            "red": self.exit_info_mode,
            "green": lambda: None,
            "yellow": lambda: None,
            "blue": lambda: None,
            "info": lambda: None,
            "up": lambda: None,
            "down": lambda: None,
        })

    def exit_info_mode(self):
        if not self.in_info_mode:
            return
        self.in_info_mode = False
        self.refresh_menu()
        self["Redkey"].setText(self.original_red)
        self["Greenkey"].setText(self.original_green)
        self["Yellowkey"].setText(self.original_yellow)
        self["Bluekey"].setText(self.original_blue)
        self["shortcuts"].actions.update({
            "ok": self.ok,
            "cancel": self.exit,
            "back": self.exit,
            "red": self.exit,
            "green": self.ok,
            "yellow": self.yellow_key,
            "blue": self.blue_key,
            "info": self.info_key,
            "up": self.page_up,
            "down": self.page_down,
        })

    def exit(self):
        if self.timer and self.timer.isActive():
            self.timer.stop()
        self.close()


class CrashLogView(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w == 1920:
        skin = """
        <screen name="CrashLogView" position="center,center" size="1920,1080" title="View Crashlog file">
        <widget source="Redkey" render="Label" position="120,1000" size="345,45" zPosition="11" font="Regular; 28" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="490,1000" size="345,45" zPosition="11" font="Regular; 28" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="120,1045" size="345,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="490,1045" size="345,6" zPosition="12" />
        <widget name="text" position="20,80" size="1880,720" font="Console; 20" text="text" />
        <widget name="text2" position="20,810" size="1880,180" font="Console; 22" foregroundColor="#ff0000" />
        <eLabel position="20,800" size="1880,4" backgroundColor="#555555" zPosition="1" />
        </screen>
        """
    elif sz_w == 2560:
        skin = """
        <screen name="CrashLogView" position="center,center" size="2560,1440" title="View Crashlog file">
        <widget source="Redkey" render="Label" position="160,1330" size="460,60" zPosition="11" font="Regular; 36" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="650,1330" size="460,60" zPosition="11" font="Regular; 36" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="160,1390" size="460,8" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="650,1390" size="460,8" zPosition="12" />
        <widget name="text" position="30,100" size="2500,980" font="Console; 26" text="text" />
        <widget name="text2" position="30,1090" size="2500,230" font="Console; 28" foregroundColor="#ff0000" />
        <eLabel position="30,1080" size="2500,6" backgroundColor="#555555" zPosition="1" />
        </screen>
        """
    else:
        skin = """
        <screen name="CrashLogView" position="center,center" size="1280,720" title="View Crashlog file">
        <widget source="Redkey" render="Label" position="80,660" size="230,30" zPosition="11" font="Regular; 18" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="330,660" size="230,30" zPosition="11" font="Regular; 18" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="80,690" size="230,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="330,690" size="230,6" zPosition="12" />
        <widget name="text" position="10,50" size="1260,480" font="Console; 12" text="text" />
        <widget name="text2" position="10,540" size="1260,110" font="Console; 13" foregroundColor="#ff0000" />
        <eLabel position="10,530" size="1260,2" backgroundColor="#555555" zPosition="1" />
        </screen>
        """

    def __init__(self, session, crashfile):
        self.session = session
        Screen.__init__(self, session)
        self.crashfile = crashfile
        self.setTitle(_("View Crashlog file: %s") % basename(crashfile))
        self.current_view = "full"   # "full" or "error"
        self.full_text = ""
        self.error_text = ""

        self["actions"] = ActionMap(
            ["DirectionActions", "ColorActions", "OkCancelActions"],
            {
                "cancel": self.exit,
                "ok": self.exit,
                "red": self.exit,
                "green": self.switch_view,
                "up": self.page_up,
                "down": self.page_down,
                "left": self.page_up,
                "right": self.page_down
            }
        )
        self["Redkey"] = StaticText(_("Close"))
        self["Greenkey"] = StaticText(_("Error Only"))
        self["text"] = ScrollLabel("")
        self["text2"] = ScrollLabel("")
        self.onLayoutFinish.append(self.load_log)

    def page_up(self):
        self["text"].pageUp()
        self["text2"].pageUp()

    def page_down(self):
        self["text"].pageDown()
        self["text2"].pageDown()

    def switch_view(self):
        if self.current_view == "full":
            self.current_view = "error"
            self["text"].hide()
            self["text2"].show()
            self["Greenkey"].setText(_("Full Log"))
        else:
            self.current_view = "full"
            self["text"].show()
            self["text2"].hide()
            self["Greenkey"].setText(_("Error Only"))

        self["text"].lastPage()
        self["text2"].lastPage()

    def exit(self):
        self.close()

    def load_log(self):
        try:
            with open(self.crashfile, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self.full_text = content

            # Try to extract traceback
            lines = content.splitlines()
            error_lines = []
            for i, line in enumerate(lines):
                if "Traceback (most recent call last):" in line or "Backtrace:" in line:
                    for j in range(i, min(i + 20, len(lines))):
                        error_lines.append(lines[j])
                    break
            if not error_lines:
                for line in lines:
                    if "Error:" in line or "Exception:" in line or "FATAL" in line:
                        error_lines.append(line)
            if not error_lines:
                error_lines = [_("No specific error trace found in log")]

            self.error_text = "\n".join(error_lines)

        except Exception as e:
            msg = _("Error opening file: %s") % str(e)
            self.full_text = msg
            self.error_text = msg

        self["text"].setText(self.full_text)
        self["text2"].setText(self.error_text)

        self["text"].show()
        self["text2"].hide()
        self["Greenkey"].setText(_("Error Only"))


def main(session, **kwargs):
    session.open(CrashLogScreen)


def Plugins(**kwargs):
    return PluginDescriptor(
        name=_("Crashlog Viewer") + " ver. " + version,
        description=_("View | Remove Crashlog files"),
        where=[
            PluginDescriptor.WHERE_PLUGINMENU,
            PluginDescriptor.WHERE_EXTENSIONSMENU],
        icon="crash.png",
        fnc=main)
