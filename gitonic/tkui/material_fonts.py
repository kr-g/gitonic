import urllib
import os


GIT_TAG = "master"

baseurl = f"https://github.com/google/material-design-icons/raw/refs/heads/{GIT_TAG}"

endpoints = [
    "LICENSE",
    "variablefont/MaterialSymbolsOutlined%5BFILL,GRAD,opsz,wght%5D.codepoints",
    "variablefont/MaterialSymbolsOutlined%5BFILL,GRAD,opsz,wght%5D.ttf",
    "variablefont/MaterialSymbolsRounded%5BFILL,GRAD,opsz,wght%5D.codepoints",
    "variablefont/MaterialSymbolsRounded%5BFILL,GRAD,opsz,wght%5D.ttf"
]


_cur_path = os.path.dirname(__file__)

BASEDIR = os.path.join(_cur_path, "material_fonts")
os.makedirs(BASEDIR, exist_ok=True)


def normfnam(fnam):
    return os.path.basename(fnam).replace(",", "_").replace("%", "_")


def download():
    for url in endpoints:
        fnam = normfnam(url)
        print("load", fnam)

        url = f"{baseurl}/{url}"

        resp = urllib.request.urlopen(url)
        data = resp.read()

        with open(os.path.join(BASEDIR, fnam), "wb") as f:
            print("write", fnam)
            f.write(data)


def get_codepoints_files():
    return list(map(lambda x: normfnam(x), filter(lambda x: x.endswith(".codepoints"), endpoints)))


def get_ttf_files():
    return list(map(lambda x: normfnam(x), filter(lambda x: x.endswith(".ttf"), endpoints)))


def read_codepoints(pos):
    fnam = get_codepoints_files()[pos]
    with open(os.path.join(BASEDIR, fnam), "r") as f:
        # print("read", fnam)
        data = f.readlines()
    elems = map(lambda x: x.split(), data)
    elems = map(lambda x: (x[0], int(x[1], 16)), elems)
    return dict(elems)


if __name__ == "__main__":
    pass
    download()
