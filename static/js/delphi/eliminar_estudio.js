// Configuraciones Generales
var tabla = "#estudiosDelphi"; // id
var boton_eliminar = ".delete"; // Clase
var formulario_modal = "#frmEliminar"; //id
var ventana_modal = "#myModal"; // id
// Fin de configuraciones


    $(document). ready(function(){

        $(boton_eliminar).on('click',function(e){
            e.preventDefault();
            console.log('se ejecutó')
            var micmac_id = $(this).data('id');
            var titulo = $(this).data('name');
            $('#modal_idestudio').val(micmac_id);
            $('#modal_titulo').text(titulo);
        });

        var options = {
                success:function(mensaje)
                {

                    if(mensaje.status=="True"){
                        alert("Eliminado!");
                        var id_estudio = mensaje.estudio_id;
                        var elementos= $(tabla+' >tbody >tr').length;
                        if(elementos==1){
                                location.reload();
                        }else{
                            $('#tr'+id_estudio).remove();
                            $(ventana_modal).modal('hide');
                        }

                    }else{
                        alert("Hubo un error al eliminar!");
                        $(ventana_modal).modal('hide');
                    }
                }
            };

        $(formulario_modal).ajaxForm(options);
    });