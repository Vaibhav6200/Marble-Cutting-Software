import matplotlib.pyplot as plt
import matplotlib.patches as patches
import algorithms as g
import csv
import os
from pathlib import Path
from algorithms.item import CustomItem
from bin_packing.plot_pdf import draw_heading_container, draw_stats_container, draw_main_container
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from django.conf import settings

SLAB_LENGTH = 138
SLAB_WIDTH = 78
cutting_blade_margin_5mm = 5 / 25.4     # considering 1 point == 1 inch


def plot_graph(slab_data, num, total_bins_used, csv_file_id):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, SLAB_LENGTH)
    ax.set_ylim(0, SLAB_WIDTH)
    ax.set_title(f'Layout: {num+1}/{total_bins_used}')
    ax.set_xlabel("Width")
    ax.set_ylabel("Length")
    ax.set_aspect('equal', adjustable='box')

    ax.autoscale(enable=False)

    ax.set_xticks([i for i in range(0, SLAB_LENGTH+1, 20)] + [SLAB_LENGTH])
    ax.set_yticks([i for i in range(0, SLAB_WIDTH+1, 10)] + [SLAB_WIDTH])

    margin = 1

    # Plot each rectangle
    for rect in slab_data['rectangles']:
        patch = patches.Rectangle((rect['x'], rect['y']), rect['width'], rect['height'], linewidth=1, edgecolor='b', facecolor='blue', alpha=0.5)
        ax.add_patch(patch)

        # Annotate width inside the rectangle with margin
        ax.text(rect['x'] + rect['width']/2, rect['y'] + margin, f"{rect['width']}",
                verticalalignment='bottom', horizontalalignment='center',
                fontsize=8, color='black', weight='bold')

        # Annotate height inside the rectangle with margin
        ax.text(rect['x'] + margin, rect['y'] + rect['height']/2, f"{rect['height']}",
                verticalalignment='center', horizontalalignment='left',
                fontsize=8, color='black', weight='bold', rotation=90)

    # Display additional statistics
    stats_text = f"Total bins used: {total_bins_used}\nArea occupied: {slab_data['slab_percentage_occupied']}%\nArea wasted: {slab_data['slab_percentage_wasted']}%\nLayout Count: {slab_data['layout_count']}"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    fig.text(0.5, 0.07, stats_text, ha='center', va='bottom', fontsize=10, bbox=props)
    fig.subplots_adjust(bottom=0.2)  # Increase the bottom margin

    # Check if the directory exists, create if not and save the image
    ROOT_DIR = Path(__file__).resolve().parent.parent
    directory_path = f'{ROOT_DIR}/media/{csv_file_id}/'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    image_name = f"image_{num+1}.png"
    plt.savefig(directory_path + image_name)
    plt.close(fig)


def create_pdf_file(context, panel_instance):
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdf', str(panel_instance.id))
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)  # Ensure the directory exists

    # c = canvas.Canvas(f"/home/vaibhav/test.pdf", pagesize=A4, bottomup=0)
    c = canvas.Canvas(pdf_path, pagesize=A4, bottomup=0)
    result = context['result']
    margin = 1 * cm  # Set a margin for aesthetics
    current_y = margin  # Start from the bottom of the page plus a margin
    plots_per_page = 0

    heading_data = {
        'total_area_used': round(result['global_total_area_used'] / 144, 2),      # divide by 144 to get area in sq. ft.
        'total_area_wasted': round(context['global_total_area_wasted'] / 144, 2), # divide by 144 to get area in sq. ft.
        'total_area_used_percent': context['global_area_percentage'],
        'total_area_wasted_percent': context['global_waste_area_percentage'],
        'total_no_of_slabs_used': result['total_bins_used'],
        'total_area_of_single_slab': round(result['slab_total_area'] / 144, 2),   # divide by 144 to get area in sq. ft.
        'slab_width': context['slab_w'],
        'slab_length': context['slab_l']
    }

    for idx, plot in enumerate(result['plots']):
        rectangles = plot['rectangles']

        total_rft = 0.0
        for rect in rectangles:
            rect_actual_width = rect['width'] - cutting_blade_margin_5mm
            rect_actual_height = rect['height'] - cutting_blade_margin_5mm
            total_rft += (rect['polish_edge_l'] * rect_actual_height) + (rect['polish_edge_w'] * rect_actual_width)
        stats_data = {
            'layout_number': idx + 1,
            'unique_layouts_count': context['unique_layouts_count'],
            'area_occupied': round(plot['slab_used_area'] / 144, 2),      # divide by 144 to get area in sq. ft.
            'area_wasted': round(plot['slab_wasted_area'] / 144, 2),      # divide by 144 to get area in sq. ft.
            'layout_count': plot['layout_count'],
            'area_occupied_percent': plot['slab_percentage_occupied'],
            'area_wasted_percent': plot['slab_percentage_wasted'],
            'total_rft': round(total_rft, 2),
        }
        page_width, page_height = A4
        needed_height = 0.3 * page_height + 0.115 * page_height  # main + stats containers height
        if current_y + needed_height > page_height - margin or plots_per_page == 2:
            c.showPage()
            current_y = margin
            plots_per_page = 0

        if idx == 0:
            heading_y_end_position = draw_heading_container(c, heading_data)
            current_y += heading_y_end_position  # Adjust current_y to account for the height of the heading

        # container_y, container_h = draw_main_container(c, current_y, rectangles, float(context['slab_w']), float(context['slab_l']))
        container_y, container_h = draw_main_container(c, current_y, rectangles)
        draw_stats_container(c, container_y, container_h, stats_data)

        # Update the current_y position and plots count
        current_y += container_h + 0.115 * page_height + margin
        plots_per_page += 1

    c.save()

    # Save the file path in the database
    panel_instance.pdf_file.name = os.path.join('pdf', str(panel_instance.id))
    panel_instance.save()


