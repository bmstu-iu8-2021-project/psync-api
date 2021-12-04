import unittest
import requests


class TestRequestsHandler(unittest.TestCase):
    def setUp(self):
        self.routs = [
            'auth',
            'find_login',
            'get_password',
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
            'get_password',
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
            response = requests.get(f'http://127.0.0.1:12355/{route}/')
            self.assertNotEqual(response.status_code, 404)

    def test_url_token(self):
        for route in self.routs_with_token:
            response = requests.get(f'http://127.0.0.1:12355/{route}/')
            self.assertEqual(response.status_code, 400)

    # def test_auth(self):
    #     # no user
    #     response = requests.get(
    #         'http://127.0.0.1:12355/auth/',
    #         params={
    #             'login': 'test_user',
    #             'password': 'test_password',
    #             'mac': 'test_mac'
    #         }
    #     )
    #     self.assertIn('access', response.json())
    #     self.assertEqual(response.json()['access'], True)
    #     self.assertIn('token', response.json())
    #     self.assertEqual(response.json()['token'], '')
    #
    #     # exist user
    #     requests.get(
    #         'http://127.0.0.1:12355/add_user/',
    #         params={
    #             'login': 'test_user',
    #             'password': 'test_password',
    #             'mac': 'test_mac'
    #         }
    #     )
    #     response = requests.get(
    #         'http://127.0.0.1:12355/auth/',
    #         params={
    #             'login': 'test_user',
    #             'password': 'test_password',
    #             'mac': 'test_mac'
    #         }
    #     )
    #     self.assertIn('access', response.json())
    #     self.assertEqual(response.json()['access'], True)
    #     self.assertIn('token', response.json())
    #     self.assertNotEqual(response.json()['token'], '')
    #     response = requests.get(
    #         'http://127.0.0.1:12355/auth/',
    #         params={
    #             'login': 'test_user',
    #             'password': 'test_password',
    #             'mac': 'other_test_mac'
    #         }
    #     )
    #     self.assertIn('access', response.json())
    #     self.assertEqual(response.json()['access'], False)
    #     self.assertIn('token', response.json())
    #     self.assertEqual(response.json()['token'], '')
    #     requests.get('http://127.0.0.1:12355/delete_user/', params={'login': 'test_user'})


if __name__ == '__main__':
    unittest.main()
