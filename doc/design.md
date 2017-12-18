# 分页器设计

## 分析
- 分页器应用最多的两个地方就是后台管理以及数据信息展示。在后台管理中，经常遇到的就是对数据进行"增、删、改、查"操作；而在数据信息展示中，比如在常见的博客页面，将文章一页页的展示，这个时候分页的作用就仅仅只是为了显示了

#### 作为后台管理时要注意的细节
- **后台管理进行查询、编辑操作(当然也可以有其他需求)的时候，在完成编辑操作之后，我们需要保证重定向到的列表信息页面是和点击编辑时所在的同一个页面，这样就保证了你在编辑完一条记录之后能够在重定向的页面上直接的看到这条修改之后的记录，而不需要再重新一页页的寻找这条记录**


#### 保存查询/编辑记录
- 要想在编辑完已提交记录之后，能够**保存之前的查询条件并重定向回到之前的位置，需要在进入编辑页面的时候，携带上查询条件/页码信息等，这样在视图函数中我们可以利用传送过来的信息重新组装重定向的url路径，达到返回的页面仍然具备编辑前的状态（查询条件和页面信息）**




## 设计
#### 数据准备
1. 创建模型
	- 这个模型用来测试分页功能

```python
from django.db import models


class Host(models.Model):
    """ 主机信息表
    普通字段:
        id, ip, port
    """

    ip = models.GenericIPAddressField(protocol='ipv4', verbose_name='主机IP地址')
    port = models.IntegerField(verbose_name='端口')

    class Meta:
        verbose_name_plural = '主机信息表'
        unique_together = (('ip', 'port'),)

```

2. 录入数据
	- 为了快速方便，者里使用randint生成了123条记录，代码如下 


```
# 路由

from django.urls import path

from pagination import views

urlpatterns = [
    path('insert_value/', views.insert_value),
]

```


```
# 视图函数
from django.shortcuts import render, HttpResponse

from pagination import models


def insert_value(request):
    """ 准备数据， 模拟生成123条主机信息记录

    """
    from random import randint
    host_list = []
    for i in range(123):
        ip = '%s.%s.%s.%s' % (randint(1, 255), randint(1, 255), randint(1, 255), randint(1, 255))
        port  = randint(1, 65535)

        obj = models.Host(ip=ip, port=port)
        if obj in host_list:            # 剔除可能重复的情况
            continue
        host_list.append(obj)

    models.Host.objects.bulk_create(host_list)
    return HttpResponse("ok")
```

- 当执行完插入数据操作，页面返回一个ok之后，代表数据插入完成了，这个时候就可以从路由和视图函数中去除上述代码了

3. 创建Paingator类

```
from copy import deepcopy

class Paingator:
    def __init__(self, request, base_url, obj_list, params=None, per_page_count=10, init_page_count=11):
        """ 初始化Paingator的实例
        Args:
            request: 当前请求对象
            base_url: 用于拼接页码超链接的url
            params: 存放列表页面的搜索条件，生成页码超链接时需要将其拼接在url的查询部分，保证重定向到列表页面时仍然是之前的查询条件
            obj_list: 要分页显示的所有记录对象
            per_page_count: 每一页要显示记录对象数量，默认位10
            init_page_count: 页面中页码的个数，默认位11
        """

        self.total_count = len(obj_list)
        self.per_page_count = per_page_count
        self.init_page_count = init_page_count
        self.half_page_num = int((init_page_count-1)/2)
        self.request = request
        self.base_url = base_url

        params = deepcopy(params)
        params._mutable = True
        self.params = params
        self.max_page_num, div = divmod(self.total_count, per_page_count)
        if div:  # 获取最大分页数量
            self.max_page_num += 1
            
        try:    # 验证客户端提供的页码
            self.current_page_num = int(request.GET.get('page', 1))
        except Exception as e:
            print(e)
            self.current_page_num += 1
        
        # 生成页面上的起始页码和终止页码
        if self.max_page_num <= init_page_count:
            self.page_start_num = 1
            self.page_end_num = self.max_page_num
        else:
            if self.current_page_num <= self.half_page_num:
                self.page_start_num = 1
                self.page_end_num = init_page_count
            elif self.current_page_num + self.half_page_num >= self.max_page_num:
                self.page_start_num = self.max_page_num - init_page_count
                self.page_end_num = self.max_page_num
            else:
                self.page_start_num = self.current_page_num - self.half_page_num
                self.page_end_num = self.current_page_num + self.half_page_num


    @property
    def start(self):
        """ 返回当前页面第一个对象在对象列表中的索引

        """

        return (self.current_page_num - 1) * self.per_page_count

    @property
    def end(self):
        """ 返回当前页面最后一个对象在对象列表中的索引

        """

        return self.current_page_num * self.per_page_count

    def page_html(self):
        """ 生成页面上的页码超链接

        """

        page_link_list = []
        for i in range(self.page_start_num, self.page_end_num + 1):
            self.params['page'] = i
            if i == self.current_page_num:
                page_link_list.append('<a class="page active" href="%s?%s">%s</a>' % (self.base_url, self.params.urlencode(), i))
            else:
                page_link_list.append('<a class="page"href="%s?%s">%s</a>' % (self.base_url, self.params.urlencode(), i))
        page_link_list = ''.join(page_link_list)
        return page_link_list
```


4. 使用

```
from django.shortcuts import render, redirect
from django.http import QueryDict
from django.forms import ModelForm

from pagination import models
from pagination.pagintator import Paingator


def list_host(request):
    """ 主机信息表路由对应视图函数

    """

    hosts = models.Host.objects.all()
    pagination_obj = Paingator(
        request=request,
        base_url=request.path_info,
        obj_list=hosts,
        per_page_count=8,
        init_page_count=7,
        params=request.GET
    )
    host_list = hosts[pagination_obj.start:pagination_obj.end]
    page_link_list = pagination_obj.page_html()
    
    params = QueryDict(mutable=True)
    params['_list_filter'] = request.GET.urlencode()
    list_condition = params.urlencode()
    return render(request, 'list.html', {"host_list": host_list,
                                         "page_link_list": page_link_list,
                                         "list_condition": list_condition})


def edit_host(request, host_id):
    """ 编辑页面路由对应视图函数
    Args:
        host_id: 要被编辑的host记录的id
    """

    # 创建ModelForm派生类，用于表单相关操作
    host_fields = {
        "model": models.Host,
        "fields": "__all__"
    }
    Meta = type("Meta", (object, ), host_fields)
    HostModelForm = type('HostModelForm', (ModelForm,), {"Meta": Meta})

    if request.method == 'GET':
        form = HostModelForm()
        return render(request, 'edit.html', {"form": form})
    else:
        host = models.Host.objects.filter(id=host_id).first()
        list_filter = request.GET.get('_list_filter')
        form = HostModelForm(data=request.POST, instance=host)
        if form.is_valid():
            form.save()
            return redirect('/list/?%s' % list_filter)
        else:
            return render(request, 'edit.html', {"form": form})
```


