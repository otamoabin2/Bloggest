from django.shortcuts import render, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from .models import Post, Comment
from .forms import CommentForm

class Home(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering =  '-pub_date'
    paginate_by = 3


class Dashboard(View):
    def get(self, request, *args, **kwargs):
        view = Home.as_view(
            template_name = 'blog/admin_page.html',
            paginate_by = 4
        )
        return view(request, *args, **kwargs)


class PostDisplay(DetailView):
    model = Post
    def get_object(self):
        object = super(PostDisplay, self).get_object()
        object.view_count += 1
        object.save()
        return object
    
    def get_context_data(self, **kwargs):
        context = super(PostDisplay, self).get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.get_object())
        context['form'] = CommentForm
        return context


class PostComment(FormView):
    form_class = CommentForm
    template_name = 'blog/post_detail.html'

    def form_valid(self, form):
        form.instance.by = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        form.instance.post = post
        form.save()
        return super(PostComment, self).form_valid(form)

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.kwargs['pk']})


class PostDetail(View):
    def get(self, request, *args, **kwargs):
        view = PostDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostComment.as_view()
        return view(request, *args, **kwargs)


class PostCreate(CreateView):
    model = Post
    fields = ('title', 'category', 'content')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super(PostCreate, self).form_valid(form)


class PostUpdate(UpdateView):
    model = Post
    fields = ('title', 'category', 'content')


class PostDelete(DeleteView):
    model = Post
    success_url = reverse_lazy('dashboard')