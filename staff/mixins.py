
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse


class StaffMixin(LoginRequiredMixin):
    pass


class StaffModelMixin(object):
    @property
    def staff_list_url(self):
        return reverse('staff:list', args=[
            self._meta.app_label, str(self._meta.model_name)])

    @property
    def staff_detail_url(self):
        return reverse('staff:detail', args=[
            self._meta.app_label, str(self._meta.model_name), self.id])


class StaffModelEditMixin(object):
    @property
    def staff_create_url(self):
        app = self._meta.app_label
        model = str(self._meta.model_name)
        return reverse(
            f'staff:{app}_{model}_create',
            args=[app, model, self.id])

    @property
    def staff_edit_url(self):
        app = self._meta.app_label
        model = str(self._meta.model_name)
        try:
            return reverse(
                f'staff:{app}_{model}_edit',
                args=[self.id])

        except Exception:
            return reverse(
                'staff:edit',
                args=[app, model, self.id])


class StaffModelDeleteMixin(object):
    @property
    def staff_delete_url(self):
        app = self._meta.app_label
        model = str(self._meta.model_name)
        return reverse(
            f'staff:{app}_{model}_delete',
            args=[app, model, self.id])


class StaffQuerysetMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)
