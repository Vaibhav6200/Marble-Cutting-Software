document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.querySelector('#panelTable tbody');

    tableBody.addEventListener('click', function(event) {
        if (event.target.classList.contains('addRow')) {
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td><input type="number" name="length[]" class="form-control" min="0" step="any" required></td>
                <td><input type="number" name="width[]" class="form-control" min="0" step="any" required></td>
                <td><input type="number" name="quantity[]" class="form-control" min="0" step="any" required></td>
                <td><input type="text" name="code[]" class="form-control" required></td>
                <td><input type="number" name="polish_edge_l[]" class="form-control" min="0" max="2" step="any" required></td>
                <td><input type="number" name="polish_edge_w[]" class="form-control" min="0" max="2" step="any" required></td>
                <td><button type="button" class="btn btn-danger removeRow">-</button></td>
            `;
            tableBody.appendChild(newRow);
        } else if (event.target.classList.contains('removeRow')) {
            const row = event.target.parentNode.parentNode;
            row.parentNode.removeChild(row);
        }
    });

    // Import CSV file validation
    document.getElementById('csv_file_input').addEventListener('change', function() {
        let fileInput = this;
        // Check if any file is selected and if it is a CSV file
        if (fileInput.files.length > 0) {
            let fileType = fileInput.files[0].type;
            if(fileType === "text/csv" || fileType === "application/vnd.ms-excel"){
                Swal.fire({
                    title: 'Success!',
                    text: 'File Imported Successfully.',
                    icon: 'success'
                }).then((result) => {
                    if (result.isConfirmed) {
                        document.getElementById('csv_upload_form').submit();
                    }
                })
            }
            else{
                Swal.fire({
                    title: 'Error!',
                    text: 'Only CSV Files Supported.',
                    icon: 'error'
                })
            }
        } else {
            Swal.fire({
                title: 'Error!',
                text: 'Please Upload a file first.',
                icon: 'error'
            })
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    let manual_slab_length = document.getElementById('manual_slab_length')
    let manual_slab_width = document.getElementById('manual_slab_width')
    let csv_slab_length = document.getElementById('csv_slab_length')
    let csv_slab_width = document.getElementById('csv_slab_width')

    let slab_length = document.getElementById('slab_length')
    let slab_width = document.getElementById('slab_width')

    slab_length.addEventListener('input', ()=>{
        let slab_length_value = slab_length.value
        manual_slab_length.value = slab_length_value
        csv_slab_length.value = slab_length_value
    })

    slab_width.addEventListener('input', ()=>{
        let slab_width_value = slab_width.value
        manual_slab_width.value = slab_width_value
        csv_slab_width.value = slab_width_value
    })
});
