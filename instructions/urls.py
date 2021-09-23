from rest_framework.routers import DefaultRouter

from .views import InstructionPageViewSet

app_name = 'instructions'

router = DefaultRouter()
router.register('instruction_pages', InstructionPageViewSet, basename='instruction_page')

urlpatterns = router.urls
