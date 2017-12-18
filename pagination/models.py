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

