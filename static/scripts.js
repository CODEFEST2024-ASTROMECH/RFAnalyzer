$(document).ready(function () {
    $('#openCsvBtn').on('click', function () {
        $('#csvInput').click();
    });

    $('#csvInput').on('change', function (event) {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            // Actualizar el nombre del archivo en el título
            $('#fileName').text(file.name);

            // Enviar el archivo al servidor
            $.ajax({
                url: '/upload',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function (data) {
                    // Actualizar el valor máximo del slider y resetearlo a 0
                    const n = data.n;
                    $('#slider').attr('max', n - 1); // N-1
                    $('#slider').val(0); // Resetear a 0
                    $('#sliderValue').text(0); // Actualizar tooltip

                    // Actualizar la imagen del espectrograma
                    $('#spectrogram').attr('src', '/spectrogram?' + new Date().getTime());
                },
                error: function (error) {
                    console.error('Error:', error);
                }
            });
        }
    });

    const slider = $('#slider');
    const sliderValue = $('#sliderValue');
    const tableCells = $('table tbody td');  // Selecciona las celdas de la tabla

    // Escucha los cambios del slider
    slider.on('input', function () {
        const index = $(this).val();
        sliderValue.text(index);

        // Llamar al backend para obtener los valores actualizados
        $.ajax({
            url: '/update_table',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ index: index }),
            success: function (data) {
                console.log(data);  // Verificar los datos recibidos en la consola del navegador

                // Actualizar las celdas de la tabla con los nuevos valores
                tableCells.eq(1).text(data.central_frequency);  // Primera fila, segunda celda
                tableCells.eq(3).text(data.bandwidth);          // Primera fila, cuarta celda
                tableCells.eq(5).text(data.noise_level);        // Segunda fila, segunda celda
                tableCells.eq(7).text(data.modulation);         // Segunda fila, cuarta celda
                tableCells.eq(9).text(data.amplitude);          // Tercera fila, segunda celda
                tableCells.eq(11).text(data.spectral_peaks);    // Tercera fila, cuarta celda
                tableCells.eq(13).text(data.snr);               // Cuarta fila, segunda celda
                tableCells.eq(15).text(data.crest_factor);      // Cuarta fila, cuarta celda
            }
        });
    });

    $('#generateReportBtn').on('click', function () {
        window.print(); // Abrir el diálogo de impresión
    });
});
