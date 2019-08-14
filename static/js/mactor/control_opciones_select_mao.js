// Mediante este archivo al seleccionar una opcion del primer select (Y), se muestran en el segundo activas solo
// aquellas opciones que aun no se han registrado.

$('#id_idActorY').on('change', DescripcionY);
        function  DescripcionY()
        {   // se obtiene el id del actor
            var id = $(this).val();
            var idEstudio = $('input[name="idEstudio"]').val();
            // se obtiene el id del formulario
            var tipo = $(this).closest("form").attr('id');

            $.ajax({
                data : {'id' : id,
                        'estudio': idEstudio,
                        'tipo': tipo},
                url : 'mao-ajax',
                type : 'get',
                success : function (data)
                {
                    var object = JSON.parse(data);
                    // permite que al cambiar la opcion se activen las opciones correspondientes (actualizar opciones)
                    for(var i=0; i<object.objetivos.length;i++)
                    {
                        $("#id_idObjetivoX").find("option[value='"+object.objetivos[i]+"']").prop("disabled",false);
                        var textAct = $("#id_idObjetivoX").find("option[value='"+object.objetivos[i]+"']").text();
                        textAct = eliminar_subcadena(textAct);
                        // asigna el valor de influencia registrado
                        $("#id_idObjetivoX").find("option[value='"+object.objetivos[i]+"']").prop("text",textAct);
                    }
                    // al activar todas las opciones se establecen cuales deben desactivarse para la opcion actual
                    for (var j=0;j<object.lista.length; j++)
                    {
                            // se asigna la lista de valores registrados a la variable value
                            var value = object.valores[j];
                            // se obtiene el texto de la opcion seleccionada en el select
                            var text = $("#id_idObjetivoX").find("option[value='"+object.lista[j]+"']").text();
                            text = eliminar_subcadena(text);
                            // asigna el valor de influencia registrado
                            $("#id_idObjetivoX").find("option[value='"+object.lista[j]+"']").prop("text",text + " (" + value + ")");

                        $("#id_idObjetivoX").find("option[value='"+object.lista[j]+"']").prop("disabled",true);
                    }
                    // se activa el segundo select
                        document.getElementById("id_idObjetivoX").disabled = false;
                }
            });
        }

function eliminar_subcadena(cadena){

                        // se actualizan los valores de las influencias registradas
                        for(var y=0;y<cadena.length; y++)
                        {
                            var caracter = cadena.charAt(y);

                            if(caracter == "(")
                            {
                                cadena = cadena.substring(0, y);
                            }
                        }

                        return cadena;
        }




