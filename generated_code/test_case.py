import unittest
from unittest.mock import patch
from generated_code.generated_selenium_code import login


class TestLogin(unittest.TestCase):
    LOGIN_URL = "http://127.0.0.1:4003/login"
    HOME_PAGE_URL_SEGMENT = "http://127.0.0.1:4003/dashboard"
    EMAIL = 'manasakonduru11@gmail.com'
    PASSWORD = '123456'

    def test_successful_login(self):
        result = login(self.LOGIN_URL, self.EMAIL, self.PASSWORD, self.HOME_PAGE_URL_SEGMENT)
        self.assertTrue(result)

    def test_wrong_password(self):
        result = login(self.LOGIN_URL, self.EMAIL, 'wrong_password', self.HOME_PAGE_URL_SEGMENT)
        self.assertFalse(result)

    def test_wrong_username(self):
        result = login(self.LOGIN_URL, 'wrong_username', self.PASSWORD, self.HOME_PAGE_URL_SEGMENT)
        self.assertFalse(result)

    def test_empty_username(self):
        result = login(self.LOGIN_URL, '', self.PASSWORD, self.HOME_PAGE_URL_SEGMENT)
        self.assertFalse(result)

    def test_empty_password(self):
        result = login(self.LOGIN_URL, self.EMAIL, '', self.HOME_PAGE_URL_SEGMENT)
        self.assertFalse(result)

    @patch('generated_code.generated_selenium_code.load_login_function_from_path', side_effect=FileNotFoundError)
    def test_missing_selenium_code_path(self, mock_load):
        with self.assertRaises(FileNotFoundError):
            login(self.LOGIN_URL, self.EMAIL, self.PASSWORD, self.HOME_PAGE_URL_SEGMENT)

    @patch('generated_code.generated_selenium_code.login', return_value=False)
    def test_login_failure(self, mock_login):
        result = mock_login(self.LOGIN_URL, self.EMAIL, self.PASSWORD, self.HOME_PAGE_URL_SEGMENT)
        self.assertFalse(result)

    @patch('generated_code.generated_selenium_code.load_login_function_from_path', side_effect=ImportError)
    def test_error_loading_login(self, mock_load):
        with self.assertRaises(ImportError):
            login(self.LOGIN_URL, self.EMAIL, self.PASSWORD, self.HOME_PAGE_URL_SEGMENT)

    @patch('generated_code.generated_selenium_code.generate_test_cases', side_effect=Exception)
    def test_llm_failure(self, mock_generate):
        with self.assertRaises(Exception):
            login(self.LOGIN_URL, self.EMAIL, self.PASSWORD, self.HOME_PAGE_URL_SEGMENT)

    def test_missing_login_url(self):
        with self.assertRaises(TypeError):
            login(None, self.EMAIL, self.PASSWORD, self.HOME_PAGE_URL_SEGMENT)

    def test_missing_home_page_url(self):
        with self.assertRaises(TypeError):
            login(self.LOGIN_URL, self.EMAIL, self.PASSWORD, None)


if __name__ == '__main__':
    unittest.main()