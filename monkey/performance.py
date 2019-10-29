#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uiautomator2 import Device
from wsgiref.validate import validator
from tools.date_utils import current_time
from tools.logger import logger
import re
import json
from config import *


class Performance:

    def __init__(self, device: Device, pkg: str):
        self._device = device
        self.pkg = pkg
        self.data = []

    def performance(self):
        raise NotImplementedError()

    def process(self, data: str):
        d = self._device
        try:
            app = d.app_current()
            time = current_time()
            d = {'t': time, 'a': app['activity'], 'd': data}
            logger.info(f'performance 数据 {json.dumps(d)}')
            self.data.append(d)
        except Exception as e:
            logger.exception(f'处理数据异常: \n{e}')

    def save(self):
        """
        缓存data到文件中
        :return:
        """
        cache_path = types[self.__class__.__name__]
        with open(cache_path, 'w') as f:
            f.write(json.dumps(self.data))


class MemInfo(Performance):
    '''
    内存数据:
        Naitve Heap Size 代表最大总共分配空间
        Native Heap Alloc 已使用的内存
        Native Heap Free  剩余内存
        Naitve Heap Size约等于Native Heap Alloc + Native Heap Free
    '''

    def __init__(self, device, pkg):
        super().__init__(device, pkg)

    def performance(self):
        d = self._device
        # dumpsys meminfo com.xueqiu.android |grep "Dalvik Heap"
        output, _ = d.shell('dumpsys meminfo {} |grep "Dalvik Heap"'.format(self.pkg))
        print(output)
        mem = float(output.split()[3]) / 1024


class CPU(Performance):
    def __init__(self, device, pkg):
        super().__init__(device, pkg)

    def performance(self):
        d = self._device

        cpu = d.shell("dumpsys cpuinfo |grep '{}'|awk -F ' '  '{{print $1}}'".format(self.pkg)).output.strip()
        print('cpu: {}'.format(cpu))


class NetWork(Performance):

    def __init__(self, device, pkg):
        super().__init__(device, pkg)

    def performance(self):

        d = self._device
        pid, _ = d.shell(" ps | grep {}  | awk -F ' ' '{{print $2}}'".format(self.pkg))
        uid, _ = d.shell("cat /proc/{}/status |grep Uid | awk -F ' ' '{{print $2}}'".format(pid))

        _, code = d.shell("ls /proc/{}".format(pid))
        if code == 0:
            net_data = d.shell(
                "cat /proc/net/dev |grep eth0 | awk -F ' ' '{{print$2,$10}}'".format(pid)).output.strip().split(' ')
            print(net_data)
        else:
            # 真机
            d.shell('cat /proc/uid_stat/{}/tcp_snd'.format(uid)).output
            d.shell('cat /proc/uid_stat/{}/tcp_rcv'.format(uid)).output


class FPS(Performance):

    def __init__(self, device, pkg):
        super().__init__(device, pkg)

    def performance(self):
        '''
                当渲染时间大于16.67，按照垂直同步机制，该帧就已经渲染超时
                那么，如果它正好是16.67的整数倍，比如66.68，则它花费了4个垂直同步脉冲，减去本身需要一个，则超时3个
                如果它不是16.67的整数倍，比如67，那么它花费的垂直同步脉冲应向上取整，即5个，减去本身需要一个，即超时4个，可直接算向下取整

                最后的计算方法思路：
                执行一次命令，总共收集到了m帧（理想情况下m=128），但是这m帧里面有些帧渲染超过了16.67毫秒，算一次jank，一旦jank，
                需要用掉额外的垂直同步脉冲。其他的就算没有超过16.67，也按一个脉冲时间来算（理想情况下，一个脉冲就可以渲染完一帧）

                所以FPS的算法可以变为：
                m / （m + 额外的垂直同步脉冲） * 60
            '''
        d = self._device

        output, _ = d.shell("dumpsys gfxinfo {}".format(self.pkg))
        # print(output)
        data = re.findall(r'(?<=Execute)([\w\W]+)(?=Stats)', output)
        frames = [x for x in data[0].split('\n') if validator(x)]
        frame_count = len(frames)
        jank_count = 0
        vsync_overtime = 0
        for frame in frames:
            time_block = re.split(r'\s+', frame.strip())

            if len(time_block) == 4:
                process = time_block[2]
                execute = time_block[3]
            elif len(time_block) == 3:
                process = time_block[1]
                execute = time_block[2]
            try:
                render_time = float(time_block[0]) + float(process) + float(execute)
            except Exception as e:
                render_time = 0

            if render_time > 16.67:
                jank_count += 1
                if render_time % 16.67 == 0:
                    vsync_overtime += int(render_time / 16.67) - 1
                else:
                    vsync_overtime += int(render_time / 16.67)
        fps = int(frame_count * 60 / (frame_count + vsync_overtime))
        self.process(fps)


types = {MemInfo.__name__: memory,
         NetWork.__name__: network,
         FPS.__name__: fps,
         CPU.__name__: cpu}
