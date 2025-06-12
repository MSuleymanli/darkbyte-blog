from django.test import tag
from rest_framework import serializers
from ..models import *

# class FilterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Filter
#         fields = ['id', 'name','count']

class CompanySerializer(serializers.ModelSerializer):
    employees_count = serializers.IntegerField(source='employee_set.count', read_only=True)
    unix_date = serializers.SerializerMethodField()
    tag_names = serializers.SerializerMethodField()
    # filters = FilterSerializer(many=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'company_name', 'country', 'flag','logo', 'revenue', 
            'employees', 'all_disclosures', 'completed_disclosures', 'date', 
            'unix_date', 'employees_count', 'tag_names','view_number','link'
        ]
        
    def get_unix_date(self, obj):
        fetch_time = timezone.now()
        date_time = obj.date

        time_difference = date_time - fetch_time

        if time_difference.total_seconds() < 0:
            return 0

        return int(time_difference.total_seconds() * 1000)

    def get_tag_names(self, obj):
        company_tags = obj.companytag_set.prefetch_related('tag').all()
        return [
            {"name": company_tag.tag.name, "status": company_tag.status}
            for company_tag in company_tags
        ]
        
class AddCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model=Company
        fields=['company_name', 'country', 'revenue','flag','logo','employees']
        
        
class DisclosuresPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model=DisclosuresPhoto
        fields = ['id', 'screenshots']
        
class DisclosuresSerializer(serializers.ModelSerializer):
    screenshots = serializers.SerializerMethodField()
    tag_details = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    files = serializers.SerializerMethodField()
    zip_link = serializers.SerializerMethodField()
    unix_date = serializers.SerializerMethodField()

    class Meta:
        model = Disclosures
        fields = [
            'id', 'screenshots', 'title', 'filesCount', 'filesSizes', 'description', 
            'view_number', 'status', 'zip_link','unix_date', 'company', 'company_name', 'tag_details', 'files'
        ]
        
    def get_unix_date(self, obj):
        fetch_time = timezone.now()
        date_time = obj.date

        time_difference = date_time - fetch_time

        if time_difference.total_seconds() < 0:
            return 0

        return int(time_difference.total_seconds() * 1000)

    def get_screenshots(self, obj):
        photos = obj.disclosuresphoto_set.all()
        return [
            {
                "id": photo.id,
                "url": photo.screenshots.url if photo.screenshots else None
            }
            for photo in photos
        ]

    def get_tag_details(self, obj):
        disclosure_tags = obj.disclosurestag_set.all()
        return [
            {
                "id": disclosure_tag.tag.id,
                "name": disclosure_tag.tag.name,
                "status": disclosure_tag.status
            }
            for disclosure_tag in disclosure_tags
        ]

    def get_files(self, obj):
        root_nodes = TreeNode.objects.filter(disclosure=obj, parent=None).distinct()
        return TreeNodeSerializer(root_nodes, many=True).data

    def get_zip_link(self, obj):
        if obj.date > now():
            return ""
        return obj.zip_link
    
        
class AddDisclosuresSerializer(serializers.ModelSerializer):
    screenshots = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Disclosures
        fields = ['company', 'title', 'filesCount', 'filesSizes', 'view_number', 'description', 'tags', 'status', 'screenshots']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        screenshots_data = validated_data.pop('screenshots', [])

        disclosures_instance = Disclosures.objects.create(**validated_data)

        disclosures_instance.tags.set(tags_data)

        for screenshot in screenshots_data:

            DisclosuresPhoto.objects.create(
                disclosures=disclosures_instance,
                screenshots=screenshot
            )
        return disclosures_instance
    
class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'name', 'file']

class TreeNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = TreeNode
        fields = ['key', 'title', 'isLeaf', 'children','disclosure']

    def get_children(self, obj):

        child_nodes = obj.children.filter(disclosure=obj.disclosure).distinct()
        return TreeNodeSerializer(child_nodes, many=True).data if not obj.isLeaf else []
    
    
# class ActiveUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ActiveUser
#         fields = ['user_id', 'last_seen']
        
# class NewsSerializer(serializers.ModelSerializer):
        
#     class Meta:
#         model = News
#         fields = '__all__'
        
# class ShopProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=ShopProduct
#         fields='__all__'
        
# class AuctionItemSerializer(serializers.ModelSerializer):
#     unix_date = serializers.SerializerMethodField()
#     class Meta:
#         model=AuctionItem
#         fields=['title','price','description','date','countryName','countryFlag','unix_date']
        
#     def get_unix_date(self, obj):
#         fetch_time = timezone.now()
#         date_time = obj.date

#         time_difference = date_time - fetch_time

#         if time_difference.total_seconds() < 0:
#             return 0

#         return int(time_difference.total_seconds() * 1000)
    
# class ContactSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Contact
#         fields='__all__'