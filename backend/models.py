from django.db import models

class households(models.Model):
    Hshd_num=models.TextField(null=False, blank=False, primary_key=True)
    Loyalty_flag=models.TextField()
    Age_range=models.TextField()
    Marital_status=models.TextField()
    Income_range=models.TextField()
    Homeowner_desc=models.TextField()
    Hshd_composition=models.TextField()
    Hshd_size=models.TextField()
    Children=models.TextField()

class products(models.Model):
    Product_num=models.IntegerField(null=False, blank=False, primary_key=True)
    Department=models.TextField()
    Commodity=models.TextField()
    Brand_type=models.TextField()
    natural_Organic_Flag=models.TextField()

class transactions(models.Model):
    Hshd_num=models.ForeignKey(households, verbose_name='hshd_id', on_delete=models.CASCADE)
    Basket_num=models.IntegerField(null=False, blank=False)
    Date=models.DateField()
    Product_num=models.ForeignKey(products, verbose_name='product_id', on_delete=models.CASCADE)
    Spend=models.FloatField()
    Units=models.IntegerField()
    Store_region=models.TextField()
    Week_num=models.IntegerField()
    Year=models.IntegerField()

class users(models.Model):
    username= models.TextField(unique=True,primary_key=True,null=False,blank=False)
    password=models.TextField(null=False,blank=False)
    email=models.TextField(null=False,blank=False)



