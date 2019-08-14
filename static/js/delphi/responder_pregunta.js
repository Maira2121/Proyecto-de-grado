$(function () {
            $('.responder').on('click', function (evt) {
                var position = $(this).data('position');
                var $form = $('#form_' + position);
                if (position == 'last') {
                    $.post($form.attr('action'), $form.serialize(),  function (data) {
                        if (data.done) {
                            $('#row_' + position).html('')
                                .append('<div class="alert alert-success">Ha respondido satisfactoriamente esta pregunta</div>');
                            $('#collapse' + next).collapse('show');
                            $('#collapse' + position).collapse('hide');
                            $('#error_' + data.id).html('');
                            if (data.finalizado) {
                                location.reload();
                            }
                        } else {
                            alert('Debe seleccionar una respuesta para la pregunta ' + position)
                        }
                    })
                } else {
                    var next = parseInt(position) + 1;
                    console.log($form.attr('action'));
                    $.post($form.attr('action'), $form.serialize(), function (data) {
                        if (data.done) {
                            $('#row_' + position).html('')
                                .append('<div class="alert alert-success">Ha respondido satisfactoriamente esta pregunta</div>');
                            console.log('hola'+position);
                            if (data.finalizado) {
                                location.reload();
                            }
                            $('#collapse' + next).collapse('show');
                            $('#collapse' + position).collapse('hide');
                            $('#error_' + data.id).html('');
                        } else {
                            alert('Debe seleccionar una respuesta para la pregunta ' + position)
                        }
                    });


                }
            })
        });