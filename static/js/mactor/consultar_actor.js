/**
 * Created by Win 10 on 2/11/2017.
 */

// Obtiene la descripcion del actor al pulsar el boton VER

    $(document).ready(function () {
        $("a").click(function () {
            var id = $(this).attr("id");
            if(id != undefined)
            {
                $.ajax(
                    {
                        data: {'id': id, 'idEstudio': 0},
                        url: 'consultar_actor',
                        type: 'get',
                        success: function (data)
                        {
                            var object = JSON.parse(data);
                            var html = ""
                            if(object.descripcion != "")
                            {
                                html = "<p>" + 'Nombre Corto:' + "</p><p>" + object.nombreCorto +
                                    "</p><br><p>" + 'Nombre Largo:' + "</p><p>" + object.nombreLargo +
                                    "</p><br><p>" + 'Descripción:' + "</p><p>" + object.descripcion + "</p><p>";
                            }
                            else
                            {
                               html = "<p>" + 'Nombre Corto:' + "</p><p>" + object.nombreCorto +
                                    "</p><br><p>" + 'Nombre Largo:' + "</p><p>" + object.nombreLargo +
                                    "</p><br><p>";
                            }
                            $('#mod_body_actor').html(html);
                        }
                    });
            }
        });
    });

// Obtiene la descripcion de actorY para el formulario de ficha de estrategia

$('#id_idActorY').on('change', DescripcionY);
        function  DescripcionY()
        {
            var id = $(this).val();
            if(id != "")
            {
                $.ajax({
                    data: {'id': id, 'idEstudio': 0},
                    url: 'consultar_actor',
                    type: 'get',
                    success: function (data) {
                        var object = JSON.parse(data);
                        var html = "";
                        if (object.descripcion != "")
                        {
                            html = "<p>" + 'Descripción:' + "</p><p>" + object.descripcion + "</p>";
                        }
                        $('#info').html(html);

                    }
                });
                var actorX = document.getElementById("id_idActorX");

                if(actorX != null)
                {
                    document.getElementById("id_idActorX").disabled = false;
                }
                else
                {
                    document.getElementById("id_idObjetivoX").disabled = false;
                }

            }
        }

// Obtiene la descripcion de actorX para el formulario de ficha de estrategia

$('#id_idActorX').on('change', DescripcionX);
        function  DescripcionX()
        {
            var id = $(this).val();
            $.ajax({
                data : {'id' : id, 'idEstudio': 0},
                url : 'consultar_actor',
                type : 'get',
                success : function (data)
                {
                    var object = JSON.parse(data);
                    var html = "";
                     if(object.descripcion != "")
                    {
                        html = "<p>" + 'Descripción:' + "</p><p>" + object.descripcion + "</p>";
                        $('#info2').html(html);
                    }
                }
            });
        }


