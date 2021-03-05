from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView
from membership.models import UserMembership, Subscription, StripeSubscription
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
from django.conf import settings
import stripe
from main_entrance.models import User
import datetime
from django.contrib.auth.decorators import login_required
# class MembershipView(LoginRequiredMixin, ListView):


#     login_url = 'main_entrance:login'
#     # redirect_field_name= 'main_entrance/index.html'

#     model = Membership
#     template_name = 'membership/list.html'
#     context_object_name = 'memberships'
#     def get_user_membership(self, request):
#         user_membership_qs = UserMembership.objects.filter(user=self.request.user)
#         if user_membership_qs.exists():
#             return user_membership_qs.first()
#         return None

#     def get_queryset(self):
#         # Call all data from set fgrom model
#         qs = {
#             'all_memberships' : Membership.objects.all(),
#             'paid_memberships' : Membership.objects.all().filter(membership_type__startswith='T'),
#             'free_membership' : Membership.objects.all().filter(membership_type__startswith='PA').first(),
#             'user_membership' : UserMembership.objects.filter(user=self.request.user).first()
#         }
#         return qs


#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # current_membership = self.get_user_membership(self.request)
#         # context['current_membership'] = str(current_membership.membership)
#         return context

class UserProfileView(LoginRequiredMixin, TemplateView):
    login_url = 'main_entrance:login'
    # redirect_field_name= 'main_entrance/index.html'
    template_name = 'membership/profileview.html'


class SubscribeView(LoginRequiredMixin, TemplateView):
    login_url = 'main_entrance:login'
    # redirect_field_name= 'main_entrance/index.html'
    template_name = 'membership/subscribe.html'

@csrf_exempt
def strip_config(request):
    if request.method == 'GET':
        strip_config={'publicKey' : settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(strip_config, safe=False)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'membership/subscribe_success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'membership/subscribe_cancel/',
                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        'price': settings.STRIPE_PRICE_ID,
                        'quantity': 1,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


class SubscribeSuccessView(LoginRequiredMixin, TemplateView):
    login_url = 'main_entrance:login'
    # redirect_field_name= 'main_entrance/index.html'
    template_name = 'membership/subscribe_success.html'

class SubscribeCancelView(LoginRequiredMixin, TemplateView):
    login_url = 'main_entrance:login'
    # redirect_field_name= 'main_entrance/index.html'
    template_name = 'membership/subscribe_cancel.html'



@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    print("****SOMETHING SENT****")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fetch all the required data from session
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        print(stripe_customer_id)
        stripe_subscription_id = session.get('subscription')

        # Get the user and create a new StripeCustomer
        user = User.objects.get(id=client_reference_id)
        try:
            # Update if exists
            stripe_subscription = StripeSubscription.objects.get(user=user)
            print("STRIPE SUBSCRIPTION EXISTS FOR THIS USER. UPDATING")
            stripe_subscription.stripe_customer_id=stripe_customer_id
            stripe_subscription.stripe_subscription_id=stripe_subscription_id
            stripe_subscription.save()
        except:
            # Else create
            print("STRIPE SUBSCRIPTION FOR THIS uSER DOESNT EXIST -  CREATING")
            StripeSubscription.objects.create(
                user=user,
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=stripe_subscription_id,
            )
        # Give points and activate subscription
    if event['type'] == 'invoice.paid':
        # this is also what we will receive when a monthly payment is made, so could hook renewal to this9
        # This seems to be what strip recommends
        # Ok so create customer in DB wth checkout complete]
        # get customer dets and add points/dates etc with invoice paid
        # this will repeat every month
        print("They have paid")
        session = event['data']['object']
        customer_id = session.get('customer')
        print(customer_id)
        stripe_subscription = StripeSubscription.objects.get(stripe_customer_id=customer_id)
        user = stripe_subscription.user
        print(user.username)
        user_membership = UserMembership.objects.get(user=user)
        current_points = user_membership.user_points
        print(current_points)
        user_membership.user_points = int(current_points) + 300000
        user_membership.save()
        user_subscription = Subscription.objects.get(user_membership=user_membership)
        user_subscription.active = True
        lines = session.get('lines')
        period = dict(lines)
        # I dont like this but there doesn't seem to be a way around it
        # What if lines changes?
        original_period_end = period['data'][0]['period']['end']
        original_period_end_formatted = datetime.datetime.utcfromtimestamp(original_period_end).strftime('%Y-%m-%d')
        leeway_period_end = original_period_end + (60*60*24*1.5)
        leeway_period_end_formatted = datetime.datetime.utcfromtimestamp(leeway_period_end).strftime('%Y-%m-%d')
        # Remember to add somthing to period end *****HEREREREERE********
        print("there original period end is " + str(original_period_end_formatted))
        print("there period end with leeway is " + str(leeway_period_end_formatted))
        user_subscription.active_until = leeway_period_end
        user_subscription.save()
        print(user.username + ' just paid. There points are now ' + str(user_membership.user_points) + ' and it is ' + str(user_subscription.active) + ' that there subscription is active. ' )



    return HttpResponse(status=200)

@login_required
def cancel_subscription(request):
    user = request.user
    # Might want to add subscribedpermission class here
    if user.is_authenticated:
        stripe_details = StripeSubscription.objects.get(user=user)
        sub_id = stripe_details.stripe_subscription_id
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            response_obj = stripe.Subscription.delete(sub_id)
            # need to convert from unix to real date
            period_start_date = datetime.datetime.utcfromtimestamp(response_obj['current_period_start']).strftime('%Y-%m-%d')
            period_end_date = datetime.datetime.utcfromtimestamp(response_obj['current_period_end']).strftime('%Y-%m-%d')
            context = {
                'period_start_date':period_start_date,
                'period_end_date': period_end_date,
            }
            return render(request, 'membership/cancel_subscription.html', context)
        except Exception as e:
            return JsonResponse({'error': (e.args[0])}, status =403)

    return redirect("main_entrance:index")

# def cancel_subscription_success(request):
#     user=request.user
#     # Need for cancel user
#     # membership end date, 