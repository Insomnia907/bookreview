# bookreviews/views.py
from django.http import HttpResponse
from .models import Book
from django.views.generic import CreateView
from .forms import PostForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
import asyncio
from django.shortcuts import render
from asgiref.sync import async_to_sync
import io
import urllib.parse
import aiohttp
from bs4 import BeautifulSoup
import os
import wikipedia
from aiohttp import ClientResponseError

import io
import urllib.parse
import aiohttp
from bs4 import BeautifulSoup
import os
import wikipedia


async def goodreads_review(title, author):
    query = f"{author} {title}".replace(" ", '+')
    url = f'https://www.goodreads.com/search?utf8=✓&q={query}&search_type=books'
    result1 = None
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                os.makedirs('parsed_images', exist_ok=True)

                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                result_list = []
                try:
                    result1 = soup.find('span', {'class': 'minirating'}).text.strip()
                    print(f"Goodreads: {result1}")
                    result_list.append(result1)
                except Exception as ex:
                    print(ex)
                    pass
            else:
                print(f"Error: {response.status}")
    return result1

async def search_and_download_image(title, author):
    api_key = 'AIzaSyBQXHMM_CembEkg6y2SmJJON3KwOGcuj9c'
    cx = 'a2f545d653cbc41e1'
    query = f"{title} {author} book cover"
    search_url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={query}&searchType=image"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                response.raise_for_status()
                data = await response.json()
                if 'items' in data and len(data['items']) > 0:
                    img_url = data['items'][0]['link']
                    search_query = f"{title} {author} book"
                    wikipedia.set_lang("en")
                    try:
                        description = ''
                        page = wikipedia.page(search_query)
                        description = page.summary
                        print(f"Description: {description}")

                        async with session.get(img_url) as img_response:
                            img_response.raise_for_status()
                            image_data = await img_response.read()
                            with open(f"{title}_{author}_cover.jpg", "wb") as file:
                                file.write(image_data)
                            print(f"Image downloaded as {title}_{author}_cover.jpg")
                            return [description, img_url]

                    except wikipedia.exceptions.DisambiguationError as e:
                        print(f"Ambiguous search term: {e.options}")
                    except wikipedia.exceptions.PageError as e:
                        print(f"Page not found: {e}")
                    except Exception as e:
                        print(f"An error occurred: {e}")

                else:
                    print("No image found.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


async def livelibreview(title, author):
    query = f"{title} {author}".replace(" ", "+")
    url = f"https://www.livelib.ru/find/{query}"
    result = None
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                try:
                    result = soup.find('span', {'class': 'rating-value stars-color-orange'}).text.strip()
                    print(f"Livelib: {result}")
                except Exception as ex:
                    print(ex)
                    pass
    return result


async def fetch_data(title, author):
    try:
        goodreads_result = await goodreads_review(title, author)
        search_result = await search_and_download_image(title, author)
        livelib_result = await livelibreview(title, author)
        return {
            'title': title,
            'author': author,
            'description': search_result[0] if search_result and search_result[0] else "None",
            'image_url': search_result[1] if search_result and search_result[1] else "None",
            'goodreads_result': goodreads_result if goodreads_result else "None",
            'livelib_result': livelib_result if livelib_result else "None"
        }
    except ClientResponseError as e:
        print(f"Error occurred while fetching data: {e}")
        return {
            'title': title,
            'author': author,
            'description': "None",
            'image_url': "None",
            'goodreads_result': "None",
            'livelib_result': "None"
        }

def home_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            data = asyncio.run(fetch_data(title, author))
            return render(request, 'search_results.html', {'object': data})
    else:
        form = PostForm()
    return render(request, 'home.html', {'form': form})


def search_results_view(request):
    if request.method == 'GET':
        title = request.GET.get('title')
        author = request.GET.get('author')
        data = asyncio.run(fetch_data(title, author))
        return render(request, 'search_results.html', {'object': data})