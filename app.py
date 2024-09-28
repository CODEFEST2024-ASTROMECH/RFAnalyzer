import os
import tempfile
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, send_file
from utils import RFSpectrum, SignalCharacterization
import io

app = Flask(__name__)

# Inicialización de RFSpectrum
rfspectrum = RFSpectrum()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spectrogram')
def plot_spectrogram():
    # Convertir a numpy para la visualización
    frequencies = rfspectrum.spectrogram.iloc[:, 0].values
    amplitudes = rfspectrum.spectrogram.iloc[:, 1:].values

    plt.figure(figsize=(10, 6))
    plt.imshow(amplitudes, aspect='auto', extent=[frequencies.min(), frequencies.max(), 0, amplitudes.shape[0]], origin='lower')
    plt.colorbar(label='Amplitud')
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('Instantes de tiempo')
    plt.title('Espectrograma')
    
    # Guardar la figura en un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    plt.close()  # Cerrar la figura

    print("Espectrograma generado con éxito")  # Debugging
    return send_file(buf, mimetype='image/png')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    
    # Guardar el archivo en un directorio temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
        file.save(temp_file.name)
        rfspectrum.read_file(temp_file.name)  # Pasar la ruta temporal al método
        n = rfspectrum.spectrogram.shape[1] - 1  # Número de columnas - 1

    return jsonify({'n': n})

@app.route('/update_table', methods=['POST'])
def update_table():
    index = int(request.json['index'])
    
    # Filtrar el DataFrame por el índice del slider
    filtered_df = rfspectrum.filter_dataframe_by_index(index)

    # Inicializar SignalCharacterization con el DataFrame filtrado
    signal_characterization = SignalCharacterization(filtered_df, index)
    
    # Obtener valores de SignalCharacterization
    values = {
        "central_frequency": signal_characterization.get_central_frequency(),
        "bandwidth": signal_characterization.get_bandwidth(),
        "noise_level": signal_characterization.get_noise_level(),
        "modulation": signal_characterization.get_modulation(),
        "amplitude": signal_characterization.get_amplitude(),
        "spectral_peaks": signal_characterization.detect_spectral_peaks(),
        "snr": signal_characterization.get_snr(),
        "crest_factor": signal_characterization.get_crest_factor()
    }
    
    # Devolver los valores en formato JSON
    return jsonify(values)


if __name__ == '__main__':
    app.run(debug=True)
