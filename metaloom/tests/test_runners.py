import unittest
from metaloom.core.runners import Runner, StatusItem

class TestRunner(unittest.TestCase):
    def setUp(self):
        self.runner = Runner("test_runner", "Test Runner")

    def test_init(self):
        self.assertEqual(self.runner.name, "test_runner")
        self.assertEqual(self.runner.description, "Test Runner")
        self.assertIsInstance(self.runner.status, StatusItem)
        self.assertIsNone(self.runner.runnable)


    def test_base(self):
        config = {"param1": "value1", "param2": "value2"}
        self.runner.base(config)
        self.assertIsNotNone(self.runner.runnable)

    def test_function(self):
        def test_func(x):
            return x * 2
        self.runner.function(test_func)
        self.assertIsNotNone(self.runner.runnable)

    def test_passthrough(self):
        self.runner.passthrough()
        self.assertIsNotNone(self.runner.runnable)

    def test_call(self):
        def test_func(x):
            return x * 2
        self.runner.function(test_func)
        result = self.runner.invoke(5)
        self.assertEqual(result, 10)
        self.assertEqual(self.runner.status.get(), {"status": "✅ Complete", "value": "None"})

    def test_call_exception(self):
        def test_func(x):
            raise ValueError("Invalid value")
        self.runner.function(test_func)
        with self.assertRaises(ValueError):
            self.runner.invoke(5)
        self.assertEqual(self.runner.status.get(), {"status": "❗️ Error", "value": "Invalid value"})





if __name__ == "__main__":
    unittest.main()
