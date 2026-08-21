# coding: latin-1
import json
import os


class WorkspaceState(object):
    def __init__(self):
        self.output_dir = os.path.expanduser(os.path.join("~", "Desktop" ,"output"))
        self.temp_dir   = os.path.expanduser(os.path.join("~", "Desktop" ,"temp"))


    def to_dict(self):
        return {
            "output_dir": self.output_dir,
            "temp_dir": self.temp_dir
        }


    def from_dict(self, data):
        self.output_dir = data.get("output_dir", self.output_dir)
        self.temp_dir = data.get("temp_dir", self.temp_dir)


    def ensure_workspace_exists(self):
        for directory in (self.output_dir, self.temp_dir):
            if directory and not os.path.exists(directory):
                os.makedirs(directory)


class UIState(object):
    def __init__(self):
        self.last_program = None
        self.window_geometry = None


    def to_dict(self):
        return {
            "last_program": self.last_program,
            "window_geometry": self.window_geometry
        }


    def from_dict(self, data):
        self.last_program = data.get("last_program")
        self.window_geometry = data.get("window_geometry")


class ApplicationState(object):
    def __init__(self):
        self.workspace = WorkspaceState()
        self.programs = {}
        self.ui = UIState()


    def to_dict(self):
        return {
            "workspace": self.workspace.to_dict(),
            "programs": self.programs,
            "ui": self.ui.to_dict()
        }


    def from_dict(self, data):
        self.workspace.from_dict(data.get("workspace", {}))
        self.programs = data.get("programs", {})
        self.ui.from_dict(data.get("ui", {}))


    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load(self, filename):
        if not os.path.exists(filename):
            return False

        try:
            with open(filename) as f:
                self.from_dict(json.load(f))
            return True
        except Exception as e:
            print("Error parsing JSON configuration: " + str(e))
            return False
