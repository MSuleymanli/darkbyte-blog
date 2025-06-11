from django.contrib import admin
from .models import *
from django import forms

# # Register your models here.
    
class DisclosuresPhotoInline(admin.TabularInline):
    model = DisclosuresPhoto
    extra = 1
    fields = ('screenshots',)

class DisclosuresTagInline(admin.TabularInline):
    model = DisclosuresTag
    extra = 1
    fields = ('tag', 'status')

@admin.register(Disclosures)
class DisclosuresAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'status', 'view_number')
    inlines = [DisclosuresTagInline, DisclosuresPhotoInline]
    exclude = ('view_number','tags')
    list_filter = ('status', 'company')
    search_fields = ('title', 'company__company_name')
       

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

class CompanyTagInline(admin.TabularInline):
    model = Company.tags.through
    extra = 1
    fields = ('tag', 'status')
    
class CompanyFilterInline(admin.TabularInline):
    model=Company.filters.through
    extra=1
    fields = ('filter',)
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('filter') 

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name','hidden', 'country', 'completed_disclosures', 'all_disclosures', 'view_number')
    inlines = [CompanyTagInline,CompanyFilterInline]
    exclude = ('completed_disclosures', 'all_disclosures', 'view_number')





class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'get_node', 'get_disclosure', 'id')
    search_fields = ('name', 'id')
    list_filter = ('node',)

    def get_node(self, obj):
        return obj.node.title if obj.node else None
    get_node.short_description = 'Node Title'

    def get_disclosure(self, obj):
        return obj.node.disclosure.title if obj.node and obj.node.disclosure else None
    get_disclosure.short_description = 'Disclosure Title'


class TreeNodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'isLeaf', 'key', 'get_disclosure')
    search_fields = ('title', 'id')
    exclude = ('key',)

    def get_disclosure(self, obj):
        return obj.disclosure.title if obj.disclosure else None
    get_disclosure.short_description = 'Disclosure Title'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':

            kwargs['queryset'] = TreeNode.objects.filter(isLeaf=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(TreeNode, TreeNodeAdmin)
admin.site.register(File, FileAdmin)
# # admin.site.register(Contact)

@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    list_display=('name','count','id')
    exclude=('count',)
    
# # @admin.register(News)
# # class NewsADmin(admin.ModelAdmin):
# #     list_display=('title','date')
    
# # @admin.register(ShopProduct)
# # class ShopProductAdmin(admin.ModelAdmin):
# #     list_display=('title','company','numberOfHosts','price')
    

# # @admin.register(AuctionItem)
# # class AuctionItemAdmin(admin.ModelAdmin):
# #     list_display=('title','countryName','price')