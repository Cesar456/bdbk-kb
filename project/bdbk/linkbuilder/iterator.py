from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def iterator(cls, **kwargs):
    all = cls.objects.filter(**kwargs).all()
    paginator = Paginator(all, 100)
    for i in xrange(1, paginator.num_pages+1):
        objs = paginator.page(i)
        for obj in objs:
            yield obj
