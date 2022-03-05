
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages

from sitemgr.utils import is_ajax

from ..models import Image, FileSetting, File, GalleryImage, Gallery

from .forms import ImageUpdateForm, GalleryImageCreateForm
from sitemgr.staff.views import SettingUpdateView


class Mixin(LoginRequiredMixin):
    def post(self, request, *args, **kwargs):
        url = self.request.POST.get('next')
        if url:
            self.success_url = url

        return super().post(request, *args, **kwargs)


class ImgUpdateMixin(Mixin):
    def form_valid(self, form):
        if is_ajax(self.request):
            form.save()
            data = {'is_valid': True}
            obj = None
            field = self.request.POST.get('field')

            if field == 'file':
                obj = self.object.file
            elif field == 'thumbnail':
                obj = self.object.thumbnail
            elif field == 'm_file':
                obj = self.object.m_file
            elif field == 'm_thumbnail':
                obj = self.object.m_thumbnail

            if obj:
                data.update({
                    'img_url': obj.url,
                    'width': obj.width,
                    'height': obj.height,
                    'size': obj.size,
                })

            return JsonResponse(data)

        url = self.object.staff_edit_url
        next = self.request.POST.get('next')
        if next:
            url = next + f'?img={self.object.pk}'

        self.success_url = url

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Something went wrong')
        return super().form_invalid(form)


"""
GALLERY
"""


class GalleryListView(Mixin, PermissionRequiredMixin, generic.ListView):
    model = Gallery
    paginate_by = 50
    permission_required = 'filemgr.view_gallery'
    template_name = 'filemgr/staff/gallery/list.html'


class GalleryCreateView(Mixin, PermissionRequiredMixin, generic.edit.CreateView):
    model = Gallery
    fields = [
        'name', 'description', 'is_slider',
        # 'object_id', 'content_type'
    ]
    permission_required = 'filemgr.add_gallery'
    template_name = 'filemgr/staff/gallery/edit.html'

    def form_valid(self, form):
        app = self.request.POST.get('app')
        model = self.request.POST.get('model')
        pk = self.request.POST.get('pk')

        if pk and app and model:
            from config.utils import get_model

            form.instance.object_id = pk
            form.instance.content_object = get_model(
                app, model).objects.get(pk=pk)

        return super().form_valid(form)


class GalleryUpdateView(Mixin, PermissionRequiredMixin, generic.edit.UpdateView):
    model = Gallery
    fields = ['name', 'description', 'is_slider']
    permission_required = 'filemgr.change_gallery'
    template_name = 'filemgr/staff/gallery/edit.html'
    success_url = reverse_lazy('filemgr:files')

    def form_invalid(self, form):
        print(self.request.POST)
        raise

    def form_valid(self, form):
        if is_ajax(self.request):
            is_slider = form.cleaned_data.get('is_slider')
            if is_slider:
                form.instance.is_slider = False
            else:
                form.instance.is_slider = True

            gal = form.save()

            data = {
                'is_valid': True,
                'checked': gal.is_slider
            }
            return JsonResponse(data)

        return super().form_valid(form)


class GalleryDeleteView(Mixin, PermissionRequiredMixin, generic.DeleteView):
    model = Gallery
    permission_required = 'filemgr.delete_gallery'
    success_url = reverse_lazy('filemgr:files')
    template_name = 'staff/components/confirm-delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back = self.request.META.get('HTTP_REFERER')

        if not back or self.request.path_info in back:
            back = self.success_url

        context.update({
            'back': back
        })
        return context


"""
GALLERY IMAGE
"""


class GalleryImageView(Mixin, PermissionRequiredMixin, generic.ListView):
    model = GalleryImage
    paginate_by = 50
    permission_required = 'filemgr.view_gallery'
    template_name = 'filemgr/staff/gallery/list.html'


class GalleryImageCreateView(Mixin, generic.edit.CreateView):
    model = GalleryImage
    form_class = GalleryImageCreateForm
    template_name = 'filemgr/staff/image/edit.html'

    def form_valid(self, form):
        url = self.request.POST.get('next')
        if not url:
            url = self.object.staff_edit_url
        self.success_url = url

        pk = self.request.POST.get('gallery_pk')
        if pk:
            form.instance.gallery = Gallery.objects.get(pk=pk)

        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Something went wrong')
        return super().form_invalid(form)


class GalleryImageUpdateView(ImgUpdateMixin, generic.edit.UpdateView):
    model = GalleryImage
    fields = [
        'order', 'title', 'description',
        'file', 'thumbnail',
        'm_file', 'm_thumbnail',
        'alt_text', 'external_url',
        'is_explicit']
    template_name = 'filemgr/staff/image/edit.html'


class GalleryImageDeleteView(Mixin, PermissionRequiredMixin, generic.DeleteView):
    model = GalleryImage
    permission_required = 'filemgr.delete_image'
    success_url = reverse_lazy('filemgr:staff_img_list')
    template_name = 'staff/components/confirm-delete.html'

    def get_success_url(self):
        next = self.request.POST.get('next', self.request.GET.get('next'))
        if next:
            return next
        return super().get_success_url()


"""
IMAGE
"""


class ImageListView(Mixin, generic.ListView):
    model = Image
    paginate_by = 50
    ordering = ('-created', )
    template_name = 'filemgr/staff/image/list.html'


class ImgUpdateView(ImgUpdateMixin, generic.edit.UpdateView):
    model = Image
    form_class = ImageUpdateForm
    template_name = 'filemgr/staff/image/edit.html'


class ImageDeleteView(Mixin, PermissionRequiredMixin, generic.DeleteView):
    model = Image
    permission_required = 'filemgr.delete_image'
    success_url = reverse_lazy('filemgr:staff_img_list')
    template_name = 'staff/components/confirm-delete.html'

    def get_success_url(self):
        next = self.request.POST.get('next', self.request.GET.get('next'))
        if next:
            return next
        return super().get_success_url()


"""
FILE
"""


class FileListView(Mixin, PermissionRequiredMixin, generic.ListView):
    model = File
    paginate_by = 50
    permission_required = 'filemgr.view_file'
    template_name = 'filemgr/staff/file/list.html'


class FileUploadView(Mixin, PermissionRequiredMixin, generic.edit.CreateView):
    model = File
    fields = ['name', 'description', 'file']
    permission_required = 'filemgr.add_file'
    template_name = 'filemgr/staff/file/edit.html'
    success_url = reverse_lazy('filemgr:files')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class FileUpdateView(Mixin, PermissionRequiredMixin, generic.edit.UpdateView):
    model = File
    fields = ['name', 'description']
    permission_required = 'filemgr.change_file'
    template_name = 'filemgr/staff/file/edit.html'
    success_url = reverse_lazy('filemgr:files')


class FileDeleteView(ImageDeleteView):
    model = File
    permission_required = 'filemgr.delete_file'
    success_url = reverse_lazy('filemgr:files')
    template_name = 'staff/components/confirm-delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back = self.request.META.get('HTTP_REFERER')

        if not back or self.request.path_info in back:
            back = self.success_url

        context.update({
            'back': back
        })
        return context

    def post(self, request, *args, **kwargs):
        url = self.request.POST.get('next')
        if url:
            self.success_url = url

        return super().post(request, *args, **kwargs)


class FileSettingUpdateView(SettingUpdateView):
    tab = 'file'
    model = FileSetting
    permission_required = 'sitemgr.change_filesetting'
    fields = ['protect_image']
