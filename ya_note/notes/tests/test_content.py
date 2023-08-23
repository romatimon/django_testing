from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
            slug='pasport'
        )
        cls.url_list = reverse('notes:list')
        cls.url_add = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_in_list_for_author(self):
        """Отдельная заметка передаётся на страницу со списком заметок"""
        response = self.author_client.get(self.url_list)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        """В список заметок одного пользователя не попадают
        заметки другого пользователя"""
        response = self.reader_client.get(self.url_list)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_note_page_contains_form(self):
        """На страницу создания заметки передаются формы"""
        response = self.author_client.get(self.url_add)
        self.assertIn('form', response.context)

    def test_edit_note_page_contains_form(self):
        """На страницу редактирования заметки передаются формы"""
        response = self.author_client.get(self.url_edit)
        self.assertIn('form', response.context)
