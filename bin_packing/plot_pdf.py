from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors


page_width, page_height = A4
WIDTH = 0.7 * page_width
X = (page_width - WIDTH) / 2
margin_between_container_and_heading = 1 * cm
cutting_blade_margin_5mm = 5 / 25.4     # considering 1 point == 1 inch


def draw_heading_container(c, data):
    heading_height = 0.155 * page_height
    heading_y_position = 30
    c.rect(X, heading_y_position, WIDTH, heading_height, stroke=1, fill=0)
    text_x = X + 0.5 * cm
    text_y = heading_y_position + 0.7 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(text_x, text_y, "Quartz Kitchen")
    heading_stats = [
        ("Total area used:", f"{data['total_area_used']} sq. ft."),
        ("Total area wasted:", f"{data['total_area_wasted']} sq. ft."),
        ("Total area of single slab:", f"{data['total_area_of_single_slab']} sq. ft."),
        ("Total area used (%):", f"{data['total_area_used_percent']}%"),
        ("Total area wasted (%):", f"{data['total_area_wasted_percent']}%"),
        ("Total no of slabs used:", f"{data['total_no_of_slabs_used']}"),
        ("Slab Size:", f"{data['slab_length']} x {data['slab_width']}"),
    ]

    c.setFont("Helvetica", 10)
    column_gap = 7 * cm
    for i, (label, value) in enumerate(heading_stats):
        c.drawString(text_x, text_y + 14 * (i + 1), label)
        c.drawString(text_x + column_gap, text_y + 14 * (i + 1), value)

    return heading_y_position + heading_height


def draw_main_container(c, heading_y_end, rectangles, slab_width=138, slab_height=78):
    container_h = 0.3 * page_height
    container_y = heading_y_end + margin_between_container_and_heading

    scale_width = WIDTH / slab_width
    scale_height = container_h / slab_height

    for rect in rectangles:
        scaled_width = rect['width'] * scale_width
        scaled_height = rect['height'] * scale_height
        scaled_x = X + rect['x'] * scale_width
        scaled_y = container_y + container_h - (rect['y'] * scale_height + scaled_height)

        # Set fill color for rectangle
        c.setFillColor(colors.lightblue)
        c.rect(scaled_x, scaled_y, scaled_width, scaled_height, stroke=1, fill=1)

        # Determine text orientation based on rectangle dimensions
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 5)
        rect_actual_width = round(rect['width'] - cutting_blade_margin_5mm, 2)
        rect_actual_height = round(rect['height'] - cutting_blade_margin_5mm, 2)
        code_text = f"Code: {rect['code']}"
        size_text = f"Size: {rect_actual_width} x {rect_actual_height}"
        # Calculate center positions
        center_x = scaled_x + scaled_width / 2
        center_y = scaled_y + scaled_height / 2

        if rect['width'] < rect['height']:
            # Rotate text for vertical rectangles
            c.saveState()
            c.translate(scaled_x + scaled_width / 2, scaled_y + scaled_height / 2)
            c.rotate(90)
            c.drawCentredString(0, -1, code_text)  # Shift text slightly
            c.drawCentredString(0, 5, size_text)
            c.restoreState()
        else:
            c.drawCentredString(center_x, center_y - 3, code_text)
            c.drawCentredString(center_x, center_y + 3, size_text)

    c.setFillColor(colors.black)
    c.rect(X, container_y, WIDTH, container_h, stroke=1, fill=0)
    return container_y, container_h


def draw_stats_container(c, main_container_y_position, main_container_height, data):
    stats_rect_height = 0.13 * page_height
    stats_y_position = main_container_y_position + main_container_height
    c.rect(X, stats_y_position, WIDTH, stats_rect_height, stroke=1, fill=0)

    stat_text_x = X + 0.5 * cm
    stat_text_y = stats_y_position + 0.6 * cm

    stats_data = [
        ("Layout Number", f"{data['layout_number']} of {data['unique_layouts_count']}"),
        ("Area occupied", f"{data['area_occupied']} sq. ft."),
        ("Area occupied (%)", f"{data['area_occupied_percent']}%"),
        ("Area wasted", f"{data['area_wasted']} sq. ft."),
        ("Area wasted (%)", f"{data['area_wasted_percent']}%"),
        ("Layout Count", f"{data['layout_count']}"),
        ("Total RFT", f"{data['total_rft']}"),
    ]

    c.setFont("Helvetica", 10)
    column_gap = 7 * cm
    for i, (label, value) in enumerate(stats_data):
        c.drawString(stat_text_x, stat_text_y + 14*i, label)
        c.drawString(stat_text_x + column_gap, stat_text_y + 14*i, value)

