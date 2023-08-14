from rest_framework import mixins, viewsets


class AbstractGETViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    pass
