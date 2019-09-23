import time as t
from sasKeypad import sasKeypad
from sasFile import sasFile
keypress = sasKeypad()
fileObject = sasFile()
def digit():
    r = None
    while 1:
        r = keypress.getKey()
        if r != None:
            break
        t.sleep(1)
    return r
if __name__ == '__main__':
    command = '1'
    fileObject.updateDesiredTask('1')
    while True:
      try:
        ch = digit()
        print("Pressed Key is {}".format(ch))
        if (ch == '#'):
            fileObject.updateDesiredTask('2')
            while 1:
                task = fileObject.readDesiredTask()
                if task == '1':
                    break
                else:
                    pass
                t.sleep(1)
        t.sleep(1)
      except Exception as e:
          fileObject.updateExceptionMessage("sasCommand",str(e))
          t.sleep(5)
