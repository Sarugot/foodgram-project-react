from django.urls import path
from api.views import SubscriptionsView, SubscribeView

urlpatterns = [
    path('users/subscriptions/', SubscriptionsView.as_view(),
         name='subscription'),
    path('users/<int:id>/subscribe/', SubscribeView.as_view(),
         name='subscribe'),
]
