import unittest

from homework import check_tokens, check_response, ResponseError


class TestHomeworkBot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.response_correct = {
            'current_date': 1679996158,
            'homeworks': [
                {'date_updated': '2023-03-09T20:46:20Z',
                 'homework_name': 'Resistor-git__hw05_final.zip',
                 'id': 710842,
                 'lesson_name': 'Проект спринта: подписки на авторов',
                 'reviewer_comment': 'Хорошая работа! Ты молодец!\n',
                 'status': 'approved'}
            ]
        }
        cls.response_not_dict = (
            'current_date', 1679, 'homeworks', []
        )
        cls.response_wrong_keys = {
            'time': 1679996158,
            'tasks': [
                {'date_updated': '2023-03-09T20:46:20Z',
                 'homework_name': 'Resistor-git__hw05_final.zip',
                 'id': 710842,
                 'lesson_name': 'Проект спринта: подписки на авторов',
                 'reviewer_comment': 'Хорошая работа! Ты молодец!\n',
                 'status': 'approved'}
            ]
        }
        cls.response_homeworks_not_list = {
            'current_date': 1679996158,
            'homeworks': (
                {'date_updated': '2023-03-09T20:46:20Z',
                 'homework_name': 'Resistor-git__hw05_final.zip',
                 'id': 710842,
                 'lesson_name': 'Проект спринта: подписки на авторов',
                 'reviewer_comment': 'Хорошая работа! Ты молодец!\n',
                 'status': 'approved'}
            )
        }
        cls.response_homeworks_empty = {
            'current_date': 1679996158,
            'homeworks': []
        }

    def test_check_tokens(self):
        # DO NOT KNOW HOW TO TEST THIS FUNCTION
        # Problem is: test uses the real data from .env, which is inappropriate
        # self.assertIsNone(check_tokens())
        # создать временную .env и записать в неё значения, а после теста стереть
        pass

    def test_check_response_correct(self):
        response = TestHomeworkBot.response_correct
        self.assertIsNone(check_response(response))

    def test_check_response_not_dict(self):
        with self.assertRaises(TypeError):
            check_response(TestHomeworkBot.response_not_dict)
    
    def test_check_response_wrong_keys(self):
        with self.assertRaises(ResponseError):
            check_response(TestHomeworkBot.response_wrong_keys)
    
    def test_check_response_homeworks_not_list(self):
        with self.assertRaises(TypeError):
            check_response(TestHomeworkBot.response_homeworks_not_list)

    def test_check_response_homeworks_empty(self):
        with self.assertRaises(ResponseError):
            check_response(TestHomeworkBot.response_homeworks_empty)


if __name__ == '__main__':
    unittest.main()
