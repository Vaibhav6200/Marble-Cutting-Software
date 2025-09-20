import csv
import json
import os
import shutil
import zipfile
from io import StringIO
from pathlib import Path
from django.core.files.base import ContentFile, File
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from bin_packing.models import Panel
from bin_packing.utils import custom_data_input, plot_graph, create_pdf_file


def create_csv_file(inventory_data):
    csv_file = StringIO()
    writer = csv.DictWriter(csv_file, fieldnames=['length', 'width', 'quantity', 'code', 'polish_edge_l', 'polish_edge_w'])
    writer.writeheader()
    for data in inventory_data:
        writer.writerow(data)
    csv_file.seek(0)                # Move cursor to beginning of StringIO object to read its content
    return csv_file


def index(request):
    if request.method == 'POST':
        context = {}
        inventory_input_type = request.POST.get('inventory_input_type')
        slab_length = request.POST.get('slab_length', None)
        slab_width = request.POST.get('slab_width', None)

        if slab_length and slab_width:
            result = None
            panel_obj = None
            if inventory_input_type == 'manual':
                lengths = request.POST.getlist('length[]')
                widths = request.POST.getlist('width[]')
                quantities = request.POST.getlist('quantity[]')
                codes = request.POST.getlist('code[]')
                polish_edge_l = request.POST.getlist('polish_edge_l[]')
                polish_edge_w = request.POST.getlist('polish_edge_w[]')

                inventory_data = [{'length': float(length), 'width': float(width), 'quantity': int(quantity), 'code': code, 'polish_edge_l': int(polish_l), 'polish_edge_w': int(polish_w)}
                                  for length, width, quantity, code, polish_l, polish_w
                                  in zip(lengths, widths, quantities, codes, polish_edge_l, polish_edge_w)]

                # Create CSV file of inventory data
                csv_file = create_csv_file(inventory_data)

                # Save CSV file to Panel model
                panel_obj = Panel()
                panel_obj.csv_file.save('inventory_data.csv', ContentFile(csv_file.getvalue(), 'inventory_store_notebook'), save=True)
                csv_file.close()

                filename = panel_obj.csv_file.name.split('/')[-1]
                result = custom_data_input(algo='maximal_rectangle', heuristic='best_area', filename=filename,
                                           slab_l=float(slab_length), slab_w=float(slab_width))
                panel_obj.json_file = json.dumps(result)
                panel_obj.save()

            elif inventory_input_type == 'csv':
                csv_file = request.FILES.get('csv_file')
                panel_obj = Panel.objects.create(csv_file=csv_file)
                filename = panel_obj.csv_file.url.split('/')[-1]
                result = custom_data_input(algo='maximal_rectangle', heuristic='best_area', filename=filename,
                                           slab_l=float(slab_length), slab_w=float(slab_width))
                panel_obj.json_file = json.dumps(result)
                panel_obj.save()
                
            global_total_area_percentage = result['global_total_area_used'] / (result['slab_total_area'] * result['total_bins_used']) * 100
            global_waste_area_percentage = 100 - global_total_area_percentage
            global_total_area_wasted = result['slab_total_area'] * result['total_bins_used'] - result['global_total_area_used']

            context['result'] = result
            context['global_area_percentage'] = round(global_total_area_percentage, 2)
            context['global_waste_area_percentage'] = round(global_waste_area_percentage, 2)
            context['global_total_area_wasted'] = round(global_total_area_wasted, 2)
            context['unique_layouts_count'] = len(result['plots'])
            context['slab_l'] = slab_length
            context['slab_w'] = slab_width
            context['show_statistics'] = True
            context['panel_obj'] = panel_obj

            create_pdf_file(context, panel_obj)

            return render(request, 'index.html', context)

        return HttpResponse('Invalid Request, Provide Slab Length and Width', status=400)
    return render(request, 'index.html')


def zip_file_handle(request):
    if request.method == 'POST':
        panel_id = request.POST.get('panel_obj_id')
        panel_obj = Panel.objects.filter(id=panel_id)
        if panel_obj.exists():
            csv_obj = panel_obj[0]
            data = json.loads(csv_obj.json_file)
            count = 0
            for slab_data in data['plots']:
                plot_graph(slab_data, count, data['total_bins_used'], panel_id)
                count += 1

            ROOT_DIR = Path(__file__).resolve().parent.parent
            zip_filename = f'{panel_id}.zip'
            folder_path = f'{ROOT_DIR}/media/{panel_id}'
            zip_file_path = f'{ROOT_DIR}/media/{panel_id}.zip'

            # Ensure the directory exists
            os.makedirs(folder_path, exist_ok=True)

            # Create zip_file of our folder
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(folder_path, '..')))

            # Save zip_file in our database
            with open(zip_file_path, 'rb') as f:
                csv_obj.zip_file.save(zip_filename, File(f), save=True)

            # Remove the original folder
            shutil.rmtree(folder_path)
            os.remove(zip_file_path)    # remove temp zip file

            # messages.success(request, 'Download Successful')
            return JsonResponse({'url': csv_obj.zip_file.url}, status=200)
        return HttpResponse('Error: Requested csv file doesn\'t exists', status=400)

