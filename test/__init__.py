import unittest

class AsesTestRunner(unittest.TextTestRunner):
    """Runs suite-level setup and teardown."""
    def __init__(self, *args, **kwargs):
        self.warn = kwargs.pop('warn', False)
        super(AsesTestRunner, self).__init__(*args, **kwargs)

    def run(self, test):
        result = super(AsesTestRunner, self).run(test)
        return result
