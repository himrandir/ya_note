from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Максим Горький')
        cls.note = Note.objects.create(
            title='Заголовок', text='текст', slug='l33t', author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('notes:list', self.author),
            ('notes:add', self.author),
            ('notes:success', self.author),
        )
        for name, current_user in urls:
            with self.subTest(name=name):
                url = reverse(name)
                if current_user is not None:
                    self.client.force_login(current_user)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_note_edit_and_delete(self):
        user_status = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for user, status in user_status:
            self.client.force_login(user)

            for name_url in urls:
                with self.subTest(user=user, name=name_url):
                    url = reverse(name_url, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anonymous(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_login_signup_everybody(self):
        users = (
            self.author,
            None,
        )
        urls = ('users:login', 'users:logout', 'users:signup')

        for user in users:
            if user is not None:
                self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user, url=url):
                    url = reverse(url)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
