from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'page_number': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'result': data
        })

