#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Pool


class BasePage(object):
    num = -1
    
    @classmethod
    def change_num(cls, num):
        cls.num = num

    @staticmethod
    def _pool(run):
        base_page = BasePage()
        base_page.change_num(run)
        print("num: {}".format(base_page.num))
        print("num: {}".format(BasePage.num))

if __name__ == "__main__":
    
    runs = [1, 2]
    pool = Pool(processes=len(runs))

    for run in runs:
        pool.apply_async(BasePage._pool,
                                 args=(run,))
    print('Waiting for all runs done........ ')
    pool.close()
    pool.join()
    print('All runs done........ ')