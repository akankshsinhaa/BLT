import os
import time
import sys

from django.test import LiveServerTestCase

os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:8082'

from django.test.utils import override_settings
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By

class MySeleniumTests(LiveServerTestCase):
    fixtures = ['initial_data.json']

    @classmethod
    def setUpClass(cls):
        print (sys.path)
        cls.selenium = webdriver.Firefox(executable_path=GeckoDriverManager(cache_valid_range=1).install())
        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

    @override_settings(DEBUG=True)
    def test_signup(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/signup/'))
        self.selenium.find_element("name", "username").send_keys('bugbugbug')
        self.selenium.find_element("name", "email").send_keys('bugbugbug@bugbug.com')
        self.selenium.find_element("name", "password1").send_keys('6:}jga,6mRKNUqMQ')
        self.selenium.find_element("name", "password2").send_keys('6:}jga,6mRKNUqMQ')
        self.selenium.find_element("name", "signup_button").click()
        WebDriverWait(self.selenium, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        body = self.selenium.find_element('tag name', 'body')
        self.assertIn('bugbugbug (0 Pts)', body.text)

    @override_settings(DEBUG=True)
    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        self.selenium.find_element("name", "login").send_keys('bugbug')
        self.selenium.find_element("name", "password").send_keys('secret')
        self.selenium.find_element("name", "login_button").click()
        WebDriverWait(self.selenium, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        body = self.selenium.find_element('tag name', 'body')
        self.assertIn('bugbug (0 Pts)', body.text)

    @override_settings(DEBUG=True)
    def test_post_bug(self):
        self.selenium.set_page_load_timeout(70)
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        self.selenium.find_element("name", "login").send_keys('bugbug')
        self.selenium.find_element("name", "password").send_keys('secret')
        self.selenium.find_element("name", "login_button").click()
        WebDriverWait(self.selenium, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        self.selenium.get('%s%s' % (self.live_server_url, '/report/'))
        self.selenium.find_element("name", "url").send_keys('http://www.example.com/')
        self.selenium.find_element("id", "description").send_keys('Description of bug')
        Imagepath = os.path.abspath(os.path.join(os.getcwd(), 'website/static/img/logo.jpg'))
        self.selenium.find_element("name", "screenshot").send_keys(Imagepath)
        self.selenium.find_element("name", "reportbug_button").click()
        WebDriverWait(self.selenium, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        body = self.selenium.find_element('tag name', 'body')
        self.assertIn('Description of bug', body.text)
