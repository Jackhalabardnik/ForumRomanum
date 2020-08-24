from django.db.models import Count

from django.urls import reverse

from django.shortcuts import render, redirect, get_object_or_404

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import UpdateView, ListView, CreateView

from django.utils import timezone

from django.template.defaultfilters import slugify

from .forms import NewTopicForm, PostForm, SearchForm
from .models import Board, Topic, Post

class BasicSearchView(ListView):
    def post(self, request, **kwargs):
        form = SearchForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('search_for') == 'topic':
                return redirect('search_topic', search_phase=slugify(form.cleaned_data.get('search_text')))
            else:
                return redirect('search_post', search_phase=slugify(form.cleaned_data.get('search_text')))
        return redirect('home')

class SearchView(BasicSearchView):
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['form'] = SearchForm()
        return super().get_context_data(**kwargs)

class BoardListView(BasicSearchView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        kwargs['form'] = SearchForm()
        return super().get_context_data(**kwargs)

class TopicListView(BasicSearchView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['form'] = SearchForm()
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

class SearchTopicView(SearchView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'search_topic.html'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset.filter(subject__contains=self.kwargs['search_phase'].replace('-',' '))

class PostListView(BasicSearchView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):

        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['form'] = SearchForm()
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

class SearchPostView(SearchView):
    model = Post
    context_object_name = 'posts'
    template_name = 'search_post.html'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('created_at')
        return queryset.filter(message__contains=self.kwargs['search_phase'].replace('-',' '))

class NewTopicView(LoginRequiredMixin, CreateView):
    form_class = NewTopicForm
    template_name = 'new_topic.html'

    def get_context_data(self, *args, **kwargs):
        context = super(NewTopicView, self).get_context_data(*args, **kwargs)
        board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        context['board'] = board
        return context
 
    def form_valid(self, form):
        topic = form.save(commit=False)
        topic.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        topic.starter = self.request.user
        topic.save()
        post = Post.objects.create(
            message=form.cleaned_data.get('message'),
            image=form.cleaned_data.get('image'),
            topic=topic,
            created_by=self.request.user
        )
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)

class ReplyTopicView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'reply_topic.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ReplyTopicView, self).get_context_data(*args, **kwargs)
        topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        context['topic'] = topic
        return context
 
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        form.instance.topic.last_updated = timezone.now()
        form.instance.topic.save()
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)