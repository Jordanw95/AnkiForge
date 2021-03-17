from django.shortcuts import redirect
from membership.models import Subscription, UserMembership
from django.urls import reverse_lazy

class RedirectMixin:
    """
    Redirect to redirect_url if the test_func() method returns False.
    """

    redirect_url = None

    def get_redirect_url(self):
        """
        Override this method to override the redirect_url attribute.
        """
        redirect_url = self.redirect_url
        if not redirect_url:
            raise ImproperlyConfigured(
                '{0} is missing the redirect_url attribute. Define {0}.redirect_url or override '
                '{0}.get_redirect_url().'.format(self.__class__.__name__)
            )
        return str(redirect_url)

    def test_func(self):
        raise NotImplementedError(
            '{0} is missing the implementation of the test_func() method.'.format(self.__class__.__name__)
        )

    def get_test_func(self):
        """
        Override this method to use a different test_func method.
        """
        return self.test_func

    def dispatch(self, request, *args, **kwargs):
        test_result = self.get_test_func()()
        if not test_result:
            return redirect(self.get_redirect_url())
        return super().dispatch(request, *args, **kwargs)

class LoggedInRedirectMixin(RedirectMixin):
    def test_func(self):
        return self.request.user.is_authenticated

class UserSubscribedMixin(RedirectMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            self.redirect_url = reverse_lazy('main_entrance:index')
            return False
        else:
            user= self.request.user
            # Every user will have UserMembership
            user_membership = UserMembership.objects.get(user=user)
            user_subscription = Subscription.objects.get(user_membership = user_membership)
            if user_subscription.active:
                return True
            else:
                # this should redirect to a page that tells them they need to subscribe
                self.redirect_url = reverse_lazy('membership:subscribe')
                return False

class UserSubscribedWithPointsMixin(RedirectMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            self.redirect_url = reverse_lazy('main_entrance:index')
            return False
        else:
            user= self.request.user
            # Every user will have UserMembership
            user_membership = UserMembership.objects.get(user=user)
            user_subscription = Subscription.objects.get(user_membership = user_membership)
            if user_subscription.active and user_membership.user_points > 0 :
                return True
            else:
                # this should redirect to a page that tells them they need to subscribe
                self.redirect_url = reverse_lazy('membership:subscribe')
                return False
