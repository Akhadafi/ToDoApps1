from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView

from .models import Task


# Auth
class CustomLoginView(LoginView):
    template_name = "backend/login.html"
    fields = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("tasks")


class RegisterPage(FormView):
    template_name = "backend/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("tasks")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("tasks")
        return super(RegisterPage, self).get(*args, **kwargs)


# Create your views here.
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = context["tasks"].filter(user=self.request.user)
        context["count"] = context["tasks"].filter(complete=False).count()

        search_input = self.request.GET.get("search-area") or ""
        if search_input:
            context["tasks"] = context["tasks"].filter(title__icontains=search_input)

        context["search_input"] = search_input

        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"
    template_name = "backend/task.html"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasks")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreateView, self).form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasks")


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("tasks")