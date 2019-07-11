from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from .serializers import ProductSerializer
from .models import Product


class ProductsPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class ListProducts(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('id',)
    search_fields = ('name', 'description',)
    pagination_class = ProductsPagination

    def get_queryset(self):
        on_sale = self.request.query_params.get('on_sale', None)
        if on_sale is None:
            return super().get_queryset()

        queryset = Product.objects.all()

        if on_sale.lower() == 'true':
            from django.utils import timezone
            now = timezone.now()
            return queryset.filter(
                sale_start__lte=now,
                sale_end__gte=now,
            )
        return queryset


class CreateProduct(CreateAPIView):
  serializer_class = ProductSerializer


  def create(self, request, *args, **kargs):
    try:
      price = request.data.get('price')
      if price is not None and float(price) <= 0.0:
        raise ValidationError({'price': 'Cannot be 0 or below'})
    except ValueError:
        raise ValidationError({'price': 'Must be a number'})
    return super().create(request, *args, **kargs)
