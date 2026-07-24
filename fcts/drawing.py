# 텍스트 줄바꿈
def wrap_text(draw, text, font, max_width):
    lines = []
    current_line = ""

    for char in text:
        test_line = current_line + char
        width = draw.textlength(test_line, font=font)

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char

    if current_line:
        lines.append(current_line)

    return lines


# 줄바꿈 텍스트 그리기
def draw_multiline_text_center(
    draw,
    text,
    font,
    start_y,
    max_width,
    canvas_width,
    fill=(255, 255, 255, 255),
    stroke_width=2,
    stroke_fill=(46, 139, 255, 255),
    line_spacing=4
):
    lines = wrap_text(draw, text, font, max_width)

    line_height = font.size + line_spacing

    for i, line in enumerate(lines):
        line_width = draw.textlength(line, font=font)
        x = (canvas_width - line_width) / 2
        y = start_y + i * line_height

        draw.text(
            (x, y),
            line,
            fill=fill,
            font=font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill
        )
