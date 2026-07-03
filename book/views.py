from rest_framework import viewsets
from book.models import Book
from book.serializers import BookSerializer
from book.permissions import IsAdminOrReadOnly


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)
