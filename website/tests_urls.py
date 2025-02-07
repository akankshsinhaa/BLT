from django import test
from django.urls import reverse
from django.conf import settings
import importlib
import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# todo
#from webdriver_manager.chrome import ChromeDriverManager

# can uncomment with chromedrivermanager
os.environ["DJANGO_LIVE_TEST_SERVER_ADDRESS"] = "localhost:8082"

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

d = DesiredCapabilities.CHROME
d["loggingPrefs"] = {"browser": "ALL"}

# switch these
driver = webdriver.Chrome(desired_capabilities=d)
#driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=d)



class UrlsTest(StaticLiveServerTestCase):
    fixtures = ["initial_data.json"]

    @classmethod
    def setUpClass(cls):
        cls.selenium = driver
        super(UrlsTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(UrlsTest, cls).tearDownClass()

    def test_responses(
        self,
        allowed_http_codes=[200, 302, 405],
        credentials={},
        default_kwargs={},
    ):

        module = importlib.import_module(settings.ROOT_URLCONF)
        if credentials:
            self.client.login(**credentials)

        def check_urls(urlpatterns, prefix=""):

            for pattern in urlpatterns:

                if hasattr(pattern, "url_patterns"):

                    new_prefix = prefix
                    if pattern.namespace:
                        new_prefix = (
                            prefix + (":" if prefix else "") + pattern.namespace
                        )
                    check_urls(pattern.url_patterns, prefix=new_prefix)
                params = {}
                skip = False

                regex = pattern.pattern.regex
                if regex.groups > 0:

                    if regex.groups > len(list(regex.groupindex.keys())) or set(
                        regex.groupindex.keys()
                    ) - set(default_kwargs.keys()):

                        skip = True
                    else:
                        for key in set(default_kwargs.keys()) & set(
                            regex.groupindex.keys()
                        ):
                            params[key] = default_kwargs[key]
                if hasattr(pattern, "name") and pattern.name:
                    name = pattern.name
                else:

                    skip = True
                    name = ""
                fullname = (prefix + ":" + name) if prefix else name

                if not skip:
                    url = reverse(fullname, kwargs=params)
                    matches = [
                        "/socialaccounts/",
                        "/auth/user/",
                        "/auth/password/change/",
                        "/auth/github/connect/",
                        "/auth/google/connect/",
                        "/auth/registration/",
                        "/auth/registration/verify-email/",
                        "/auth/registration/resend-email/",
                        "/auth/password/reset/",
                        "/auth/password/reset/confirm/",
                        "/auth/login/",
                        "/auth/logout/",
                        "/auth/facebook/connect/",
                        "/captcha/refresh/",
                        "/rest-auth/user/",
                        "/rest-auth/password/change/",
                        "/accounts/github/login/",
                        "/accounts/google/login/",
                        "/accounts/facebook/login/",
                        "/error/",
                        "/tz_detect/set/",
                        "/leaderboard/api/"
                    ]
                    if not any(x in url for x in matches):
                        response = self.client.get(url)
                        self.assertIn(response.status_code, allowed_http_codes, msg=url)
                        self.selenium.get("%s%s" % (self.live_server_url, url))

                        for entry in self.selenium.get_log("browser"):
                            self.assertNotIn("SyntaxError", str(entry), msg=url)

        check_urls(module.urlpatterns)
