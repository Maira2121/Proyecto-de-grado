/*permite que al seleccionar una opcion en el primer select, en el segundo solo se muestren activas aquellas que
aun no se han registrado. Esto para los formularios de fichas de estrategias y mid */

$('#id_idActorY').on('change', Desactivar);
        function  Desactivar()
        {
            // se obtiene el id del actor
            var id = $(this).val();
            // se obtiene el id del formulario
            var idEstudio = $('input[name="idEstudio"]').val();
            // se obtiene el id del formulario
            var tipo = $(this).closest("form").attr('id');
            // se envian mediante ajax los parametros
            $.ajax({
                data : {'id' : id, 'estudio': idEstudio, 'tipo': tipo},
                url : 'mid-ajax',
                type : 'get',
                success : function (data)
                {
                    var object = JSON.parse(data);

                    // determina cuales options deben ser activados
                    for(var i=0; i<object.actores.length;i++)
                    {
                        // para el formulario de ficha de estrategias
                        $("#id_idActorX").find("option[value='"+object.actores[i]+"']").prop("disabled",false);

                        // para el formulario de influencias directas
                        if(tipo =="form_mid")
                        {
                            var textAct = $("#id_idActorX").find("option[value='"+object.actores[i]+"']").text();
                            textAct = eliminar_subcadena(textAct);
                            // asigna el valor de influencia registrado
                            $("#id_idActorX").find("option[value='"+object.actores[i]+"']").prop("text",textAct);
                        }
                    }

                    // determina cuales optiones deben ser desactivados
                    for (var j=0;j<object.lista.length; j++)
                    {
                        // se asigna la lista de valores registrados a la variable value
                        var value = object.valores[j];

                        if(tipo=="form_mid")
                        {
                            // se obtiene el texto de la opcion seleccionada en el select
                            var text = $("#id_idActorX").find("option[value='"+object.lista[j]+"']").text();
                            text = eliminar_subcadena(text);
                            // asigna el valor de influencia registrado
                            $("#id_idActorX").find("option[value='"+object.lista[j]+"']").prop("text",text + " (" + value + ")");
                        }
                         // desactiva las opciones correspondientes a las influencias registradas
                        var option = $("#id_idActorX").find("option[value='"+object.lista[j]+"']");
                        option.prop("disabled",true);
                        option.prop("title","Registrado");
                    }
                    // se activa el segundo select
                        document.getElementById("id_idActorX").disabled = false;
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





