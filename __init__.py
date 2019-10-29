
import uiautomator2 as u2 
from os import path
import os
from wsgiref.validate import validator
import re
from tools.logger import logger
from config import *

apk_path = path.join('.', 'assert', 'com.xueqiu.android.apk')
print(apk_path)
d = u2.connect()

print(d)

# d.app_uninstall('com.xueqiu.android')
# d.adb_shell("".format(apk_path))

if __name__ == "__main__":
    logger.error("1111")
    logger.warning('22222')
    logger.info("dddd")
    logger.debug("eeeee")

    print(d.app_list())

    print(d.app_list('-3'))

    print(d.app_list('-1'))