from rest_framework.routers import DefaultRouter
from transations.views import AccountViewSet, TransationViewSet


router = DefaultRouter()
router.register('account', AccountViewSet, basename='account')
router.register('transaction', TransationViewSet, basename='transaction')

urlpatterns = router.urls