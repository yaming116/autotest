#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uiautomator2 as u2
from uiautomator2 import Device
from os import path
import re
import time
from tools.logger import logger
from monkey.performance import FPS


class Monkey(object):
    __CMD = 'CLASSPATH=/sdcard/monkey.jar:/sdcard/framework.jar exec app_process /system/bin ' \
            'tv.panda.test.monkey.Monkey '

    def __init__(self, device: Device):
        d = self._device = device
        self.res_path = path.join(__file__, '../..', 'res')

    def init(self):
        """
        环境初始化, 包括如下步骤:
            1. 清空各种日志信息
            2. 检查必要文件是否存在及版本是否一致: monkey.jar 等
            3. 停止遍历程序及logcat
        """
        logger.info('monkey init')
        if not self.check_install():
            self.push_jar()

        self.clear()

    def push_jar(self):
        logger.info('monkey push_jar')
        d = self._device
        d.push(path.join(self.res_path, 'jar', 'monkey.jar'), '/sdcard/')
        d.push(path.join(self.res_path, 'jar', 'framework.jar'), '/sdcard/')

    def clear(self):
        '''
        清除缓存日志文件
        '''
        logger.info('monkey clear logs')
        pass

    def check_install(self):
        '''
        检查必要
        '''
        logger.info('monkey check install')
        d = self._device
        if d.sync.stat("/sdcard/monkey.jar").size == 0:
            return False

        if d.sync.stat("/sdcard/framework.jar").size == 0:
            return False

        return True

    def list_packages(self) -> list:
        """
        Returns:
            list of package names
        """
        d = self._device
        output, _ = d.shell(['pm', 'list', 'packages'])
        packages = re.findall(r'package:([^\s]+)', output)
        return list(packages)

    def check_monkey_live(self):
        '''
        检查monkey是否在运行中
        '''
        d = self._device
        data = d.shell("ps | grep tv.panda.test.monkey").output.strip()
        if data:
            return True
        return False

    def current_activity(self) -> str:
        '''
        获取当前的activity
        '''
        d = self._device

        activity = d.shell('shell dumpsys activity | grep "mFocusedActivity"').output.strip()
        return activity

    def run(self, pkg, mode='uiautomatormix', runtime=5, **kwargs):
        '''
            启动monkey,统计如下数据: 网络, 内存,cpu,fps
        '''

        if not pkg:
            raise ValueError("pkg is null")

        d = self._device
        packages = self.list_packages()

        if pkg not in packages:
            raise ValueError("{} is not install".format(pkg))

        package = ' -p ' + pkg
        runtime = ' --running-minutes ' + str(runtime)
        mode = ' --' + mode

        off_line_cmd = ' -v -v >/sdcard/monkeyout.txt 2>/sdcard/monkeyerr.txt &'

        monkey_shell = ''.join([self.__CMD, package, runtime, mode, off_line_cmd])

        d.service('uiautomator').stop()
        print(monkey_shell)
        d.shell(monkey_shell)

        # 暂停一下,启动没有那么快
        time.sleep(5)
        is_runing = True
        while is_runing:
            if not self.check_monkey_live():
                is_runing = False
            else:
                self.current_activity()

            time.sleep(5)

        print("game over")


if __name__ == "__main__":
    d = u2.connect()
    print(d)

    monkey = Monkey(d)

    # monkey.run('com.xueqiu.android', runtime=2)

    m = FPS(d, 'com.xueqiu.android')
    import time
    for i in range(50):
        time.sleep(2)
        m.performance()
    m.save()
    # print(" ps | grep {}  | awk -F ' ' '{print $2}'".format('11'))

    # output, _ = d.shell("dumpsys gfxinfo com.xueqiu.android")
    # print(_)
    # print(output)
