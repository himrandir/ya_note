from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Обычный автор')
        cls.another_author = User.objects.create(
            username='Другой обычный автор'
        )
        cls.note = Note.objects.create(
            title='Заголовок', text='текст', slug='l33t', author=cls.author
        )

    def test_note_in_list_on_list_page(self):
        url = reverse('notes:list')
        parameters = (
            (self.author, True),
            (self.another_author, False),
        )
        for user, assert_bool in parameters:
            self.client.force_login(user)
            response = self.client.get(url)
            object_list = response.context['object_list']
            with self.subTest(user=user):
                self.assertEqual(self.note in object_list, assert_bool)


class TestAddDetailPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Обычный автор')
        cls.note = Note.objects.create(
            title='Заголовок', text='текст', slug='l33t', author=cls.author
        )

    def test_authorized_client_has_form_on_detail_and_add_pages(self):
        detail_urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        )
        self.client.force_login(self.author)

        for url in detail_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
