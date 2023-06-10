from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets, filters, exceptions

from .filters import CustomFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrReadOnly
from .serializers import SubscriptionsSerializer, SubscribeSerializer
from .serializers import TagSerializer, IngredientSerializer
from .serializers import RecipeListSerializer, RecipeCreateUpdateSerializer
from .serializers import RecipeShortSerializer
from recipes.models import Recipe, Tag, Ingredient, Favorite, ShoppingСart
from recipes.models import RecipeIngredient
from users.models import Subscribe, User


class SubscriptionsView(ListAPIView):
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class SubscribeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        serializer = SubscribeSerializer(
            data={'user': request.user.id, 'author': id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscribe.objects.filter(
            user=user,
            author=author
        )
        if not subscription:
            return Response(
                'Подписки не существует',
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return Response(
            'Подписка удалена',
            status=status.HTTP_400_BAD_REQUEST,
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminUserOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, **kwargs)
        if self.request.method == 'POST':
            serializer = RecipeShortSerializer(
                recipe,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError('Рецепта нет в избранном.')
            get_object_or_404(Favorite, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, **kwargs)
        if self.request.method == 'POST':
            serializer = RecipeShortSerializer(
                recipe,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            ShoppingСart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            if not ShoppingСart.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError('Рецепта нет в списке.')
            get_object_or_404(ShoppingСart, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        shopping_cart = (
            RecipeIngredient.objects
            .filter(recipe__shoppingcart_recipes__user=request.user)
            .values('ingredient')
            .annotate(amount=Sum('amount'))
        )
        shopping_cart_list = ['Список покупок.\n']
        for cart in shopping_cart:
            ingredient = Ingredient.objects.get(id=cart['ingredient'])
            amount = cart['amount']
            shopping_cart_list.append(
                f'{ingredient.name}, {amount} {ingredient.measurement_unit}\n'
            )
        response = HttpResponse(shopping_cart_list, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response
