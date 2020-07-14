$(document).ready(function () {
    $('#paginatedTable').DataTable({
        "dom": 'lrtip',
        "aaSorting": [],
        "pagingType": "full_numbers",
        "language": {
            "lengthMenu": "Wyświetl _MENU_ rekordów",
            "zeroRecords": "Brak odpowiadających rekordów",
            "search": "Wyszukaj:",
            "info": "_START_ - _END_ z _TOTAL_ rekordów",
            "paginate": {
                "first": "Pierwsza strona",
                "last": "Ostatnia strona",
                "next": "Następna",
                "previous": "Poprzednia"
            }
        }
    });
});
