#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# updated Lululla 05/06/2023
# updated Lululla 30/04/2024
# updated Lululla 30/08/2024
# updated Lululla 22/09/2024
# updated Lululla 17/11/2024
# updated Lululla 26/05/2025
# updated Lululla 17/12/2025
# by 2boom 4bob@ua.fm

import gettext
from os import remove, popen
from os.path import exists
from os.path import isfile, basename
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
from . import __version__ as version

path_folder_log = '/media/hdd/'


def _(txt):
    t = gettext.dgettext("CrashlogViewer", txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def isMountReadonly(mnt):
    try:
        with open("/proc/mounts", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) < 4:
                    continue
                device, mp, fs, flags = parts[:4]
                if mp == mnt:
                    return "ro" in flags
    except IOError as e:
        print("I/O error: %s" % str(e))
    except Exception as err:
        print("Error: %s" % str(err))
    return False


def get_log_path():
    """Get the primary log directory path"""
    try:
        path_folder_log = config.crash.debug_path.value
        if path_folder_log and exists(
                path_folder_log) and not isMountReadonly(path_folder_log):
            return path_folder_log.rstrip('/') + '/'
    except (KeyError, AttributeError):
        pass

    possible_paths = paths()
    for path in possible_paths:
        if exists(path) and not isMountReadonly(path):
            return path.rstrip('/') + '/'

    return "/tmp/"


def paths():
    return [
        "/media/hdd",
        "/media/usb",
        "/media/mmc",
        "/home/root",
        "/home/root/logs/",
        "/media/hdd/logs",
        "/media/usb/logs",
        "/ba/",
        "/ba/logs",
        "/tmp/"]


def find_log_files():
    """Find all crash log files - FIXED VERSION"""
    import glob

    log_files = []

    # Search patterns that include /tmp
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

    # Get primary path
    primary_path = get_log_path()
    if primary_path and primary_path not in ["/tmp/", "/home/root/"]:
        search_patterns.extend([
            "%s*crash*.log" % primary_path,
            "%slogs/*crash*.log" % primary_path,
            "%stwisted.log" % primary_path
        ])

    # Search all patterns
    for pattern in search_patterns:
        try:
            found_files = glob.glob(pattern)
            for file_path in found_files:
                # Check if it's a file and not a directory
                if isfile(file_path) and file_path not in log_files:
                    # Check if it's really a crash log
                    filename = basename(file_path).lower()
                    if ('crash' in filename or
                            'error' in filename or
                            'log' in filename):  # Accept all .log files
                        log_files.append(file_path)
        except BaseException:
            pass

    # Also check specific known files
    specific_files = [
        "/tmp/enigma2_crash.log",
        "/home/root/enigma2_crash.log",
        "/tmp/Enigma2-Crash.log",
        "/tmp/crash.log",
        "/tmp/crash_log.log"
    ]

    for file_path in specific_files:
        if isfile(file_path) and file_path not in log_files:
            log_files.append(file_path)

    return log_files


def delete_log_files(files):
    for file in files:
        try:
            remove(file)
            print('CrashLogScreen file deletedt: %s' % file)
        except OSError as e:
            print("Error while deleting %s error %s:" % (file, str(e)))


class CrashLogScreen(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w == 2560:
        skin = """
        <screen name="crashlogscreen" position="center,center" size="1280,1000" title="View or Remove Crashlog files">
        <widget source="Redkey" render="Label" position="160,900" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="415,900" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Yellowkey" render="Label" position="670,900" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Bluekey" render="Label" position="925,900" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="160,948" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="415,948" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#00ffff00" position="670,948" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#000000ff" position="925,948" size="250,6" zPosition="12" />
        <eLabel name="" position="1194,901" size="52,52" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" cornerRadius="26" font="Regular; 17" zPosition="1" text="INFO" />
        <widget source="menu" render="Listbox" position="80,67" size="1137,781" scrollbarMode="showOnDemand">
        <convert type="TemplatedMultiContent">
        {"template": [
            MultiContentEntryText(pos = (80, 5), size = (580, 46), font=0, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 0), # index 2 is the Menu Titel
            MultiContentEntryText(pos = (80, 55), size = (580, 38), font=1, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 1), # index 3 is the Description
            MultiContentEntryPixmapAlphaTest(pos = (5, 35), size = (51, 40), png = 2), # index 4 is the pixmap
                ],
        "fonts": [gFont("Regular", 42),gFont("Regular", 34)],
        "itemHeight": 100
        }
                </convert>
            </widget>
        </screen>
        """

    elif sz_w == 1920:
        skin = """
        <screen name="crashlogscreen" position="center,center" size="1000,880" title="View or Remove Crashlog files">
        <widget source="Redkey" render="Label" position="0,814" size="250,45" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="252,813" size="250,45" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Yellowkey" render="Label" position="499,814" size="250,45" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Bluekey" render="Label" position="749,814" size="250,45" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="0,858" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="250,858" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#00ffff00" position="500,858" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#000000ff" position="750,858" size="250,6" zPosition="12" />
        <eLabel name="" position="933,753" size="52,52" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" cornerRadius="26" font="Regular; 17" zPosition="1" text="INFO" />
        <widget source="menu" render="Listbox" position="20,10" size="961,781" scrollbarMode="showOnDemand">
        <convert type="TemplatedMultiContent">
        {"template": [
            MultiContentEntryText(pos = (70, 2), size = (580, 34), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
            MultiContentEntryText(pos = (80, 29), size = (580, 30), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
            MultiContentEntryPixmapAlphaTest(pos = (5, 15), size = (51, 40), png = 2), # index 4 is the pixmap
                ],
        "fonts": [gFont("Regular", 30),gFont("Regular", 26)],
        "itemHeight": 70
        }
                </convert>
            </widget>
        </screen>
        """
    else:
        skin = """
        <screen name="crashlogscreen" position="center,center" size="640,586" title="View or Remove Crashlog files">
        <widget source="Redkey" render="Label" position="6,536" size="160,35" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="166,536" size="160,35" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Yellowkey" render="Label" position="325,536" size="160,35" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Bluekey" render="Label" position="485,536" size="160,35" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="5,570" size="160,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="165,570" size="160,6" zPosition="12" />
        <eLabel backgroundColor="#00ffff00" position="325,570" size="160,6" zPosition="12" />
        <eLabel backgroundColor="#000000ff" position="480,570" size="160,6" zPosition="12" />
        <eLabel name="" position="586,495" size="42,35" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" cornerRadius="26" font="Regular; 14" zPosition="1" text="INFO" />
        <widget source="menu" render="Listbox" position="13,6" size="613,517" scrollbarMode="showOnDemand">
        <convert type="TemplatedMultiContent">
        {"template": [
            MultiContentEntryText(pos = (46, 1), size = (386, 22), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
            MultiContentEntryText(pos = (53, 19), size = (386, 20), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
            MultiContentEntryPixmapAlphaTest(pos = (3, 10), size = (34, 26), png = 2), # index 4 is the pixmap
                ],
        "fonts": [gFont("Regular", 18),gFont("Regular", 16)],
        "itemHeight": 50
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
                "ok": self.Ok,
                "cancel": self.exit,
                "back": self.exit,
                "red": self.exit,
                "green": self.Ok,
                "yellow": self.YellowKey,
                "blue": self.BlueKey,
                "info": self.infoKey,
                "up": self.pageUp,
                "down": self.pageDown,
            }
        )
        self["Redkey"] = StaticText(_("Close"))
        self["Greenkey"] = StaticText(_("View"))
        self["Yellowkey"] = StaticText(_("Remove"))
        self["Bluekey"] = StaticText(_("Remove All"))
        self.in_confirm_mode = False
        self.showing_info = False
        self.list = []
        self["menu"] = List(self.list)
        self.CfgMenu()

    def CfgMenu(self):
        self.list = []
        path_folder_log = "/tmp/"
        log_files = find_log_files()
        if log_files:
            paths_to_search = " ".join(log_files)
        else:
            paths_to_search = (
                "%s*crash*.log "
                "%slogs/*crash*.log "
                "/home/root/*crash*.log "
                "/home/root/logs/*crash*.log "
                "%stwisted.log "
                "/media/usb/logs/*crash*.log "
                "/media/usb/*crash*.log "
                "/media/hdd/logs/*crash*.log "
                "/media/mmc/*crash*.log "
                "/media/hdd/*crash*.log "
                "/ba/*crash*.log "
                "/ba/logs/*crash*.log"
            ) % (path_folder_log, path_folder_log, path_folder_log)

        crashfiles = popen("ls -lh " + paths_to_search).read()
        sz_w = getDesktop(0).size().width()
        if sz_w == 2560:
            minipng = LoadPixmap(
                cached=True,
                path=resolveFilename(
                    SCOPE_PLUGINS,
                    "Extensions/CrashlogViewer/images/crashminiwq.png"))
        elif sz_w == 1920:
            minipng = LoadPixmap(
                cached=True,
                path=resolveFilename(
                    SCOPE_PLUGINS,
                    "Extensions/CrashlogViewer/images/crashmini.png"))
        else:
            minipng = LoadPixmap(
                cached=True,
                path=resolveFilename(
                    SCOPE_PLUGINS,
                    "Extensions/CrashlogViewer/images/crashmini1.png"))

        for line in crashfiles.splitlines():
            item = line.split()
            if len(item) >= 9:
                file_size = item[4]
                file_date = " ".join(item[5:8])
                file_name = item[8]
                display_name = (file_name.split("/")[-1],
                                "Dimensione: %s - Data: %s" % (file_size, file_date),
                                minipng,
                                file_name)
                if display_name not in self.list:
                    self.list.append(display_name)

        self["menu"].setList(self.list)

    def Ok(self):
        item = self["menu"].getCurrent()
        try:
            base_dir = item[3]
            crashfile = str(base_dir)
            self.session.openWithCallback(self.CfgMenu, CrashLogView, crashfile)
        except (IndexError, TypeError, KeyError) as e:
            print('CrashLogScreen error to select: %s' % e)
            crashfile = " "

    def pageUp(self):
        current_index = self["menu"].getIndex()
        if current_index > 0:
            self["menu"].setIndex(current_index - 1)

    def pageDown(self):
        current_index = self["menu"].getIndex()
        list_length = len(self.list)
        if current_index < list_length - 1:
            self["menu"].setIndex(current_index + 1)

    def YellowKey(self):
        if self.in_confirm_mode:
            return

        item = self["menu"].getCurrent()

        if not item or len(item) < 4 or not item[3]:
            self.showTempMessage(_("No file selected"), 1500)
            return

        file_path = str(item[3])

        if not exists(file_path):
            self.showTempMessage(_("File already removed"), 1500)
            self.CfgMenu()
            return

        try:
            remove(file_path)

            original_title = self.getTitle()
            self.setTitle(_("Removed: %s") % basename(file_path))

            self.CfgMenu()

            timer = eTimer()
            timer.callback.append(lambda: self.setTitle(original_title))
            timer.start(1500, True)

        except Exception as e:
            original_title = self.getTitle()
            self.setTitle(_("Error: %s") % str(e))

            timer = eTimer()
            timer.callback.append(lambda: self.setTitle(original_title))
            timer.start(2000, True)

    def BlueKey(self):
        """Delete all crash log files"""
        if self.in_confirm_mode:
            return

        try:
            log_files = find_log_files()
            if not log_files:
                self.showTempMessage(_("No crash logs found"), 2000)
                return

            original_title = self.getTitle()

            deleted = 0
            for file_path in log_files:
                try:
                    if exists(file_path):
                        remove(file_path)
                        deleted += 1
                except Exception:
                    pass

            if deleted > 0:
                self.setTitle(_("Deleted %d files") % deleted)
            else:
                self.setTitle(_("No files deleted"))

            self.CfgMenu()

            timer = eTimer()
            timer.callback.append(lambda: self.setTitle(original_title))
            timer.start(1500, True)

        except Exception as e:
            original_title = self.getTitle()
            self.setTitle(_("Error: %s") % str(e))
            self.CfgMenu()
            timer = eTimer()
            timer.callback.append(lambda: self.setTitle(original_title))
            timer.start(2000, True)

    def showTempMessage(self, message, duration=2000):
        if self.in_confirm_mode:
            return

        original_title = self.getTitle()
        self.setTitle(message)

        timer = eTimer()
        timer.callback.append(lambda: self.setTitle(original_title))
        timer.start(duration, True)

    def infoKey(self):
        if self.in_confirm_mode:
            return

        original_list = self.list.copy()

        info_items = []

        info_items.append(("=" * 50, "", None, ""))
        info_items.append(("CRASHLOG VIEWER - INFO", "", None, ""))
        info_items.append(("=" * 50, "", None, ""))
        info_items.append(("Version: " + version, "", None, ""))
        info_items.append(("Developer: 2boom", "", None, ""))
        info_items.append(("Modifier: Evg77734", "", None, ""))
        info_items.append(("Update from Lululla", "", None, ""))
        info_items.append(("=" * 50, "", None, ""))
        info_items.append(("Press OK or RED to return", "", None, ""))

        self["menu"].setList(info_items)

        self["Redkey"].setText(_("Back"))
        self["Greenkey"].setText("")
        self["Yellowkey"].setText("")
        self["Bluekey"].setText("")

        self.showing_info = True

        self["shortcuts"].actions.update({
            "ok": self.returnFromInfo,
            "cancel": self.returnFromInfo,
            "red": self.returnFromInfo,
            "green": lambda: None,  # Disabilita
            "yellow": lambda: None,  # Disabilita
            "blue": lambda: None,   # Disabilita
            "info": lambda: None    # Disabilita
        })

    def returnFromInfo(self):
        if hasattr(self, 'showing_info') and self.showing_info:
            self.showing_info = False
            self.CfgMenu()

            self["Redkey"].setText(_("Close"))
            self["Greenkey"].setText(_("View"))
            self["Yellowkey"].setText(_("Remove"))
            self["Bluekey"].setText(_("Remove All"))

            self["shortcuts"].actions.update({
                "ok": self.Ok,
                "cancel": self.exit,
                "back": self.exit,
                "red": self.exit,
                "green": self.Ok,
                "yellow": self.YellowKey,
                "blue": self.BlueKey,
                "info": self.infoKey,
                "up": self.pageUp,
                "down": self.pageDown,
            })

    def exit(self):
        self.close()


class CrashLogView(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w == 1920:
        skin = """
        <screen name="CrashLogView" position="center,center" size="1880,980" title="View Crashlog file">
        <widget source="Redkey" render="Label" position="16,919" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="266,919" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="20,963" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="270,963" size="250,6" zPosition="12" />
        <widget name="text" position="10,70" size="1860,630" font="Console; 24" text="text" /> <!-- Mostra il log completo -->
        <widget name="text2" position="10,720" size="1860,190" font="Console; 26" foregroundColor="#ff0000" /> <!-- Mostra le linee di errore -->
        <eLabel position="10,710" size="1860,2" backgroundColor="#555555" zPosition="1" />
        </screen>
        """
    else:
        skin = """
        <screen name="CrashLogView" position="center,center" size="1253,653" title="View Crashlog file">
        <widget source="Redkey" render="Label" position="19,609" size="172,33" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="191,609" size="172,33" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="20,643" size="172,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="192,643" size="172,6" zPosition="12" />
        <widget name="text" position="6,50" size="1240,420" font="Console; 16" text="text" />
        <widget name="text2" position="6,480" size="1240,126" font="Console; 17" foregroundColor="#ff0000" />
        <eLabel position="6,473" size="1240,1" backgroundColor="#555555" zPosition="1" />
        </screen>
        """

    def __init__(self, session, Crashfile):
        self.session = session
        Screen.__init__(self, session)
        self.crashfile = Crashfile
        self.setTitle("View Crashlog file: " + basename(Crashfile))
        self.current_view = "full"  # "full" o "error"
        self.full_text = ""
        self.error_text = ""
        self["actions"] = ActionMap(
            ["DirectionActions", "ColorActions", "OkCancelActions"],
            {
                "cancel": self.exit,
                "ok": self.exit,
                "red": self.exit,
                "green": self.switchView,
                "up": self.pageUp,
                "down": self.pageDown,
                "left": self.pageUp,
                "right": self.pageDown
            }
        )
        self["Redkey"] = StaticText(_("Close"))
        self["Greenkey"] = StaticText(_("Error Only"))
        self["text"] = ScrollLabel("")
        self["text2"] = ScrollLabel("")
        self.onLayoutFinish.append(self.listcrah)

    def pageUp(self):
        self["text"].pageUp()
        self["text2"].pageUp()

    def pageDown(self):
        self["text"].pageDown()
        self["text2"].pageDown()

    def switchView(self):
        """Switch between full log (top) and error only (bottom)"""
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

    def listcrah(self):
        try:
            with open(self.crashfile, "r") as crashfile:
                content = crashfile.read()
                self.full_text = content

                lines = content.split('\n')
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
                    error_lines = ["No specific error trace found in log"]

                self.error_text = '\n'.join(error_lines)

        except Exception as e:
            error_msg = "Error opening file: %s" % str(e)
            self.full_text = error_msg
            self.error_text = error_msg

        self["text"].setText(self.full_text)
        self["text2"].setText(self.error_text)

        self["text"].show()
        self["text2"].hide()
        self["Greenkey"].setText(_("Error Only"))


def main(session, **kwargs):
    session.open(CrashLogScreen)


def Plugins(**kwargs):
    return PluginDescriptor(
        name=(
            _("Crashlog  Viewer") +
            " ver. " +
            version),
        description=_("View | Remove Crashlog files"),
        where=[
            PluginDescriptor.WHERE_PLUGINMENU,
            PluginDescriptor.WHERE_EXTENSIONSMENU],
        icon="crash.png",
        fnc=main)
