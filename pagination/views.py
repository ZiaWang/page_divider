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
