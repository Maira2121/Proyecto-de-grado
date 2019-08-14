$(document).ready(function() {
	var campo=$("#article1");
	var ShowForm = function () {
		var btn = $(this);
		$.ajax({
			url: btn.attr("data-url"),
			type: 'get',
			dataType: 'json',
			beforeSend: function () {
				$('#modal-participantes').modal('show');
			},
			success: function (data) {
				$('#modal-participantes .modal-content').html(data.html_form);

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
					$('#tb-participantes tbody').html(data.opcion_list);
					$('#modal-participantes').modal('hide');

				} else {
					$('#modal-participantes .modal-content').html(data.html_form)
				}
			}
		})
		return false;
	}

// create
$(".show-form").click(ShowForm);
$("#modal-participantes").on("submit",".create-form",SaveForm);

//update
$('#tb-participantes').on("click",".show-form-update",ShowForm);
$('#modal-participantes').on("submit",".update-form",SaveForm)

//delete
$('#tb-participantes').on("click",".show-form-delete",ShowForm);
$('#modal-participantes').on("submit",".delete-form",SaveForm)
});