import unittest
import requests


class TestRequestsHandler(unittest.TestCase):
    def setUp(self):
        self.routs = [
            'auth',
            'find_login',
            'find_email',
            'get_email',
            'get_password',
            'change_mail',
            'change_password',
            'add_user',
            'delete_user',
            'find_version',
            'add_version',
            'upload_folder',
            'update_version',
            'download_folder',
            'delete_version',
            'make_actual',
            'make_no_actual',
            'get_folders',
            'get_actual_version',
            'check_actuality',
            'synchronize',
            'synchronize_folder',
            'terminate_sync',
            'get_synchronized',
            'check_synchronized'
        ]
        self.routs_with_token = [
            'get_email',
            'get_password',
            'change_mail',
            'change_password',
            'delete_user',
            'find_version',
            'add_version',
            'upload_folder',
            'update_version',
            'download_folder',
            'delete_version',
            'make_actual',
            'make_no_actual',
            'get_folders',
            'get_actual_version',
            'check_actuality',
            'synchronize',
            'synchronize_folder',
            'terminate_sync',
            'get_synchronized',
            'check_synchronized'
        ]

    def test_url_exist(self):
        for route in self.routs:
            response = requests.get(f'http://127.0.0.1:8080/{route}/')
            self.assertNotEqual(response.status_code, 404)

    def test_url_token(self):
        for route in self.routs_with_token:
            response = requests.get(f'http://127.0.0.1:8080/{route}/')
            self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
