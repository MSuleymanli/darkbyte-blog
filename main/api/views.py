from rest_framework.generics import ListAPIView,RetrieveAPIView,CreateAPIView,UpdateAPIView
from ..models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from .mypagination import MyCustomPagination
from rest_framework.permissions import IsAdminUser
from ..utils import admin_cookie_required
from django.utils.decorators import method_decorator



class ModulPagination(PageNumberPagination):
    
    page_size = 10
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


# class FilterApiView(ListAPIView):
#     queryset = Filter.objects.all()
#     serializer_class = FilterSerializer

#     @swagger_auto_schema(tags=['List'])
#     def get(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         filters_data = [
#             {
#                 "id": filter.id,
#                 "name": filter.name,
#                 "count": Company.objects.filter(filters=filter,hidden=False).count()
#             }
#             for filter in queryset
#         ]

#         total_company_count = Company.objects.filter(hidden=False).count()
#         response_data = {
#             "total_company_count": total_company_count,
#             "filters": filters_data
#         }

#         return Response(response_data)
    
    

class CompanyApiView(ListAPIView):
    serializer_class = CompanySerializer

    filter_id_param = openapi.Parameter(
        'filter_id',
        openapi.IN_QUERY,
        type=openapi.TYPE_INTEGER,
        required=False
    )

    def get_queryset(self):

        queryset = Company.objects.filter(hidden=False).order_by('-id')

        filter_id = self.request.query_params.get('filter_id')
        if filter_id:
            queryset = queryset.filter(filters__id=filter_id)

        return queryset

    @swagger_auto_schema(
        tags=['List'],
        manual_parameters=[filter_id_param]
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        filter_id = request.query_params.get('filter_id')
        if filter_id:
            company_count = queryset.count()
            return Response({
                "filter_id": filter_id,
                "company_count": company_count,
                "companies": self.serializer_class(queryset, many=True).data
            })

        company_count = queryset.count()
        return Response({
            "filter_id": None,
            "company_count": company_count,
            "companies": self.serializer_class(queryset, many=True).data
        })   


class DisclosuresDetailApiView(RetrieveAPIView):
    queryset = Disclosures.objects.order_by('-id')
    serializer_class = DisclosuresSerializer

    @swagger_auto_schema(tags=['List'],operation_summary='Disclosures Detail and view number set')
    def get(self, request, *args, **kwargs):
        card = self.get_object()
        card.view_number += 1
        card.save()
        serializer = self.get_serializer(card)
        return Response(serializer.data)


class DisclosuresApiView(ListAPIView):
    serializer_class = DisclosuresSerializer

    @swagger_auto_schema(
        tags=['List'],
        operation_summary='Company id-e gore disclosuresleri tap company viewn_number+1',
        manual_parameters=[
            openapi.Parameter(
                'company_id',
                openapi.IN_QUERY,
                description="Filter disclosures by company ID",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        company_id = request.GET.get('company_id')
        if company_id:
            self.queryset = Disclosures.objects.filter(company_id=company_id).all()
            company = Company.objects.get(id=company_id)
            company.view_number += 1
            company.save()
        else:
            self.queryset = Disclosures.objects.order_by('-id')

        # status true
        for disclosure in self.queryset:
            if disclosure.date <= now() and not disclosure.status:
                disclosure.status = True
                disclosure.save(update_fields=['status'])

        active_disclosures_count = self.queryset.filter(status=True).count()

        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = DisclosuresSerializer(page, many=True)
            return self.get_paginated_response({
                "total_active_disclosures": active_disclosures_count,
                "results": serializer.data
            })

        serializer = DisclosuresSerializer(self.queryset, many=True)
        return Response({
            "total_active_disclosures": active_disclosures_count,
            "results": serializer.data
        })

@method_decorator(admin_cookie_required, name='dispatch')    
class AddDisclosuresView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AddDisclosuresSerializer
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        tags=['Add'],
        operation_summary='Add Disclosure ',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'company': openapi.Schema(type=openapi.TYPE_INTEGER, description="Company ID"),
                'title': openapi.Schema(type=openapi.TYPE_STRING, description="Disclosure Title"),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description="Disclosure Description"),
                'tags': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description="List of Tag IDs"
                ),
                'screenshots': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_FILE),
                    description="List of Screenshot Files"
                ),
                'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Disclosure Status")
            },
            required=['company', 'title', 'description']
        ),
        responses={
            201: "Disclosure created successfully.",
            400: "Invalid input data."
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@method_decorator(admin_cookie_required, name='dispatch')    
class UpdateDisclosureStatusApiView(APIView):
    permission_classes = [IsAdminUser]
    @swagger_auto_schema(
        tags=['Update'],
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description="Disclosure ID"),
            openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description="True or False")
        ],
        responses={
            200: openapi.Response("Status updated successfully."),
            404: openapi.Response("Disclosure not found."),
        }
    )
    def post(self, request, *args, **kwargs):
        disclosure_id = self.kwargs.get('id')
        status_value = request.query_params.get('status', None)
        if status_value is None:
            return Response({"error": "'status' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        if status_value.lower() == "true":
            status_value = True
        elif status_value.lower() == "false":
            status_value = False
        else:
            return Response({"error": "'status' must be 'true' or 'false'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            disclosure = Disclosures.objects.get(id=disclosure_id)

            disclosure.status = status_value
            disclosure.save()
            return Response({"message": f"Disclosure with ID {disclosure_id} status updated to {status_value}."}, status=status.HTTP_200_OK)

        except Disclosures.DoesNotExist:
            return Response({"error": "Disclosure not found."}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(admin_cookie_required, name='dispatch')    
class AddCompanyApiView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AddCompanySerializer
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        tags=['Add'],
        operation_summary='Add a new company',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'company_name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the company"),
                'country': openapi.Schema(type=openapi.TYPE_STRING, description="Country of the company"),
                'revenue': openapi.Schema(type=openapi.TYPE_NUMBER, description="Revenue of the company"),
                'employees': openapi.Schema(type=openapi.TYPE_NUMBER, description="Number of employees"),
                'flag': openapi.Schema(type=openapi.TYPE_STRING, description="Company flag image"),
            },
            required=['company_name', 'country']
        ),
        responses={
            201: "Company successfully added.",
            400: "Invalid input data."
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()
            return Response({'message': 'Company created successfully!', 'company': serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# class PageVisitView(APIView):
#     def post(self, request, *args, **kwargs):
        
#         PageVisit.delete_old_visits()

#         PageVisit.objects.create()
#         return Response({"message": "Page visit counted", "visited": True}, status=status.HTTP_201_CREATED)

#     def get(self, request, *args, **kwargs):
#         visit_count = {
#             "24h": PageVisit.objects.filter(created_date__gte=timezone.now() - timedelta(days=1)).count(),
#             "7d": PageVisit.objects.filter(created_date__gte=timezone.now() - timedelta(weeks=1)).count(),
#             "30d": PageVisit.objects.filter(created_date__gte=timezone.now() - timedelta(days=30)).count(),
#         }

#         visited = request.query_params.get('visited', 'false') == 'true'
#         response_data = {"visit_count": visit_count, "visited": visited}

#         return Response(response_data, status=status.HTTP_200_OK)
    
    
    

# class TreeNodeListAPIView(APIView):
#     def get(self, request):
#         root_nodes = TreeNode.objects.filter(parent=None)
#         serializer = TreeNodeSerializer(root_nodes, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         parent_id = request.data.get('parent')
#         isLeaf = request.data.get('isLeaf', False)

#         # Parent kontrolü
#         if parent_id:
#             try:
#                 parent_node = TreeNode.objects.get(id=parent_id)
#                 if parent_node.isLeaf:
#                     return Response(
#                         {"error": "Cannot add children to a file (isLeaf=True)."},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )
#             except TreeNode.DoesNotExist:
#                 return Response(
#                     {"error": "Parent node not found."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#         else:
#             parent_node = None

#         # Dosya mı klasör mü ekleniyor kontrolü
#         if isLeaf:
#             # Dosya ekleniyor
#             file_serializer = FileSerializer(data=request.data)
#             if file_serializer.is_valid():
#                 file_serializer.save(node=parent_node)
#                 return Response(file_serializer.data, status=status.HTTP_201_CREATED)
#             return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             # Klasör ekleniyor
#             node_serializer = TreeNodeSerializer(data=request.data)
#             if node_serializer.is_valid():
#                 node_serializer.save(parent=parent_node, isLeaf=False)
#                 return Response(node_serializer.data, status=status.HTTP_201_CREATED)
#             return Response(node_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TreeNodeListAPIView(APIView):
    def get(self, request):

        root_nodes = TreeNode.objects.filter(parent=None)
        serializer = TreeNodeSerializer(root_nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
   
# class PingView(APIView):
#     def post(self, request):
#         user_id = request.data.get('user_id')
#         if not user_id:
#             return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
#         ActiveUser.objects.update_or_create(
#             user_id=user_id,
#             defaults={'last_seen': now()}
#         )
#         return Response({'message': 'Ping received'}, status=status.HTTP_200_OK)
        

# class ActiveUsersView(APIView):
#     def get(self, request):

#         ActiveUser.clean_inactive_users()

#         active_user_count = ActiveUser.objects.count()
#         return Response({'active_users': active_user_count}, status=status.HTTP_200_OK)
    

# class NewsApiview(ListAPIView):
#     queryset=News.objects.order_by('-id')
#     serializer_class=NewsSerializer
#     pagination_class = MyCustomPagination
    
#     @swagger_auto_schema(tags=['List'])
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)

  
# class NewsDetailApiView(RetrieveAPIView):
#     queryset=News.objects.all()
#     serializer_class=NewsSerializer
#     lookup_field='pk'
    
#     @swagger_auto_schema(tags=['List'])
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)

  
# class ShopProductApiView(ListAPIView):
#     serializer_class=ShopProductSerializer
#     pagination_class = MyCustomPagination
    
#     def get_queryset(self):
#         shop_id = self.request.query_params.get("id")
#         return ShopProduct.objects.filter(id=shop_id) if shop_id else ShopProduct.objects.order_by("-id")

#     @swagger_auto_schema(
#         tags=['List'],
#         manual_parameters=[
#             openapi.Parameter(
#                 'id', openapi.IN_QUERY, description="ShopProduct ID", type=openapi.TYPE_INTEGER
#             )
#         ]
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)

    
# class AuctionItemApiView(ListAPIView):
#     queryset=AuctionItem.objects.order_by('-id')
#     serializer_class=AuctionItemSerializer
#     pagination_class = MyCustomPagination
    
#     @swagger_auto_schema(tags=['List'])
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)   
    
# class ContactApiview(ListAPIView):
#     queryset=Contact.objects.order_by('-id')
#     serializer_class=ContactSerializer
    
#     @swagger_auto_schema(tags=['List'])
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)  
    