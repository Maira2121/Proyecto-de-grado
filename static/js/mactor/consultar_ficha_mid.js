
// Obtiene el registro de la ficha de estrategias de los actores seleccionados

function  Consultar_ficha()
        {
            var id = $(id_idActorX).val();
            var id2 = $(id_idActorY).val();
            var idEstudio = $('input[name="idEstudio"]').val();
            $.ajax({
                data : {'id' : id, 'id2' : id2, 'idEstudio': idEstudio},
                url : 'consultar_ficha_mid',
                type : 'get',
                success : function (data)
                {
                    var object = JSON.parse(data);
                    var html = "<p>" + object.estrategia + "</p>";
                    $('#mod_body').html(html);
                }
            });
        }

