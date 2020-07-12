function showDetails(param1) {
    var detailClass = param1 + 'details';
    var elems = document.getElementsByClassName(detailClass);
    if (elems[0].style.display === 'none') {
        for (i = 0; i < elems.length; i++) {
            elems[i].style.display = 'table-row';
        }
    } else {
        for (i = 0; i < elems.length; i++) {
            elems[i].style.display = 'none';
        }
    }
}