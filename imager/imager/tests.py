from django.test import TestCase, Client, LiveServerTestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from imagerprofile.models import ImagerProfile
from imager_images.tests import ImageFactory, AlbumFactory
import factory
from selenium import webdriver
from time import sleep


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username', 'password', 'is_active')

    username = factory.Sequence(lambda n: 'User%03d' % n)
    password = 'secret'
    is_active = True


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImagerProfile
        django_get_or_create = ('user',)

    user = factory.SubFactory(UserFactory)


# class LoginTestCase(TestCase):
#     # def setUp(self):
#     #     '''set up basic client'''
#     #     self.client = Client()

#     def loginHelper(self, username, password):
#         return self.client.post('/login', {'username': username,
#                                            'password': password})

#     def test_home(self):
#         '''test that home page is available to logged out user'''
#         response = self.client.get(reverse('home'))
#         self.assertEqual(response.status_code, 200)

#     def test_register(self):
#         '''test registration is available, and redirects on post'''
#         username = 'sally'
#         email = 'sally@sally.com'
#         password = 'secret'
#         response = self.client.get(reverse('registration_register'))
#         self.assertEqual(response.status_code, 200)
#         response = self.client.post(
#             reverse('registration_register'), {
#                 'username': username,
#                 'email': email,
#                 'password': password
#             })
#         self.assertEqual(response.status_code, 200)

#     def test_login(self):
#         '''test login is reachable when not logged in,
#         login changes auth'''
#         response = self.client.get(reverse('login'))
#         self.assertEqual(response.status_code, 200)
#         fred = UserFactory(username='fred', password='secret')
#         self.loginHelper('fred', 'secret')
#         assert fred.is_authenticated()

    # def test_profile_view_redirect(self):
    #     '''unauthenticated user redirected when trying
    #     to view personal profile'''
    #     # response = self.client.get('/logout')
    #     response = self.client.get('/profile')
    #     self.assertRedirects(response, '/login/', status_code=302)

    # def test_profile_view(self):
    #     '''authenticated user able to view personal profile'''
    #     fred = UserFactory(username='fred', password='secret')
    #     response = self.loginHelper('fred', 'secret')
    #     assert fred.is_authenticated()
    #     response = self.client.get('/profile')
    #     # import pdb; pdb.set_trace()
    #     self.assertEqual(response.status_code, 200)
    #     assert 'Welcome, fred' in response.context['body']


class TestProfileView(LiveServerTestCase):
    def setUp(self):
        self.user1 = UserFactory.create(
            username='alice',
            first_name='Alice'
            )
        self.user1.set_password('secret')
        self.user1.save()
        self.user2 = UserFactory.create(
            username='bob',
            first_name='Bob',
            )
        self.user2.set_password('secret')
        self.user2.save()
        self.selenium = webdriver.Firefox()
        super(TestProfileView, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(TestProfileView, self).tearDown()

    def login_user(self, user=None):
        if user is None:
            user = self.user1
        self.selenium.get(
            '{}{}'.format(self.live_server_url, reverse('login'))
            )
        self.selenium.find_element_by_id('id_username').send_keys(user.username)
        self.selenium.find_element_by_id('id_password').send_keys('secret')
        self.selenium.find_element_by_tag_name('form').submit()

    def create_album(self, user=None):
        if user is None:
            user = self.user2
            self.login_user(user)
        self.selenium.get(
            '{}{}'.format(self.live_server_url, reverse('album_create'))
            )
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('My test album')
        self.selenium.find_element_by_id('id_description').send_keys('This is an album test')
        self.selenium.find_element_by_id('submit').click()

    def test_login_redirect(self):
        user = self.user1
        self.login_user(user)
        assert user.is_authenticated()
        # self.selenium.save_screenshot('login.png')
        assert self.selenium.find_element_by_id('stream_link')
        assert self.selenium.find_element_by_partial_link_text('Update my profile')

    def test_profile(self):
        user = self.user1
        self.login_user(user)
        # self.selenium.save_screenshot('profile.png')
        assert self.selenium.find_element_by_id('stream_link')
        assert self.selenium.find_element_by_id('welcome_name')
        assert self.selenium.find_element_by_class_name('profile_pic')

    def test_stream(self):
        user = self.user1
        self.login_user(user)
        self.selenium.find_element_by_partial_link_text('Stream').click()
        # self.selenium.save_screenshot('stream.png')
        assert self.selenium.find_element_by_id('album_gallery')
        assert self.selenium.find_element_by_id('photo_gallery')

    def test_library(self):
        user = self.user1
        self.login_user(user)
        self.selenium.find_element_by_partial_link_text('Library').click()
        # self.selenium.save_screenshot('library.png')
        assert self.selenium.find_element_by_id('album_gallery')
        assert self.selenium.find_element_by_id('photo_gallery')

    def test_upload_photo(self):
        user = self.user1
        self.login_user(user)
        self.selenium.find_element_by_partial_link_text('Upload Photo').click()
        self.selenium.find_element_by_id('id_picture').send_keys('/Users/jwarren/Desktop/jwarren.jpg')
        # self.selenium.save_screenshot('upload.png')
        self.selenium.find_element_by_id('submit').click()
        assert self.selenium.find_element_by_tag_name('img')

    def test_create_album(self):
        user = self.user2
        self.login_user(user)
        self.create_album(user)
        # self.selenium.save_screenshot('create.png')
        assert self.selenium.find_element_by_class_name('library_gallery')

    def test_edit_and_delete_album(self):
        user = self.user2
        self.login_user(user)
        self.create_album(user)
        self.selenium.get(
            '{}{}'.format(self.live_server_url, reverse('library'))
            )
        self.selenium.find_element_by_class_name('library_gallery').click()
        self.selenium.find_element_by_id('id_published').send_keys('Private')
        self.selenium.find_element_by_id('submit').click()
        self.selenium.find_element_by_class_name('library_gallery').click()
        # self.selenium.save_screenshot('pre_delete.png')
        self.selenium.find_element_by_name('album_delete').click()
        # self.selenium.save_screenshot('post_delete.png')
        assert self.selenium.find_element_by_id('no_albums')

    def test_logout(self):
        user = self.user2
        self.login_user(user)
        self.selenium.find_element_by_link_text('Logout').click()
        assert self.selenium.find_element_by_link_text('Login')
        assert self.selenium.find_element_by_link_text('Register')
