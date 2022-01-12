from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Post, Group


def index(request):
    """Shows main page of the site."""
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    """Get all posts of the group and split it on pages."""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"page": page, "paginator": paginator})

@login_required
def new_post(request):
    """Function to show user new post creation form."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            author = request.user
            text = form.cleaned_data['text']
            group = form.cleaned_data['group']
            post = Post(author=author, text=text, group=group)
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    """Shows user profile with number of followers, following and total number of posts.
    Also show all user's posts and split it on pages."""
    is_author = False
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-id')
    overall = len(posts)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user == user:
        is_author = True
    return render(request, 'profile.html', {"user": user, "is_author": is_author, "page": page, "overall": overall})


def post_view(request, username, post_id):
    """Show single post on the page."""
    is_author = False
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    overall = len(posts)
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'post.html', {"user": user, "is_author": is_author, "post": post, "overall": overall})

@login_required
def post_edit(request, username, post_id):
    """Function to show user post editing form."""
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    if request.user == user:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post.text = form.cleaned_data['text']
                post.group = form.cleaned_data['group']
                post.save()
                return redirect('index')
            return render(request, 'post_new.html', {'form': form, 'username': username, 'post_id': post_id})
        data = {"text": post.text, "group": post.group}
        # Insert into form initial data of editable post
        form = PostForm(initial=data)
        return render(request, 'post_new.html', {'form': form, 'username': username, 'post_id': post_id})
