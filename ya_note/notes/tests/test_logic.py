from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    NOTE_TITLE = "Заголовок заметки"
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'pasport'

    NEW_NOTE_TITLE = 'Новый текст заголовка заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NEW_NOTE_SLUG = 'kniga'

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
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG
        )

        cls.url = reverse('notes:add',)
        cls.url_sussess = ('notes:sussess',)
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'title': cls.NEW_NOTE_TITLE,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.NEW_NOTE_SLUG,
                         }

    def test_user_cant_create_note(self):
        '''Залогиненный пользователь может создать заметку'''
        self.author_client.post(self.url, data=self.form_data)
        notes_cout = Note.objects.count()
        self.assertEqual(notes_cout, 2)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку"""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_cant_use_warning(self):
        """Нельзя создать заметку с существующим slug"""
        warning_data_slug = {
            'title': 'Заголовок из формы',
            'text': 'Текст из формы',
            'slug': 'pasport',
        }
        response = self.author_client.post(self.url, data=warning_data_slug)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors='pasport'+WARNING
        )

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):

    NOTE_TITLE = "Заголовок заметки"
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'pasport'

    NEW_NOTE_TITLE = 'Новый текст заголовка заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NEW_NOTE_SLUG = 'kniga'

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
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG
        )
        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.url = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))

        cls.form_data = {'title': cls.NEW_NOTE_TEXT,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.NEW_NOTE_SLUG}

    def test_author_can_delete_note(self):
        '''Автор может удалять свои заметки'''
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        '''Читатель не может удалять чужие заметки'''
        response = self.reader_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        '''Автор может редактировать свою заметку'''
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_notes_of_another_user(self):
        '''Читатель не может редактировать чужие заметки'''
        response = self.reader_client.post(self.url_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)


class TestEmptySlug(TestCase):

    NEW_NOTE_TITLE = 'Новый текст заголовка заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NEW_NOTE_SLUG = 'kniga'

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.url_add = reverse('notes:add')
        cls.form_data = {'title': cls.NEW_NOTE_TEXT,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.NEW_NOTE_SLUG}

    def test_empty_slug(self):
        """Если при создании заметки не заполнен slug,
        то он формируется автоматически"""
        self.form_data.pop('slug',)
        self.author_client.post(self.url_add, data=self.form_data)
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note, expected_slug
