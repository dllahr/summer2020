import unittest
import logging
import summer2020py.setup_logger as setup_logger
import general_python_script_template as gpst


logger = logging.getLogger(setup_logger.LOGGER_NAME)

# Some notes on testing conventions (more in cuppers convention doc):
#    (1) Use "self.assert..." over "assert"
#        - self.assert* methods: https://docs.python.org/2.7/library/unittest.html#assert-methods
#       - This will ensure that if one assertion fails inside a test method,
#         exectution won't halt and the rest of the test method will be executed
#         and other assertions are also verified in the same run.
#     (2) For testing exceptions use:
#        with self.assertRaises(some_exception) as context:
#            [call method that should raise some_exception]
#        self.assertEqual(str(context.exception), "expected exception message")
#
#        self.assertAlmostEquals(...) for comparing floats


class TestRunGseaUsingGenepattern(unittest.TestCase):
    def test_main(self):
        gpst.main(None)


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()