def custom_data_input(algo, heuristic, filename=None, slab_l=138, slab_w=78):
    SLAB_LENGTH = slab_l
    SLAB_WIDTH = slab_w
    M = g.BinManager(SLAB_LENGTH, SLAB_WIDTH, pack_algo=algo, heuristic=heuristic, rotation=True, sorting=True, wastemap=True)
    demoList = []

    if filename:
        ROOT_DIR = Path(__file__).resolve().parent.parent
        file_path = f'{ROOT_DIR}/media/csv/{filename}'
        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for item in csv_reader:
                height = float(item['length']) + cutting_blade_margin_5mm
                width = float(item['width']) + cutting_blade_margin_5mm
                quantity = int(item['quantity'])
                code = item['code']
                polish_edge_l = int(item['polish_edge_l'])
                polish_edge_w = int(item['polish_edge_w'])

                for _ in range(int(quantity)):
                    # demoList.append(g.Item(height, width))
                    demoList.append(CustomItem(height, width, code, polish_edge_l, polish_edge_w))
    else:
        raise ValueError("Please provide a valid filename.")

    M.add_items(*demoList)
    M.execute()

    slab_configurations = {}
    for bin in M.bins:
        rectangles = [(rectangle.width, rectangle.height, rectangle.x, rectangle.y, rectangle.code,
                       rectangle.polish_edge_l, rectangle.polish_edge_w) for rectangle in bin.items]
        # Sort rectangles by position and size for consistent comparison
        rectangles.sort()
        # Convert to a tuple for immutability and use as a dictionary key
        key = tuple(rectangles)
        if key in slab_configurations:
            slab_configurations[key] += 1
        else:
            slab_configurations[key] = 1

    # Prepare data to return, incorporating counts of each unique slab configuration
    plots = []
    global_total_area_used = 0
    slab_total_area = SLAB_LENGTH * SLAB_WIDTH

    for config, count in slab_configurations.items():
        slab_details = {}
        plotList = [{"width": rect[0], "height": rect[1], "x": rect[2], "y": rect[3], "code": rect[4], "polish_edge_l": rect[5], "polish_edge_w": rect[6]} for rect in config]
        area_occupied = sum(rect[0] * rect[1] for rect in config)
        global_total_area_used += area_occupied * count
        percentage_occupied = round((area_occupied / slab_total_area) * 100, 3)

        slab_details["slab_percentage_occupied"] = percentage_occupied
        slab_details["slab_percentage_wasted"] = round(100 - percentage_occupied, 3)
        slab_details["rectangles"] = plotList
        slab_details["layout_count"] = count
        slab_details["slab_used_area"] = round(area_occupied, 2)
        slab_details["slab_wasted_area"] = round(slab_total_area - area_occupied, 2)
        plots.append(slab_details)

    return {
        "plots": plots,
        "total_bins_used": len(M.bins),
        "slab_total_area": slab_total_area,
        "global_total_area_used": global_total_area_used
    }

