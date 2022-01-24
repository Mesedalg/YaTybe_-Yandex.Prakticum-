from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions

from .forms import PostForm, CommentForm
from .models import Post, Group, Comment, Follow
from .serializers import PostSerializer


@cache_page(15)
def index(request):
    """Shows main page of the site."""
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page}
    )


def group_posts(request, slug):
    """Get all posts of the group and split it on pages."""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"page": page,"group":group})

@login_required
def new_post(request):
    """Function to show user new post creation form."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            author = request.user
            text = form.cleaned_data['text']
            group = form.cleaned_data['group']
            image = form.cleaned_data['image']
            post = Post(author=author, text=text, group=group, image=image)
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
    try:
        author = get_object_or_404(User, username=username)
        following = Follow.objects.get(user=request.user, author=author)
    except:
        following = False

    if request.user == user:
        is_author = True
    return render(request, 'profile.html', {"user": user, "is_author": is_author, "page": page,
                                            "overall": overall, "profile":user, "following": following})


def post_view(request, username, post_id):
    """Show single post on the page."""
    is_author = False
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    overall = len(posts)
    post = get_object_or_404(Post, pk=post_id)
    items = Comment.objects.filter(post_id=post_id)
    form = CommentForm()
    return render(request, 'post.html', {"user": user, "is_author": is_author, "post": post, "overall": overall, "items": items, "form":form})


@login_required
def post_edit(request, username, post_id):
    """Function to show user edit post form."""
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

    if request.method == 'POST':
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)

    return render(
        request, 'post_edit.html', {'form': form, 'post': post, 'username': request.user.username, 'post_id': post_id},
    )


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    """Function to write."""
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            author = request.user
            post = get_object_or_404(Post, pk=post_id)
            text = form.cleaned_data['text']
            comment = Comment(author=author, text=text, post=post)
            comment.save()
    return redirect('post', username=username, post_id=post_id)

@login_required
def follow_index(request):
    following_posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(following_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    print(author)
    follow = Follow.objects.get_or_create(user=request.user, author=author)
    print(follow)
    follow[0].save()
    print(Follow.objects.all())
    return redirect('profile', username=username)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    un_follow = Follow.objects.get(user=request.user, author=author)
    un_follow.delete()

    return redirect('profile', username=username)


@api_view(['GET', 'POST'])
def hello(request):
    if request.method == 'POST':
        return Response({'message': f'Привет {request.data}'})
    return Response({'message': 'Привет, мир!'})


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-pub_date')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
