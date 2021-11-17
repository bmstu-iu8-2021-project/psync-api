import unittest
from db_control.database_actions import *


class TestDatabaseActions(unittest.TestCase):
    def test_access(self):
        # проверка функции добавления пользователя
        self.assertIsNone(add_user('test_user', 'test_mac', 'test_email', 'test_password'))

        # проверка функций поиска
        self.assertEqual(find_login('test_user'), 'False')
        self.assertEqual(find_email('test_email'), 'False')

        # проверка функций получения
        self.assertEqual(get_email('test_user'), 'test_email')
        self.assertEqual(get_password('test_user'), 'test_password')

        # проверка функции удаления пользователя
        self.assertIsNone(delete_user('test_user'))

        # проверка функций поиска
        self.assertEqual(find_login('test_user'), 'True')
        self.assertEqual(find_email('test_email'), 'True')

        # проверка функций получения
        self.assertRaises(TypeError, get_email, 'test_user')
        self.assertRaises(TypeError, get_password, 'test_user')

    def test_change(self):
        add_user('test_user', 'test_mac', 'test_email', 'test_password')

        self.assertEqual(get_email('test_user'), 'test_email')
        self.assertEqual(get_password('test_user'), 'test_password')

        # проверка функций смены
        change('test_user', 'email', 'new_test_email')
        self.assertEqual(get_email('test_user'), 'new_test_email')
        change('test_user', 'password', 'new_test_password')
        self.assertEqual(get_password('test_user'), 'new_test_password')

        delete_user('test_user')

    def test_auth(self):
        add_user('test_user', 'test_mac', 'test_email',
                 bcrypt.hashpw('test_password'.encode('UTF-8'), bcrypt.gensalt(rounds=5)).decode('UTF-8'))

        # проверка функции авторизации
        self.assertFalse(auth('test_user', 'wrong_test_password', 'another_test_mac'))
        self.assertTrue(auth('test_user', 'test_password', 'test_mac'))
        self.assertTrue(auth('test_user', 'test_password', 'another_test_mac'))

        delete_user('test_user')

    def test_version(self):
        # проверка функции добавления версии
        self.assertRaises(TypeError, add_version, 'test_user', 'test_mac', 'test_folder', 'test_version', False)

        add_user('test_user', 'test_mac', 'test_email',
                 bcrypt.hashpw('test_password'.encode('UTF-8'), bcrypt.gensalt(rounds=5)).decode('UTF-8'))
        self.assertTrue(auth('test_user', 'test_password', 'another_test_mac'))

        # проверка функции поиска и добавления версии
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'test_version'), 'True')
        self.assertIsNone(add_version('test_user', 'test_mac', 'test_folder', 'test_version', False))

        # проверка функции поиска версии
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'test_version'), 'False')
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'another_test_version'), 'True')

        # проверка функции добавления версий разным папкам
        self.assertIsNone(add_version('test_user', 'test_mac', 'test_folder', 'one_test_version', False))
        self.assertIsNone(add_version('test_user', 'test_mac', 'test_folder', 'two_test_version', False))
        self.assertIsNone(add_version('test_user', 'test_mac', 'test_folder', 'three_test_version', False))
        self.assertIsNone(add_version('test_user', 'test_mac', 'one_test_folder', 'test_version', False))
        self.assertIsNone(add_version('test_user', 'test_mac', 'one_test_folder', 'one_test_version', False))
        self.assertIsNone(add_version('test_user', 'test_mac', 'two_test_folder', 'test_version', False))
        self.assertIsNone(add_version('test_user', 'another_test_mac', 'one_test_folder', 'test_version', False))
        self.assertIsNone(
            add_version('test_user', 'another_test_mac', 'another_test_folder', 'one_test_version', False))
        self.assertIsNone(
            add_version('test_user', 'another_test_mac', 'another_test_folder', 'two_test_version', False))

        # проверка функции поиска версий разных папок
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'one_test_version'), 'False')
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'two_test_version'), 'False')
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'three_test_version'), 'False')
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'test_version'), 'False')
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'another_test_version'), 'True')
        self.assertEqual(find_version('test_user', 'test_mac', 'one_test_folder', 'test_version'), 'False')
        self.assertEqual(find_version('test_user', 'test_mac', 'one_test_folder', 'one_test_version'), 'False')
        self.assertEqual(find_version('test_user', 'test_mac', 'one_test_folder', 'two_test_version'), 'True')
        self.assertEqual(find_version('test_user', 'test_mac', 'two_test_folder', 'test_version'), 'False')
        self.assertEqual(find_version('test_user', 'test_mac', 'two_test_folder', 'one_test_version'), 'True')
        self.assertEqual(find_version('test_user', 'test_mac', 'two_test_folder', 'two_test_version'), 'True')
        self.assertEqual(find_version('test_user', 'another_test_mac', 'one_test_folder', 'test_version'), 'False')
        self.assertEqual(find_version('test_user', 'another_test_mac', 'one_test_folder', 'one_test_version'), 'True')
        self.assertEqual(find_version('test_user', 'another_test_mac', 'another_test_folder', 'one_test_version'),
                         'False')
        self.assertEqual(find_version('test_user', 'another_test_mac', 'another_test_folder', 'two_test_version'),
                         'False')

        # проверка установки некоторых версий как актуальных
        self.assertIsNone(make_actual('test_user', 'test_mac', 'test_folder', 'one_test_version'))
        self.assertIsNone(make_actual('test_user', 'test_mac', 'test_folder', 'two_test_version'))
        self.assertIsNone(make_actual('test_user', 'test_mac', 'one_test_folder', 'test_version'))
        self.assertIsNone(make_no_actual('test_user', 'test_mac', 'one_test_folder'))
        self.assertIsNone(make_actual('test_user', 'test_mac', 'two_test_folder', 'test_version'))
        self.assertIsNone(make_actual('test_user', 'another_test_mac', 'one_test_folder', 'test_version'))

        # проверка актуальных версий
        self.assertEqual(get_actual_version('test_user', 'test_mac', 'test_folder'), 'two_test_version')
        self.assertIsNone(get_actual_version('test_user', 'test_mac', 'one_test_folder'))
        self.assertEqual(get_actual_version('test_user', 'test_mac', 'two_test_folder'), 'test_version')
        self.assertEqual(get_actual_version('test_user', 'another_test_mac', 'one_test_folder'), 'test_version')

        # проверка вывода всех папок
        versions = json.loads(get_folders('test_user', 'test_mac'))
        self.assertEqual(len(versions), 7)
        for rec in versions:
            rec.pop('created_at')
        self.assertIn({'folder': 'test_folder', 'version': 'test_version', 'is_actual': False}, versions)
        self.assertIn({'folder': 'test_folder', 'version': 'three_test_version', 'is_actual': False}, versions)
        self.assertIn({'folder': 'test_folder', 'version': 'one_test_version', 'is_actual': False}, versions)
        self.assertIn({'folder': 'test_folder', 'version': 'two_test_version', 'is_actual': True}, versions)
        self.assertIn({'folder': 'one_test_folder', 'version': 'one_test_version', 'is_actual': False}, versions)
        self.assertIn({'folder': 'one_test_folder', 'version': 'test_version', 'is_actual': False}, versions)
        self.assertIn({'folder': 'two_test_folder', 'version': 'test_version', 'is_actual': True}, versions)

        versions = json.loads(get_folders('test_user', 'another_test_mac'))
        self.assertEqual(len(versions), 3)
        for rec in versions:
            rec.pop('created_at')
        self.assertIn({'folder': 'one_test_folder', 'version': 'test_version', 'is_actual': True}, versions)
        self.assertIn({'folder': 'another_test_folder', 'version': 'one_test_version', 'is_actual': False}, versions)
        self.assertIn({'folder': 'another_test_folder', 'version': 'two_test_version', 'is_actual': False}, versions)

        # проверка удаления папок
        self.assertIsNotNone(delete_version('test_user', 'test_mac', 'test_folder', 'test_version'))
        self.assertIsNotNone(delete_version('test_user', 'test_mac', 'test_folder', 'one_test_version'))
        self.assertIsNotNone(delete_version('test_user', 'test_mac', 'test_folder', 'two_test_version'))
        self.assertIsNotNone(delete_version('test_user', 'test_mac', 'test_folder', 'three_test_version'))
        self.assertIsNotNone(delete_version('test_user', 'test_mac', 'one_test_folder', 'test_version'))
        self.assertIsNotNone(delete_version('test_user', 'test_mac', 'one_test_folder', 'one_test_version'))
        self.assertIsNotNone(delete_version('test_user', 'test_mac', 'two_test_folder', 'test_version'))
        self.assertIsNotNone(delete_version('test_user', 'another_test_mac', 'one_test_folder', 'test_version'))
        self.assertIsNotNone(delete_version('test_user', 'another_test_mac', 'another_test_folder', 'one_test_version'))
        self.assertIsNotNone(delete_version('test_user', 'another_test_mac', 'another_test_folder', 'two_test_version'))

        # проверка поиска папок
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'test_version'), 'True')
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'one_test_version'), 'True')
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'two_test_version'), 'True')
        self.assertEqual(find_version('test_user', 'test_mac', 'test_folder', 'three_test_version'), 'True')
        self.assertEqual(find_version('test_user', 'test_mac', 'one_test_folder', 'test_version'), 'True')
        self.assertEqual(find_version('test_user', 'test_mac', 'one_test_folder', 'one_test_version'), 'True')
        self.assertEqual(find_version('test_user', 'test_mac', 'two_test_folder', 'test_version'), 'True')
        self.assertEqual(find_version('test_user', 'another_test_mac', 'one_test_folder', 'test_version'), 'True')
        self.assertEqual(find_version('test_user', 'another_test_mac', 'another_test_folder', 'one_test_version'),
                         'True')
        self.assertEqual(find_version('test_user', 'another_test_mac', 'another_test_folder', 'two_test_version'),
                         'True')

        # проверка вывода всех папок
        versions = json.loads(get_folders('test_user', 'test_mac'))
        self.assertEqual(len(versions), 0)

        versions = json.loads(get_folders('test_user', 'another_test_mac'))
        self.assertEqual(len(versions), 0)

        delete_user('test_user')

    def test_synchronization(self):
        add_user('one_test_user', 'one_test_mac', 'one_test_email', 'test_password')
        add_user('two_test_user', 'two_test_mac', 'two_test_email', 'test_password')
        add_user('three_test_user', 'three_test_mac', 'three_test_email', 'test_password')

        add_version('one_test_user', 'one_test_mac', 'one_test_folder', 'test_version', True)
        add_version('one_test_user', 'one_test_mac', 'two_test_folder', 'test_version', True)
        add_version('two_test_user', 'two_test_mac', 'three_test_folder', 'test_version', True)
        add_version('two_test_user', 'two_test_mac', 'four_test_folder', 'test_version', True)
        add_version('three_test_user', 'three_test_mac', 'five_test_folder', 'test_version', True)
        add_version('three_test_user', 'three_test_mac', 'six_test_folder', 'test_version', True)

        # проверка создание синхронизации папок
        self.assertIsNone(synchronize(('one_test_user', 'one_test_mac', 'one_test_folder'),
                                      ('two_test_user', 'two_test_mac', 'three_test_folder')))
        self.assertIsNone(synchronize(('one_test_user', 'one_test_mac', 'one_test_folder'),
                                      ('two_test_user', 'two_test_mac', 'four_test_folder')))
        self.assertIsNone(synchronize(('one_test_user', 'one_test_mac', 'one_test_folder'),
                                      ('three_test_user', 'three_test_mac', 'five_test_folder')))
        self.assertIsNone(synchronize(('one_test_user', 'one_test_mac', 'one_test_folder'),
                                      ('three_test_user', 'three_test_mac', 'six_test_folder')))
        self.assertIsNone(synchronize(('one_test_user', 'one_test_mac', 'two_test_folder'),
                                      ('two_test_user', 'two_test_mac', 'three_test_folder')))
        self.assertIsNone(synchronize(('one_test_user', 'one_test_mac', 'two_test_folder'),
                                      ('two_test_user', 'two_test_mac', 'four_test_folder')))
        self.assertIsNone(synchronize(('one_test_user', 'one_test_mac', 'two_test_folder'),
                                      ('three_test_user', 'three_test_mac', 'five_test_folder')))
        self.assertIsNone(synchronize(('one_test_user', 'one_test_mac', 'two_test_folder'),
                                      ('three_test_user', 'three_test_mac', 'six_test_folder')))
        self.assertIsNone(synchronize(('two_test_user', 'two_test_mac', 'three_test_folder'),
                                      ('one_test_user', 'one_test_mac', 'one_test_folder')))
        self.assertIsNone(synchronize(('two_test_user', 'two_test_mac', 'three_test_folder'),
                                      ('one_test_user', 'one_test_mac', 'two_test_folder')))
        self.assertIsNone(synchronize(('two_test_user', 'two_test_mac', 'three_test_folder'),
                                      ('three_test_user', 'three_test_mac', 'five_test_folder')))
        self.assertIsNone(synchronize(('two_test_user', 'two_test_mac', 'three_test_folder'),
                                      ('three_test_user', 'three_test_mac', 'six_test_folder')))
        self.assertIsNone(synchronize(('two_test_user', 'two_test_mac', 'four_test_folder'),
                                      ('one_test_user', 'one_test_mac', 'one_test_folder')))
        self.assertIsNone(synchronize(('two_test_user', 'two_test_mac', 'four_test_folder'),
                                      ('one_test_user', 'one_test_mac', 'two_test_folder')))
        self.assertIsNone(synchronize(('two_test_user', 'two_test_mac', 'four_test_folder'),
                                      ('three_test_user', 'three_test_mac', 'five_test_folder')))
        self.assertIsNone(synchronize(('two_test_user', 'two_test_mac', 'four_test_folder'),
                                      ('three_test_user', 'three_test_mac', 'six_test_folder')))
        self.assertIsNone(synchronize(('three_test_user', 'three_test_mac', 'five_test_folder'),
                                      ('one_test_user', 'one_test_mac', 'one_test_folder')))
        self.assertIsNone(synchronize(('three_test_user', 'three_test_mac', 'five_test_folder'),
                                      ('one_test_user', 'one_test_mac', 'two_test_folder')))
        self.assertIsNone(synchronize(('three_test_user', 'three_test_mac', 'five_test_folder'),
                                      ('two_test_user', 'two_test_mac', 'three_test_folder')))
        self.assertIsNone(synchronize(('three_test_user', 'three_test_mac', 'five_test_folder'),
                                      ('three_test_user', 'three_test_mac', 'six_test_folder')))
        self.assertIsNone(synchronize(('three_test_user', 'three_test_mac', 'six_test_folder'),
                                      ('one_test_user', 'one_test_mac', 'one_test_folder')))
        self.assertIsNone(synchronize(('three_test_user', 'three_test_mac', 'six_test_folder'),
                                      ('one_test_user', 'one_test_mac', 'two_test_folder')))
        self.assertIsNone(synchronize(('three_test_user', 'three_test_mac', 'six_test_folder'),
                                      ('two_test_user', 'two_test_mac', 'three_test_folder')))

        self.assertEqual(len(get_pairs_resource_id('one_test_user', 'one_test_mac')), 8)
        self.assertEqual(len(get_pairs_resource_id('two_test_user', 'two_test_mac')), 8)
        self.assertEqual(len(get_pairs_resource_id('three_test_user', 'three_test_mac')), 8)

        # syncs = json.loads(get_synchronized('one_test_user', 'one_test_mac'))
        # self.assertEqual(len(syncs), 4)
        # for rec in syncs:
        #     rec.pop('current_time')
        # self.assertIn({'other_login': 'two_test_user', 'current_folder': '', 'other_folder': ''}, syncs)
        # self.assertIn({'other_login': 'two_test_user', 'current_folder': '', 'other_folder': ''}, syncs)
        # self.assertIn({'other_login': 'three_test_user', 'current_folder': '', 'other_folder': ''}, syncs)
        # self.assertIn({'other_login': 'three_test_user', 'current_folder': '', 'other_folder': ''}, syncs)
        #
        # syncs = json.loads(get_synchronized('two_test_user', 'two_test_mac'))
        # self.assertEqual(len(syncs), 4)
        # for rec in syncs:
        #     rec.pop('current_time')
        #
        # syncs = json.loads(get_synchronized('three_test_user', 'three_test_mac'))
        # self.assertEqual(len(syncs), 4)
        # for rec in syncs:
        #     rec.pop('current_time')

        delete_version('one_test_user', 'one_test_mac', 'one_test_folder', 'test_version')
        delete_version('one_test_user', 'one_test_mac', 'two_test_folder', 'test_version')
        delete_version('two_test_user', 'two_test_mac', 'three_test_folder', 'test_version')
        delete_version('two_test_user', 'two_test_mac', 'four_test_folder', 'test_version')
        delete_version('three_test_user', 'three_test_mac', 'five_test_folder', 'test_version')
        delete_version('three_test_user', 'three_test_mac', 'six_test_folder', 'test_version')

        delete_user('one_test_user')
        delete_user('two_test_user')
        delete_user('three_test_user')


if __name__ == '__main__':
    unittest.main()
