$(document).ready(function() {
	var ShowForm = function () {
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType: 'json',
			beforeSend: function () {
				$('#modal-opciones').modal('show');
			},
			success: function (data) {
				$('#modal-opciones .modal-content').html(data.html_form);
			}
		});
	};

	var SaveForm =  function(){
		var form = $(this);
		$.ajax({
			url: form.attr('data-url'),
			data: form.serialize(),
			type: form.attr('method'),
			dataType: 'json',
			success: function(data){
				if(data.form_is_valid){
					$('#tb-opciones tbody').html(data.opcion_list);
					$('#modal-opciones').modal('hide');
				} else {
					$('#modal-opciones .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

// create
$(".show-form").click(ShowForm);
$("#modal-opciones").on("submit",".create-form",SaveForm);

//update
$('#tb-opciones').on("click",".show-form-update",ShowForm);
$('#modal-opciones').on("submit",".update-form",SaveForm)

//delete
$('#tb-opciones').on("click",".show-form-delete",ShowForm);
$('#modal-opciones').on("submit",".delete-form",SaveForm)
});