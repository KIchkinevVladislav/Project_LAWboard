from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

@cache_page(20, key_prefix='index_page')
def index(request):
    """
    Gets a selection of 10 entries per page.
    :param request:
    :return: page 'index.html'
    """  
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 5) 

    page_number = request.GET.get('page')  
    page = paginator.get_page(page_number)  
    return render(
         request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )

def group_posts(request, slug):
    """
    Gets an object from the database and outputs new entries by criteria.
    If the object is not found it reports a 404 error.

    :param request:
    :param slug:
    :return: page 'group.html'
    """
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
            request,
            'group.html',
            {'group': group, 'page': page, 'paginator': paginator}
    )

@login_required
def new_post(request):
    """
    Adds a new publication.
    :param request:
    :return: After validating the form and creating a new post,
    the author is redirected to the main page.
    """
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})

def profile(request, username):
    """
    Adds a profile page with posts
    :param request:
    :param username:
    :return: page 'profile.html'
    """
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
         following = Follow.objects.filter(user=request.user.id,
                                        author=author).exists()        
    post_list = Post.objects.filter(author=author)
    count_posts = post_list.count()
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {'page' : page,
                'author' : author,
                'paginator' : paginator,
                'following': following,
                'count_posts': count_posts
                }
    return render(request, 'profile.html', context)


@login_required
def add_comment(request, username, post_id):
    """
    Creating a comment for editing an existing post
    :param request:
    :param username:
    :param post_id:
    :return: the page with comment or the page for viewing the post.
    """
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'includes/comments.html',
                      {'form': form, 'post': post})
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()
    return redirect('post', username, post_id)

def post(request, username, post_id):
    """
    Creates a Page for viewing a separate post
    :param request:
    :param username:
    :param post_id:
    :return: page 'post.html'
    """
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username = username, id = post_id) 
    post_list = Post.objects.filter(author=author)
    count_posts = post_list.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
        
    context = {'author': author,
    'username': username,
    'post': post,
    'form': form,
    'comments': comments,
    'count_posts': count_posts}

    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    """
    Creating a page for editing an existing post
    :param request:
    :param username:
    :param post_id:
    :return: the page with the changed post or the page for viewing the post.
    """
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
   
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post', username=request.user.username, post_id=post_id)

    return render(
        request, 'new_post.html', {'form': form, 'post': post,'is_edit': True},
    )


@login_required
def follow_index(request):
    """
    Displays posts of authors that the current user is subscribed to.
    :param request:
    :return: the page with posts of authors that the current user is subscribed to.
    """
    user = get_object_or_404(User, username=request.user)
    post_list = Post.objects.filter(author__following__user=request.user)
    count_posts = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'user': user, 
                'page': page, 
                'paginator': paginator, 
                'count_post': count_posts}
    return render (request, 'follow.html', context)

@login_required
def profile_follow(request, username):
    """
    Subscribes to an interesting author.
    """
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if not request.user == author:
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)

@login_required
def profile_unfollow(request, username):
    """
    Unsubscribes from the author.
    """
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)

def page_not_found(request, exception):
        return render(
        request, 
        'misc/404.html', 
        {'path': request.path}, 
        status=404
    )

def server_error(request):
    return render(request, 'misc/500.html', status=500)