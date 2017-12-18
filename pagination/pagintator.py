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