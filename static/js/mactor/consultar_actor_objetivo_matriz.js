
// Obtiene la descripcion del actor u objetivo seleccionado

    $(document).ready(function () {
        $("input").click(function () {
            var id = $(this).attr("id");
            var idEstudio = $('input[name="idEstudio"]').val();
            if(id!=undefined)
            {
                   if (id.indexOf("act")!= -1 || id.indexOf("ver")!= -1 || id.indexOf("mid")!= -1 || id.indexOf("caa")!= -1 || id.indexOf("daa")!= -1)
                    {
                        $.ajax
                        ({
                            data: {'id': id, 'idEstudio': idEstudio},
                            url: 'consultar_actor',
                            type: 'get',
                            success: function (data) {
                                var object = JSON.parse(data);
                                var html = "";
                                if(object.descripcion != "")
                                {
                                   html = "<p>" + 'Nombre Corto:' + "</p><p>" + object.nombreCorto
                                    + "</p><br><p>" + 'Nombre Largo:' + "</p><p>" + object.nombreLargo
                                    + "</p><br><p>" + 'Descripción:' + "</p><p>" + object.descripcion + "</p><p>";
                                }
                                else
                                {
                                  html = "<p>" + 'Nombre Corto:' + "</p><p>" + object.nombreCorto
                                    + "</p><br><p>" + 'Nombre Largo:' + "</p><p>" + object.nombreLargo
                                    + "</p><p>";
                                }
                                $('#mod_body_actor').html(html);
                            }
                        });
                    }
                    // si se pulsa el input de un objetivo
                    else
                        {
                            $.ajax
                            ({
                                data: {'id': id},
                                url: 'consultar_objetivo',
                                type: 'get',
                                success: function (data) {
                                    var object = JSON.parse(data);
                                    var html = "";
                                    if(object.descripcion != "")
                                    {
                                       html = "<p>" + 'Nombre Corto:' + "</p><p>" + object.nombreCorto
                                        + "</p><br><p>" + 'Nombre Largo:' + "</p><p>" + object.nombreLargo
                                        + "</p><br><p>" + 'Descripción:' + "</p><p>" + object.descripcion + "</p><p>";
                                    }
                                    else
                                    {
                                      html = "<p>" + 'Nombre Corto:' + "</p><p>" + object.nombreCorto
                                        + "</p><br><p>" + 'Nombre Largo:' + "</p><p>" + object.nombreLargo
                                        + "</p><p>";
                                    }
                                    $('#mod_body_objetivo').html(html);
                                    }
                                });

                        }
            }

        });
    });


