from pytkfaicons.fonts import get_font_icon


def get_icon(ico):
    return get_font_icon(
        ico, style="solid", height=19, image_size=(23, 23), bg="lightgrey"
    )
