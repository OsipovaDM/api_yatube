from django.core.exceptions import PermissionDenied
from rest_framework import viewsets

from posts.models import Comment, Group, Post
from .serializers import CommentSerializer, GroupSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    '''
    любые операции CRUD с моделью
    '''
    # выборка объектов модели, с которой будет работать вьюсет
    queryset = Post.objects.all()
    # какой сериализатор будет применён для валидации и сериализации
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(PostViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        return super().perform_destroy(instance)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Возвращает информацию без возможности изменения или записи
    '''
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    # queryset во вьюсете не указываем
    # Нам тут нужны не все комментарии, а только связанные с котом с id=post_id
    # Поэтому нужно переопределить метод get_queryset и применить фильтр

    def get_queryset(self):
        # Получаем id из эндпоинта
        post_id = self.kwargs.get("post_id")
        # И отбираем только нужные комментарии
        new_queryset = Comment.objects.filter(post=post_id)
        return new_queryset

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user, post_id=post_id)
        else:
            raise PermissionDenied("Пользователь не авторизован.")

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(CommentViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        return super().perform_destroy(instance)
