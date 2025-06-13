from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from datetime import timedelta
from django.utils import timezone
from datetime import datetime
import uuid
from django.utils.timezone import now


# Create your models here.


class Company(models.Model):
    company_name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    flag = models.ImageField(upload_to="flag_image/", blank=True, null=True)
    logo = models.ImageField(upload_to="logo_image/", blank=True, null=True)
    revenue = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    employees = models.PositiveIntegerField(default=0, blank=True, null=True)
    all_disclosures = models.PositiveIntegerField(default=0, blank=True, null=True)
    completed_disclosures = models.PositiveIntegerField(default=0, blank=True, null=True)
    date = models.DateTimeField(default=datetime.now)
    tags = models.ManyToManyField('Tag', through='CompanyTag', blank=True)
    filters=models.ManyToManyField('Filter',through='CompanyFilter',blank=True)
    view_number = models.PositiveBigIntegerField(default=0, blank=True, null=True)
    link=models.URLField(blank=True,null=True)
    description=models.TextField(blank=True,null=True)
    hidden=models.BooleanField(default=False)

    def update_disclosure_counts(self):
        """Disclosures verilerini günceller."""
        self.all_disclosures = Disclosures.objects.filter(company=self).count()
        self.completed_disclosures = Disclosures.objects.filter(company=self, status=True).count()
        self.save()

    def __str__(self):
        return self.company_name
    
class CompanyTag(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company} - {self.tag} (Status: {self.status})"
    
class CompanyFilter(models.Model):
    company=models.ForeignKey('Company',on_delete=models.CASCADE)
    filter=models.ForeignKey('Filter',on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.filter) 


class Disclosures(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="disclosures")
    title = models.CharField(max_length=40, blank=True, null=True)
    filesCount = models.PositiveIntegerField(default=0, blank=True, null=True)
    filesSizes = models.CharField(max_length=20,default=0, blank=True, null=True)
    description = models.CharField(max_length=40, blank=True, null=True)
    view_number = models.PositiveIntegerField(default=0, blank=True, null=True)
    zip_link=models.CharField(max_length=500,blank=True,null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    date=models.DateTimeField(default=now())
    
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class DisclosuresPhoto(models.Model):
    disclosures=models.ForeignKey(Disclosures,on_delete=models.CASCADE,blank=True,null=True)
    screenshots=models.ImageField(upload_to='screenshots/',blank=True,null=True)
    class Meta:
        ordering=['id']
    
@receiver(post_save, sender=Disclosures)
def update_company_on_save(sender, instance, **kwargs):
    if instance.company:
        instance.company.update_disclosure_counts()


@receiver(post_delete, sender=Disclosures)
def update_company_on_delete(sender, instance, **kwargs):
    if instance.company:
        instance.company.update_disclosure_counts()
        
class DisclosuresTag(models.Model):
    company = models.ForeignKey('Disclosures', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company} - {self.tag} (Status: {self.status})"


class Tag(models.Model):
    name = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.name
    
    
# class PageVisit(models.Model):
#     created_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Visit ID: {self.id}"

#     def get_view_count(self, time_period):
#         now = timezone.now()
#         if time_period == '24h':
#             start_time = now - timedelta(days=1)
#         elif time_period == '7d':
#             start_time = now - timedelta(weeks=1)
#         elif time_period == '30d':
#             start_time = now - timedelta(days=30)
#         else:
#             raise ValueError("Invalid time period")

#         return PageVisit.objects.filter(
#             created_date__gte=start_time
#         ).count()
        
#     @staticmethod
#     def delete_old_visits():
#         thirty_three_days_ago = timezone.now() - timedelta(days=33)
#         PageVisit.objects.filter(created_date__lt=thirty_three_days_ago).delete()
        

class TreeNode(models.Model):
    title = models.CharField(max_length=255)
    key = models.AutoField(primary_key=True)
    isLeaf = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )
    disclosure = models.ForeignKey(Disclosures, on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return self.title

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/')
    node = models.ForeignKey(
        TreeNode, on_delete=models.CASCADE, related_name='files'
    )
 

    def __str__(self):
        return self.name
    
    
# class ActiveUser(models.Model):
#     user_id = models.CharField(max_length=255, unique=True)
#     last_seen = models.DateTimeField(default=now)
#     @staticmethod
#     def clean_inactive_users(timeout_seconds=300):

#         cutoff = now() - timedelta(seconds=timeout_seconds)
#         ActiveUser.objects.filter(last_seen__lt=cutoff).delete()
    
class Filter(models.Model):
    name = models.CharField(max_length=60, blank=True, null=True)
    count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name if self.name else "Unnamed Filter"
    

@receiver(post_save, sender=CompanyFilter)
def update_filter_count_on_add(sender, instance, **kwargs):

    filter_instance = instance.filter
    filter_instance.count = CompanyFilter.objects.filter(filter=filter_instance).count()
    filter_instance.save()

@receiver(post_delete, sender=CompanyFilter)
def update_filter_count_on_remove(sender, instance, **kwargs):
    
    filter_instance = instance.filter
    filter_instance.count = CompanyFilter.objects.filter(filter=filter_instance).count()
    filter_instance.save()
    
    
# class News(models.Model):
#     title=models.CharField(max_length=200)
#     description=models.TextField()
#     date = models.DateTimeField(default=now)
#     image=models.ImageField(upload_to='news-photo/',blank=True,null=True)
    
#     def __str__(self):
#         return self.title
    
# class ShopProduct(models.Model):
#     title=models.CharField(max_length=40,blank=True,null=True)
#     company=models.CharField(max_length=200 ,blank=True,null=True)
#     numberOfHosts=models.PositiveIntegerField(default=0,blank=True,null=True)
#     price=models.PositiveIntegerField(default=0,blank=True,null=True)
#     av=models.TextField(blank=True,null=True)
#     rights=models.TextField(default='')
    
#     def __str__(self):
#         return self.company
    
# class AuctionItem(models.Model):
#     title=models.TextField()
#     price=models.PositiveIntegerField(default=0)
#     description=models.TextField()
#     date=date = models.DateTimeField(default=datetime.now)
#     countryName=models.TextField()
#     countryFlag=models.ImageField(upload_to='auction-flag/')
    
#     def __str__(self):
#         return self.title
    
# class Contact(models.Model):
#     tox=models.TextField()
#     jabber=models.TextField()
    
#     def __str__(self):
#         return self.tox
    