from typing import Any

class StatusItem:
    def __init__(self, name: str, word: str = str(), value=None):
        self.name = name
        self.content = {
            "aborted"      : {"title": "Aborted", "icon": "⛔️"},
            "cancelled"    : {"title": "Cancelled", "icon": "❌"},
            "cleaning"     : {"title": "Cleaning", "icon": "🧹"},
            "compiling"    : {"title": "Compiling", "icon": "🔨"},
            "complete"     : {"title": "Complete", "icon": "✅"},
            "connecting"   : {"title": "Connecting", "icon": "🔗"},
            "deleting"     : {"title": "Deleting", "icon": "🗑"},
            "disconnecting": {"title": "Disconnecting", "icon": "🔌"},
            "downloading"  : {"title": "Downloading", "icon": "⬇️"},
            "error"        : {"title": "Error", "icon": "❗️"},
            "exporting"    : {"title": "Exporting", "icon": "📤"},
            "failure"      : {"title": "Failure", "icon": "❌"},
            "finished"     : {"title": "Finished", "icon": "🎉"},
            "idle"         : {"title": "Idle", "icon": "🕛"},
            "importing"    : {"title": "Importing", "icon": "📥"},
            "installing"   : {"title": "Installing", "icon": "🔧"},
            "loading"      : {"title": "Loading", "icon": "⏳"},
            "paused"       : {"title": "Paused", "icon": "⏸"},
            "pending"      : {"title": "Pending", "icon": "🕒"},
            "progress"     : {"title": "Progress", "icon": "🔄"},
            "receiving"    : {"title": "Receiving", "icon": "📩"},
            "refreshing"   : {"title": "Refreshing", "icon": "🔄"},
            "rendering"    : {"title": "Rendering", "icon": "🎨"},
            "restarting"   : {"title": "Restarting", "icon": "🔄"},
            "resuming"     : {"title": "Resuming", "icon": "▶️"},
            "running"      : {"title": "Running", "icon": "🏃"},
            "saving"       : {"title": "Saving", "icon": "💾"},
            "scanning"     : {"title": "Scanning", "icon": "🔍"},
            "sending"      : {"title": "Sending", "icon": "📤"},
            "size"         : {"title": "Size", "icon": "📐"},
            "started"      : {"title": "Started", "icon": "🚀"},
            "success"      : {"title": "Success", "icon": "✅"},
            "syncing"      : {"title": "Syncing", "icon": "🔄"},
            "uninstalling" : {"title": "Uninstalling", "icon": "🔧"},
            "updating"     : {"title": "Updating", "icon": "🔃"},
            "uploading"    : {"title": "Uploading", "icon": "⬆️"},
            "validating"   : {"title": "Validating", "icon": "✅"},
            "verifying"    : {"title": "Verifying", "icon": "✅"},
            "waiting"      : {"title": "Waiting", "icon": "⌛️"},
        }
        self.status = {"status": "", "value": ""}
        self.set(word or "", value or "")

    def set(self, word: str, value: str | float | int | bool | dict | None = None):
        """
        outtput to status: an icon and status word, as well as the state if exists
        """
        if word in self.content:
            self.status["status"] = f"{ self.content[word]['icon']} {self.content[word]['title']}"
        else:
            self.status["status"] = word or ""

        if value in self.content:
            self.status["value"] = f"{ self.content[str(value)]['title']}"
        else:
            self.status["value"] = str(value)

        return self.status

    def get(self):
        return self.status

    def __str__(self):
        return self.status["status"] + " " + str(self.status["value"])

    def __repr__(self):
        return self.status["status"] + " " + str(self.status["value"])

    def __eq__(self, other: Any):
        if not isinstance(other, StatusItem):
            return self.status["value"] == other
        return self.status["value"] == other.status["value"]

    def __hash__(self):
        return hash(self.status["value"])

    def __lt__(self, other: Any):
        if not isinstance(other, StatusItem):
            return self.status["value"] < other
        return self.status["value"] < other.status["value"]

    def __gt__(self, other: Any):
        if not isinstance(other, StatusItem):
            return self.status["value"] > other
        return self.status["value"] > other.status["value"]

    def __le__(self, other: Any):
        if not isinstance(other, StatusItem):
            return self.status["value"] <= other
        return self.status["value"] <= other.status["value"]

    def __ge__(self, other: Any):
        if not isinstance(other, StatusItem):
            return self.status["value"] >= other
        return self.status["value"] >= other.status["value"]

    def __ne__(self, other: Any):
        if not isinstance(other, StatusItem):
            return self.status["value"] != other
        return self.status["value"] != other.status["value"]

    def __add__(self, other: Any):
        if not isinstance(other, StatusItem):
            return self.status["value"] + other
        return self.status["value"] + other.status["value"]

class StatusList:
    """List of StatusList Container"""

    def __init__(self):
        self.items = {}

    def add(self, name, status=None, value=None):
        self.items.update({name: StatusItem(name, status or "pending", value)})

    def remove(self, name):
        self.items.pop(name)

    def clear_items(self):
        self.items.clear()

    def set_status(self, name, status, value=None):
        self.items[name].set(status, value)

    def set_idle(self, name):
        self.items[name].set("idle")

    def set_success(self, name):
        self.items[name].set("success")

    def set_error(self, name, error):
        self.items[name].set("error", error)

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __str__(self):
        return str(self.items)  # return all status in items

    def __repr__(self):
        return str(self.items)  # return all status in items

    def __getitem__(self, name):
        return self.items[name]

    def __setitem__(self, name, value):
        self.items[name] = value

    def __delitem__(self, name):
        del self.items[name]


if __name__ == "__main__":
    sl = StatusList()
    # add a dozen various statuses
    for i in range(12):
        sl.add(f"status {i}")
    print(sl)
