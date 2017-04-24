import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from tmall_list_spider_class import tmall_list_spider_class


if __name__ == '__main__':
    app = tmall_list_spider_class()
    app.do_task('kad')
