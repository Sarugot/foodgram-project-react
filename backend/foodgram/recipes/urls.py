from rest_framework.routers import SimpleRouter
from django.urls import include, path

from api.views import TagViewSet, IngredientViewSet, RecipeViewSet

router = SimpleRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
]
