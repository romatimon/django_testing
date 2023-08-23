import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(client, all_news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, all_news):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, slug_for_comment):
    """Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка,
    новые — в конце."""
    detail_url = reverse('news:detail', args=slug_for_comment)
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created, all_comments[1].created


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, slug_for_args):
    """Авторизированному пользователю доступна форма для отправки
    комментария на странице отдельной новости"""
    detail_url = reverse('news:detail', args=slug_for_args)
    response = author_client.get(detail_url)
    assert 'form' in response.context


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, slug_for_args):
    """Неавторизованному пользователю недоступна форма для отправки
    комментария на странице отдельной новости"""
    detail_url = reverse('news:detail', args=slug_for_args)
    response = client.get(detail_url)
    assert 'form' not in response.context
