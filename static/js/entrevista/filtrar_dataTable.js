
function filtrarTable() {

  var input, filter, table, tr, td, i;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  table = document.getElementsByClassName('table table-bordered table-hover');
  table = table[0];
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = "";
    if(table.id === "tabla_rondas" || table.id === "tabla_coeficientes")
    {
      td = tr[i].getElementsByTagName("td")[0];
    }
    else
    {
      td = tr[i].getElementsByTagName("td")[1];
    }
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}


