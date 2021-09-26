import math

from django.shortcuts import render

# Create your views here.
from django.views import View
from goods.models import *
from django.core.paginator import Paginator


class IndexView(View):
    def get(self, request, cid=1, num=1):

        cid = int(cid)
        num = int(num)
        # 查询所有类别信息
        categorys = Category.objects.all().order_by('id')

        # 查询当前类别下的所有信息
        goodslist = Goods.objects.filter(category_id=cid).order_by('id')

        # 进行分页（每页显示8条）
        pager = Paginator(goodslist, 8)

        # 获取当前页的数据
        page_goodsList = pager.page(num)
        # 注意一下这个地方，假如num传过来为2，系统底层自动就把第2页的数据给了page_goodslist 所有传入页面的goodslist就为这个了

        # 每页开始页码
        begin = (num - int(math.ceil(10.0 / 2)))
        if begin < 1:
            begin = 1

        # 每页结束页码
        end = begin + 9
        if end > pager.num_pages:
            end = pager.num_pages

        if end <= 10:
            begin = 1
        else:
            begin = end - 9

        pagelist = range(begin, end + 1)

        return render(request, 'index.html',
                      {'categorys': categorys, 'goodslist': page_goodsList, 'currentcid': cid, 'pagelist': pagelist,
                       'currentNum': num})


# 思考1：最终需要获取的推荐商品，goodsobjlist = 【】
# 思考2：get方法只能获取到每次访客goodsid goodsidlist=【】
# 思考3：将每次访问的商品编号保存下来，将它保存到cookie中
# 思考4：考虑推荐商品展示的先后顺序问题

def recommed_view(func):
    def wrapper(detailView, request, goodsid, *args, **kwargs):
        # 将存放在cookie中的goodsid获取
        cookie_str = request.COOKIES.get('recommend', '')
        goodsidlist = [gid for gid in cookie_str.split() if gid.strip()]  # 存放goodsID放在里面
        # 最终需要获取的推荐商品
        goodsobjlist = [Goods.objects.get(id=gsid) for gsid in goodsidlist if gsid != goodsid and Goods.objects.get(id=gsid).category_id == Goods.objects.get(id=goodsid).category_id][:4]
        # id对象放在里面就是id对应整个商品的属性 查询出来的是整个goodislist的所有对象，但是下面只显示四个，列表切片就可以了
        # 将 goodliest 传给get方法
        response = func(detailView, request, goodsid, goodsobjlist, *args, **kwargs)
        # 这个地方你可以理解为调用了get方法，然后返回给了浏览器一个response对象了，只不过这个地方拿过来了，很基本的通用操作，注意一下
        # 判断 goodsid 是否存在goodsidlist中
        if goodsid in goodsidlist:
            goodsidlist.remove(goodsid)
            goodsidlist.insert(0, goodsid)
        else:
            goodsidlist.insert(0, goodsid)
        # 将goosidlist中的数据保存到cookid中
        response.set_cookie('recommend', ' '.join(goodsidlist), max_age=3 * 24 * 60)
        return response

    return wrapper


class DetailView(View):
    @recommed_view
    def get(self, request, goodsid, recommendlist=[]):
        goodsid = int(goodsid)

        # 根据goodsid查询商品详情信息，（goods对象）
        goods = Goods.objects.get(id=goodsid)

        return render(request, 'detail.html', {'goods': goods, 'recommendlist': recommendlist})
