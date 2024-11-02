function downloadSwimmersExcel() {
    // Get table data
    var table = document.getElementById('swimmersTable');
    var rows = table.querySelectorAll('tr');
    var data = [];

    // Loop through rows and cells to extract data
    rows.forEach(function(row) {
        var rowData = [];
        var cells = row.querySelectorAll('th, td');
        cells.forEach(function(cell) {
            rowData.push(cell.innerText);
        });
        data.push(rowData);
    });

    // Create a new workbook and add the data
    var wb = XLSX.utils.book_new();
    var ws = XLSX.utils.aoa_to_sheet(data);
    XLSX.utils.book_append_sheet(wb, ws, 'Swimmers');

    // Generate Excel file and trigger download
    XLSX.writeFile(wb, 'swimmers.xlsx');
}