from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..forms import SearchForm
from ..models import Board, Post, Topic
from ..views import SearchPostView, SearchTopicView


class SearchTestCase(TestCase):
    '''
    Base test case to be used in all `search_topic` view tests
    '''
    def setUp(self):
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)
        self.client.login(username=self.username, password=self.password)

class SearchTopicTests(SearchTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('search_topic', kwargs={'search_phase': 'a'})
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/search/topic/a/')
        self.assertEquals(view.func.view_class, SearchTopicView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SearchForm)

    def test_form_inputs(self):
        '''
        The view must contain four inputs: csrf, message textarea and two radios
        '''
        self.assertContains(self.response, '<input', 4)

class SearchPostTests(SearchTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('search_post', kwargs={'search_phase': 'a'})
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/search/post/a/')
        self.assertEquals(view.func.view_class, SearchPostView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SearchForm)

    def test_form_inputs(self):
        '''
        The view must contain four inputs: csrf, message textarea and two radios
        '''
        self.assertContains(self.response, '<input', 4)