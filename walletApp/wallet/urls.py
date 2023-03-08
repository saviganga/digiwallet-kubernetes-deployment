from django.urls import path, include
# from wallet import views as wallet_views
#
# urlpatterns = [
#     path("get/", wallet_views.ViewWallets.as_view()),
# ]

from django.db import router
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("walletbox", views.WalletsBox)
router.register("wallets", views.Wallets)
router.register("entry", views.Entry)
router.register("bank-accounts", views.UserBankAccountView)

urlpatterns = [
    # path("withdraw/", views.Withdraw.as_view())
]
urlpatterns += router.urls
