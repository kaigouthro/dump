import unittest
from metaloom.core.states import StatusItem, StatusList

class TestStatusItem(unittest.TestCase):
    def test_set(self):
        item = StatusItem("test")
        item.set("complete", 100)
        self.assertEqual(item.get(), {"status": "✅ Complete", "value": "100"})

    def test_get(self):
        item = StatusItem("test")
        item.set("in_progress", "yay")
        self.assertEqual(item.get(), {"status": "in_progress", "value": "yay"})

    def test_str(self):
        item = StatusItem("test")
        item.set("error", "Something went wrong")
        self.assertEqual(str(item), "❗️ Error Something went wrong")

    def test_eq(self):
        item1 = StatusItem("test")
        item1.set("success")
        item2 = StatusItem("test")
        item2.set("success")
        self.assertEqual(item1, item2)

class TestStatusList(unittest.TestCase):
    def test_add(self):
        status_list = StatusList()
        status_list.add("status1", "in_progress", 50)
        self.assertEqual(len(status_list), 1)

    def test_remove(self):
        status_list = StatusList()
        status_list.add("status1", "in_progress", 50)
        status_list.remove("status1")
        self.assertEqual(len(status_list), 0)

    def test_clear_items(self):
        status_list = StatusList()
        status_list.add("status1", "in_progress", 50)
        status_list.clear_items()
        self.assertEqual(len(status_list), 0)

    def test_getitem(self):
        status_list = StatusList()
        status_list.add("status1", "in_progress", 50)
        item = status_list["status1"]
        self.assertIsInstance(item, StatusItem)

    def test_setitem(self):
        status_list = StatusList()
        item = StatusItem("status1")
        status_list["status1"] = item
        self.assertEqual(status_list["status1"], item)

    def test_delitem(self):
        status_list = StatusList()
        status_list.add("status1", "in_progress", 50)
        del status_list["status1"]
        self.assertEqual(len(status_list), 0)

if __name__ == "__main__":
    unittest.main()
