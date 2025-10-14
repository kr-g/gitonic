import os

from PIL import Image, ImageTk, ImageDraw, ImageFont

from material_fonts import read_codepoints, get_ttf_files, BASEDIR

HEIGHT = 20

_codepoint_cache = {}
_font_cache = {}


def get_font(pos, font_size):
    global _font_cache
    fid = (pos, font_size)

    if fid not in _font_cache:

        if pos not in _codepoint_cache:
            codepoints = read_codepoints(pos)
            _codepoint_cache[pos] = codepoints

        ttf_file = get_ttf_files()[pos]
        ttf_file = os.path.join(BASEDIR, ttf_file)

        assert os.path.exists(ttf_file)

        ttf = ImageFont.truetype(ttf_file, size=font_size)

        _font_cache[fid] = ttf

    return _codepoint_cache[pos], _font_cache[fid]


def get_font_icon(
    name, pos=0, height=HEIGHT, image_size=None, bg="white", fg="black"
):

    codepoint, ttf = get_font(pos, height)

    if image_size is None:
        image_size = (height, height)

    unicode_ic = codepoint[name]
    unicode_text = chr(unicode_ic)

    return create_font_icon(unicode_text, ttf, image_size, bg=bg, fg=fg)


def create_font_icon(unicode_text, font, image_size, bg="white", fg="black"):

    imag = Image.new(mode="RGB", size=image_size, color=bg)
    draw = ImageDraw.Draw(im=imag)

    height_2 = font.size / 2

    sx = int(image_size[0] / 2)
    sy = int(image_size[1] / 2)

    # print(unicode_text, font, image_size,)

    draw.text(xy=(sx, sy), text=unicode_text, font=font, fill=fg, anchor="mm")

    im = ImageTk.PhotoImage(imag)

    return im


def get_icon(ico):
    return get_font_icon(
        ico, style="solid", height=19, image_size=(23, 23), bg="lightgrey"
    )
