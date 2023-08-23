from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, slug_for_args):
    """Анонимный пользователь не может отправить комментарий."""
    detail_url = reverse('news:detail', args=slug_for_args)
    response = client.post(detail_url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_create_comment(author_client, slug_for_args, form_data):
    """Авторизованный пользователь может отправить комментарий."""
    detail_url = reverse('news:detail', args=slug_for_args)
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1


def test_user_cant_use_bad_words(author_client, bad_words_data, slug_for_args):
    """Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку."""
    detail_url = reverse('news:detail', args=slug_for_args)
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment, form_data, news_edit_url, slug_for_args):
    """Авторизованный пользователь может редактировать свои комментарии."""
    url = reverse('news:detail', args=slug_for_args)
    response = author_client.post(news_edit_url, form_data)
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(admin_client, news_edit_url, form_data, comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = admin_client.post(news_edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_detele_comment(author_client, comment, news_delete_url, slug_for_args):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:detail', args=slug_for_args)
    response = author_client.post(news_delete_url)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(admin_client, news_delete_url, form_data, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = admin_client.post(news_delete_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text

