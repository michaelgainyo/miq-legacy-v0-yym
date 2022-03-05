from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect


from config.utils import get_model

from filemgr.forms import ImageUploadForm
from filemgr.models import Image


class ImageUploadView(View):
    def get(self, request):
        imgs = Image.objects.order_by('-created').all()
        return render(
            self.request, 'filemgr/staff/upload.html', {'imgs': imgs})

    def post(self, request, *args, **kwargs):
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():

            app = request.POST.get('app')
            model = request.POST.get('model')
            pk = request.POST.get('pk')

            if pk and app and model:
                obj = get_model(app, model).objects.get(pk=pk)

                form.instance.object_id = pk
                form.instance.content_object = obj
                form.instance.order = obj.images.count() + 1

            form.instance.user = request.user
            img = form.save()

            data = {
                'is_valid': True,
                'url': img.url, 'pk': img.pk,
                'thumb': img.thumbnail.url
            }

            next = request.POST.get('next')
            if next:
                data.update({'next': next})

        else:
            data = {'is_valid': False}

        return JsonResponse(data)


@login_required
def image_deactivate_view(request):
    img = get_object_or_404(Image, pk=request.POST.get('pk'))
    img.delete()
    return redirect(request.POST.get('next'))
