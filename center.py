import zhipuPic
import zhipuVid
import wenxin
import zhipuGLM

def 调用(mode, s):
    try:
        mode = int(mode)
    except Exception:
        print("模式出错")
        return 0
    if mode == 1:
        zhipuPic.main(s, 0)
    elif mode == 2:
        zhipuVid.main(s, 0)
    elif mode == 3:
        zhipuGLM.main(s)
    elif mode == 4:
        print(wenxin.main(s))
    elif mode == 5:
        pic = zhipuPic.main(s, 1)[0]
        zhipuVid.main(s, 0, pic)
    else:
        print("模式出错")
        return 0
