import codecs
import csv
import  datetime
import io
from collections import defaultdict
import os, sys
from django.db import connection, reset_queries
import time
import functools
from django.db.models import Sum
from django.http import JsonResponse
from backend.models import households,products,transactions,users

from django.db.models.functions import TruncYear
def jsonResponseSender(response):
    response['Access-Control-Allow-Origin'] = "*"
    return response

def hello(request):
    temp={}
    temp['name']='skfnd'
    return jsonResponseSender(JsonResponse(temp))

def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func

def login(request):
    print(request.POST)
    username=request.POST.get('username')
    password=request.POST.get('password')
    temp=users.objects.filter(username=username).all()
    correctpass=temp[0].password if len(temp)!=0 else None
    if(password==correctpass):
        return jsonResponseSender(JsonResponse({'success':True}))
    return jsonResponseSender(JsonResponse({'success': False,'msg': 'Invalid Username or Password' }))

def signup(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    try:
        temp=users(username=username,password=password,email=email)
        temp.save(force_insert=True)
    except Exception as e:
        return jsonResponseSender(JsonResponse({"success":False,"msg":"Username Already Exists"}))
    return jsonResponseSender(JsonResponse({"success": True}))


@query_debugger
def gethsnumdetails(request):
    hsnum=request.GET.get('hsnum', None)
    if hsnum==None or len(hsnum)==0:
        hsnum='0010'
    temp=transactions.objects.filter(Hshd_num=hsnum)\
        .select_related('Hshd_num','Product_num')
        # 'Children','Age_range','Marital_status','Income_range',
        #                           'Homeowner_desc','Hshd_composition','Hshd_size','Children'
        #                                                                   ,'Product_num','Department','Commodity','Brand_type','natural_Organic_Flag')
    results=defaultdict(list)
    for x in temp:
        inddata={}
        inddata['Hshd_num'] = x.Hshd_num.Hshd_num
        inddata['Children']=x.Hshd_num.Children
        inddata['Age_range'] = x.Hshd_num.Age_range
        inddata['Marital_status'] = x.Hshd_num.Marital_status
        inddata['Income_range'] = x.Hshd_num.Income_range
        inddata['Homeowner_desc'] = x.Hshd_num.Homeowner_desc
        inddata['Hshd_composition'] = x.Hshd_num.Hshd_composition
        inddata['Hshd_size'] = x.Hshd_num.Hshd_size
        inddata['Product_num'] = x.Product_num.Product_num
        inddata['Department'] = x.Product_num.Department
        inddata['Commodity'] = x.Product_num.Commodity
        inddata['Brand_type'] = x.Product_num.Brand_type
        results['data'].append(inddata)
    return jsonResponseSender(JsonResponse(results))


def getspendvstime(request):
    spendvstime=transactions.objects.annotate(year=TruncYear('Date')).values('year').annotate(total=Sum('Spend')).values('year','total')
    categories=[]
    values=[]
    for x in spendvstime:
        categories.append(x['year'].year)
        values.append(x['total'])
    return jsonResponseSender(JsonResponse({'categories':categories,'values':values}))

def getspendvstimedetailed(request):
    temp=defaultdict(list)
    labelset=set()
    spendvstime=transactions.objects.values('Product_num__Department').annotate(year=TruncYear('Date')).annotate(total=Sum('Spend'))
    for x in spendvstime:
        temp[x['Product_num__Department']].append(x['total'])
        labelset.add(x['year'].year)
    res=[]
    for x in temp.keys():
        res.append({'name':x,'data':temp[x]})
    return jsonResponseSender(JsonResponse({'categories':list(labelset),'data':res}))

def getmschart(request):
    temp=transactions.objects.values('Hshd_num__Marital_status').annotate(total=Sum('Spend'))
    res=[]
    for x in temp:
        res.append({'name':x['Hshd_num__Marital_status'],'y':x['total']})
    return jsonResponseSender(JsonResponse({'data':res}))


def getincomechart(request):
    temp=transactions.objects.values('Hshd_num__Income_range').annotate(total=Sum('Spend'))
    res=[]
    for x in temp:
        res.append({'name':x['Hshd_num__Income_range'],'y':x['total']})
    return jsonResponseSender(JsonResponse({'data':res}))


def loadcsv(request):
    try:
        pfile=request.FILES.get('pfile').read().decode('utf-8') if request.FILES.get('pfile') else None
        tfile = request.FILES.get('tfile').read().decode('utf-8') if request.FILES.get('tfile') else None
        hsfile = request.FILES.get('hsfile').read().decode('utf-8') if request.FILES.get('hsfile') else None
        if pfile!=None:
            io_string = io.StringIO(pfile)
            productstemp = []
            for row in list(csv.reader(io_string))[1:]:
                productstemp.append(products(
                    Product_num=row[0].strip(),
                    Department=row[1].strip(),
                    Commodity=row[2].strip(),
                    Brand_type=row[3].strip(),
                    natural_Organic_Flag=row[4].strip()
                ))
            products.objects.bulk_create(productstemp, ignore_conflicts=True)

        if hsfile!=None:
            io_string = io.StringIO(hsfile)
            hstemp=[]
            for row in list(csv.reader(io_string))[1:]:
                hstemp.append(households(
                    Hshd_num=row[0].strip(),
                    Loyalty_flag=row[1].strip(),
                    Age_range=row[2].strip(),
                    Marital_status=row[3].strip(),
                    Income_range=row[4].strip(),
                    Homeowner_desc=row[5].strip(),
                    Hshd_composition=row[6].strip(),
                    Hshd_size=row[7].strip(),
                    Children=row[8].strip(),
                ))
            households.objects.bulk_create(hstemp, ignore_conflicts=True)
        if tfile!=None:
            io_string = io.StringIO(tfile)
            tstemp=[]
            for row in list(csv.reader(io_string))[1:10000]:
                tstemp.append(transactions(
                    Hshd_num_id=row[1].strip(),
                    Basket_num=int(row[0].strip()),
                    Date=datetime.datetime.strptime(row[2].strip(), '%d-%b-%y').strftime('%Y-%m-%d'),
                    Product_num_id=row[3].strip(),
                    Spend=float(row[4].strip()),
                    Units=int(row[5].strip()),
                    Store_region=row[6].strip(),
                    Week_num=int(row[7].strip()),
                    Year=int(row[8].strip()),
                ))
            transactions.objects.bulk_create(tstemp, ignore_conflicts=True)
        return jsonResponseSender(JsonResponse({"success":True}))
    except Exception as e:
        print(e)
        return jsonResponseSender(JsonResponse({"success": False,"msg":"Error with the Files you uploaded,Check the files you uploaded"}))


def initialload():
    filepath = '../data/{0}'
    with open(filepath.format('400_products.csv')) as allproducts:
        with open(filepath.format('400_transactions.csv')) as alltransactions:
            with open(filepath.format('400_households.csv')) as allhouseholds:
                preader = csv.reader(allproducts)
                treader = csv.reader(alltransactions)
                hreader = csv.reader(allhouseholds)
                if products.objects.all().count() >0:
                    print(products.objects.all().count())
                    pass
                else:
                    productstemp=[]
                    for row in list(preader)[1:]:
                        productstemp.append(products(
                            Product_num=int(row[0].strip()),
                            Department=row[1].strip(),
                            Commodity=row[2].strip(),
                            Brand_type=row[3].strip(),
                            natural_Organic_Flag=row[4].strip()
                        ))
                    products.objects.bulk_create(productstemp, ignore_conflicts=True)
                if households.objects.all().count() >0:
                    pass
                else:
                    housetemp=[]
                    for row in list(hreader)[1:]:
                        housetemp.append(households(
                            Hshd_num=row[0].strip(),
                            Loyalty_flag=row[1].strip(),
                            Age_range=row[2].strip(),
                            Marital_status=row[3].strip(),
                            Income_range=row[4].strip(),
                            Homeowner_desc=row[5].strip(),
                            Hshd_composition=row[6].strip(),
                            Hshd_size=row[7].strip(),
                            Children=row[8].strip(),
                        ))
                    households.objects.bulk_create(housetemp, ignore_conflicts=True)
                if transactions.objects.all().count() >0:
                    pass
                else:
                    temp=[]
                    for row in list(treader)[1:20000]:
                        obj=transactions(
                            Hshd_num_id=row[1].strip(),
                            Basket_num=int(row[0].strip()),
                            Date=datetime.datetime.strptime(row[2].strip(), '%d-%b-%y').strftime('%Y-%m-%d'),
                            Product_num_id=row[3].strip(),
                            Spend=float(row[4].strip()),
                            Units=int(row[5].strip()),
                            Store_region=row[6].strip(),
                            Week_num=int(row[7].strip()),
                            Year=int(row[8].strip()),
                        )
                        temp.append(obj)
                    transactions.objects.bulk_create(temp,ignore_conflicts=True)
# initialload()
