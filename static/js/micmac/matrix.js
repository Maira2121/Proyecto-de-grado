            var lista_relacion = $('tbody').data('relacion')
            console.log(lista_relacion);
            var tupla = []
            var row_length = document.getElementById("example-table").rows.length - 1

            function ListarRelacion(listado_relacion){
                var lista = [], i=0, elemento1
	            for (i=0;i<lista_relacion.length;++i){
	                if( !(lista_relacion[i] == "[") && !(lista_relacion[i] == "]") && !(lista_relacion[i] == "(") && !(lista_relacion[i] == ")") && !(lista_relacion[i] == ",") && !(lista_relacion[i] == " ")){
	                    elemento1=lista_relacion[i]
	                    j = i+1
	                    if( !(lista_relacion[j] == "[") && !(lista_relacion[j] == "]") && !(lista_relacion[j] == "(") && !(lista_relacion[j] == ")") && !(lista_relacion[j] == ",") && !(lista_relacion[j] == " ")){
	                       lista.push(elemento1.concat(lista_relacion[j]))
	                       i=j
	                    }else{
	                       lista.push(elemento1)
	                    }
	                }
	             }
                return lista
            }


            function TuplaRelacion(lista_relacion){
                var tuplaRel = [], i = 0, cont = 0
                   for (i=0;i<(lista_relacion.length/3);++i){
                        tuplaRel[i] = []
                        for(j=0;j<3;++j){
                            tuplaRel[i].push(lista_relacion[cont])
                            ++cont;
                        }
                   }
                return tuplaRel
            }
            function relacionValorecion(lista){
                list_valRel = []
                for (i=2;i<lista.length;i=i+3){
                        list_valRel.push(lista[i])
                }
                return list_valRel
            }

            var listRel = ListarRelacion(lista_relacion)
            var tupRel = TuplaRelacion(listRel)
            console.log(tupRel)

            $('td').each(function(){
                var celda = 0;
                for (i=0;i<tupRel.length;++i){
                    if(($(this).data('row')==tupRel[i][0]) && ($(this).data('col')==tupRel[i][1])){
                       $(this).text(tupRel[i][2])
                    }
                 }
                 if($(this).data('row')==$(this).data('col')){
                    $(this).text('0')
                 }
            });