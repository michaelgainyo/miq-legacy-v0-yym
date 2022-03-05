
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, LoginRequiredMixin)


from blog.models import Category


__all__ = [
    'CategoryListView', 'CategoryCreateView',
    'CategoryUpdateView', 'CategoryDeleteView',
]


class Mixin(LoginRequiredMixin, PermissionRequiredMixin):
    app_name = 'blog'
    model = Category
    filter_by_user = False


class EditMixin(Mixin):
    fields = ['name', 'description']
    template_name = 'blog/staff/category/edit.html'
    success_url = reverse_lazy('blog:category_list')

    def __init__(self, *args, **kwargs):

        try:
            self.form_class = self.get_form_class()
        except Exception:
            pass
        else:
            for field in iter(self.form_class.base_fields):
                self.form_class.base_fields[field].widget.attrs.update(
                    {'class': 'form-control'})

            self.fields = None

        finally:
            super().__init__(*args, **kwargs)

    def form_invalid(self, form):
        from pprint import pprint

        pprint(self.request.POST)

        return super().form_invalid(form)


class CategoryListView(Mixin, generic.ListView):
    paginate_by = 24
    permission_required = 'blog.view_category'
    template_name = 'blog/staff/category/list.html'


class CategoryCreateView(EditMixin, generic.edit.CreateView):
    permission_required = 'blog.add_category'


class CategoryUpdateView(EditMixin, generic.edit.UpdateView):
    permission_required = 'blog.change_category'


class CategoryDeleteView(Mixin, generic.DeleteView):
    success_url = reverse_lazy('blog:category_list')
    permission_required = 'blog.delete_category'
    template_name = 'staff/confirm-delete.html'
