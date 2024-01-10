from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminOrReadOnly


class BaseCategoryGenreViewset(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Базовый вюсет для Категорий и Жанров."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
