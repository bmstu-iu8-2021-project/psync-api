import unittest

from db_control.files_actions import *


class TestFilesActions(unittest.TestCase):
    def test_is_difference(self):
        # разные архивы
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'empty_folder.zip'), '/empty_folder/include'))
        content = [{'name': i, 'timestamp': files[i]} for i in files]
        self.assertFalse(is_difference(join(os.path.dirname(__file__), 'archives', 'folder.zip'), content))

        # разные архивы
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'folder.zip'), '/folder/directory/include'))
        content = [{'name': i, 'timestamp': files[i]} for i in files]
        self.assertFalse(is_difference(join(os.path.dirname(__file__), 'archives', 'empty_folder.zip'), content))

        # один и тот же архив
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'folder.zip'), ''))
        content = [{'name': i, 'timestamp': files[i]} for i in files]
        self.assertTrue(is_difference(join(os.path.dirname(__file__), 'archives', 'folder.zip'), content))

        # одинаковые (копия)
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'to_compare.zip'), ''))
        content = [{'name': i, 'timestamp': files[i]} for i in files]
        self.assertTrue(is_difference(join(os.path.dirname(__file__), 'archives', 'to_compare_2.zip'), content))

        # дерево то же - дата изменена
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'to_compare.zip'), ''))
        content = [{'name': i, 'timestamp': files[i]} for i in files]
        self.assertFalse(is_difference(join(os.path.dirname(__file__), 'archives', 'to_compare_3.zip'), content))

        # файл переименован
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'to_compare.zip'), ''))
        content = [{'name': i, 'timestamp': files[i]} for i in files]
        self.assertFalse(is_difference(join(os.path.dirname(__file__), 'archives', 'to_compare_4.zip'), content))

        # один файл был перемещен внутри архива
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'to_compare.zip'), ''))
        content = [{'name': i, 'timestamp': files[i]} for i in files]
        self.assertFalse(is_difference(join(os.path.dirname(__file__), 'archives', 'to_compare_5.zip'), content))

    def test_get_dict(self):
        # папки, файлы, файлы под стартовой папкой
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'folder.zip'), '/folder/directory/include'))
        self.assertEqual(len(files), 12)
        self.assertIn('/bear_file.txt', files)
        self.assertIn('/one/', files)
        self.assertIn('/one/one.txt', files)
        self.assertIn('/one/two.txt', files)
        self.assertIn('/one/three.txt', files)
        self.assertIn('/two/', files)
        self.assertIn('/two/one.cpp', files)
        self.assertIn('/two/one.py', files)
        self.assertIn('/two/one.pas', files)
        self.assertIn('/two/two_dot_one/', files)
        self.assertIn('/two/two_dot_one/text.txt', files)
        self.assertIn('/two/two_dot_one/text.md', files)

        # одна папка
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'folder.zip'), '/folder/directory/include/one'))
        self.assertEqual(len(files), 3)
        self.assertIn('/one.txt', files)
        self.assertIn('/two.txt', files)
        self.assertIn('/three.txt', files)

        # папка без файлов
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'empty_folder.zip'), '/empty_folder/include'))
        self.assertEqual(len(files), 2)
        self.assertIn('/include_folder/', files)
        self.assertIn('/include_folder/another_folder/', files)

        # пустая папка
        files = get_dict((join(os.path.dirname(__file__), 'archives', 'empty_folder.zip'),
                          '/empty_folder/include/include_folder/another_folder'))
        self.assertEqual(len(files), 0)

    def test_need_merge(self):
        # одинаковые (копия)
        self.assertTrue(need_merge((join(os.path.dirname(__file__), 'archives', 'to_merge.zip'), ''),
                                   (join(os.path.dirname(__file__), 'archives', 'to_merge_2.zip'), '')))
        self.assertTrue(need_merge((join(os.path.dirname(__file__), 'archives', 'to_merge_2.zip'), ''),
                                   (join(os.path.dirname(__file__), 'archives', 'to_merge.zip'), '')))

        # младше
        self.assertTrue(need_merge((join(os.path.dirname(__file__), 'archives', 'to_merge_3.zip'), ''),
                                   (join(os.path.dirname(__file__), 'archives', 'to_merge.zip'), '')))

        # старше
        self.assertFalse(need_merge((join(os.path.dirname(__file__), 'archives', 'to_merge.zip'), ''),
                                    (join(os.path.dirname(__file__), 'archives', 'to_merge_3.zip'), '')))

        # является надмножеством
        self.assertTrue(need_merge((join(os.path.dirname(__file__), 'archives', 'to_merge.zip'), ''),
                                   (join(os.path.dirname(__file__), 'archives', 'to_merge_4.zip'), '')))

        # является подмножеством
        self.assertFalse(need_merge((join(os.path.dirname(__file__), 'archives', 'to_merge.zip'), ''),
                                    (join(os.path.dirname(__file__), 'archives', 'to_merge_5.zip'), '')))

        # разные
        self.assertFalse(need_merge((join(os.path.dirname(__file__), 'archives', 'to_merge.zip'), ''),
                                    (join(os.path.dirname(__file__), 'archives', 'empty_folder.zip'), '')))
        self.assertFalse(need_merge((join(os.path.dirname(__file__), 'archives', 'empty_folder.zip'), ''),
                                    (join(os.path.dirname(__file__), 'archives', 'to_merge.zip'), '')))


if __name__ == '__main__':
    unittest.main()
