$(function(){
	$(".crear_estudio").click( function(){
		$.ajax({
			url: '/micmac/estudio/crear',
			type: 'get',
			beforeSend: function () {
        		$("#modalEstudio").modal("show");
      		},
      		success: function (data) {
      		}
		})
	})
})