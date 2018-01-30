from partisk.models import Stuff
from django.shortcuts import render, get_object_or_404
import bleach

def login(request):
    pass


def logout(request):
    pass


def handle(request, stuff_id):
    stuff_data = get_object_or_404(Stuff, id=stuff_id)
    stuff_data.content = bleach.clean(stuff_data.content,
        tags=['div', 'p', 'strong', 'span', 'br', 'a', 'h1', 'h2', 'h3', 'ul', 'li'])
    context = {
        'stuff': stuff_data,
        'tweetId': stuff_data.url.split('/')[-1]
    }
    return render(request, 'handle.html', context)


def stuff(request):
    context = {
        'stuff': Stuff.objects.all().order_by('date', 'id')
    }
    return render(request, 'stuff.html', context)


def admin_index(request):
    return render(request, 'admin.html')
