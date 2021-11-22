import unittest

import tests.test_files_actions as file_actions
import tests.test_database_actions as database_actions
import tests.test_requests_handler as requests_handler


if __name__ == '__main__':
    test = unittest.TestLoader().loadTestsFromModule(file_actions)
    unittest.TextTestRunner(verbosity=2).run(test)
    test = unittest.TestLoader().loadTestsFromModule(database_actions)
    unittest.TextTestRunner(verbosity=2).run(test)
    test = unittest.TestLoader().loadTestsFromModule(requests_handler)
    unittest.TextTestRunner(verbosity=2).run(test)
