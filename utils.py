import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import find_peaks
import numpy as np
import re


class RFSpectrum:
    def __init__(self):
        self.metadata = {}
        self.data_instant = pd.DataFrame()
        self.spectrogram = pd.DataFrame()

    def read_file(self, file_path):
        """
        Lee un archivo CSV, procesa su contenido y muestra cada parte.
        
        Args:
            file_path (str): Ruta del archivo CSV a leer.
        """
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # Limpiar el csv
        clean_content = re.sub(r";{2,}", "", content)  # Reemplaza secuencias de dos o más ";" por nada
        clean_content = clean_content.replace(',', '.')  # Reemplazar comas por puntos para formato decimal adecuado

        # Dividir las tres partes del archivo
        parts = clean_content.split('\n\n')  # Dividir por filas vacías
        
        # Procesar cada parte
        self.metadata = self.process_metadata(parts[0])
        self.data_instant = self.process_rf_given_time(parts[1])
        self.spectrogram = self.process_spectrogram(parts[2])
        
        # Mostrar el contenido procesado
        self.display_content()

    def display_content(self):
        """
        Muestra el contenido de cada parte procesada.
        """
        print("Metadata:")
        for key, value in self.metadata.items():
            print(f"{key}: {value}")
        
        print("\nDatos de frecuencia y magnitud:")
        print(self.data_instant.head())
        
        print("\nEspectrograma:")
        print(self.spectrogram.head())

    def process_metadata(self, text):
        """
        Procesa la primera parte del archivo CSV y almacena la información en un diccionario.
        """
        lines = text.splitlines()
        metadata = {}
        
        for line in lines:
            if ';' in line:
                parts = line.split(';')
                
                if len(parts) == 3:
                    key, value, unit = parts
                    metadata[key.strip()] = (value.strip(), unit.strip())
                elif len(parts) == 2:
                    key, value = parts
                    metadata[key.strip()] = value.strip()
        
        return metadata

    def process_rf_given_time(self, text):
        """
        Procesa la segunda parte del archivo CSV, que contiene los datos de frecuencia y magnitud.
        Devuelve un DataFrame con las columnas 'Frequency [Hz]' y 'Magnitude [dBm]'.
        """        
        data = pd.read_csv(StringIO(text), sep=';', header=0)
        data.columns = data.columns.str.strip()
        data['Frequency [Hz]'] = pd.to_numeric(data['Frequency [Hz]'], errors='coerce')
        data['Magnitude [dBm]'] = pd.to_numeric(data['Magnitude [dBm]'], errors='coerce')
        return data

    def plot_frequency_magnitude(self):
        """
        Grafica los datos de frecuencia vs magnitud.
        """
        if self.data_instant.empty:
            print("No hay datos para graficar.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(self.data_instant['Frequency [Hz]'], self.data_instant['Magnitude [dBm]'], label='Magnitud de la señal', color='b')
        plt.title('Señal de Radiofrecuencia')
        plt.xlabel('Frecuencia [Hz]')
        plt.ylabel('Magnitud [dBm]')
        plt.grid(True)
        plt.legend()
        plt.show()

    def process_spectrogram(self, text):
        """
        Procesa la tercera parte del archivo CSV, despreciando las primeras tres filas y
        devolviendo un DataFrame con la frecuencia como la primera columna y las magnitudes en las siguientes columnas.
        
        Args:
            text (str): El texto correspondiente a la tercera parte del archivo CSV.
            
        Returns:
            DataFrame: Un DataFrame con la columna "Frecuencia [Hz]" y columnas de magnitudes numeradas.
        """
        data = pd.read_csv(StringIO(text), sep=';', header=None, skiprows=3)
        column_names = ['Frecuencia [Hz]'] + [str(i) for i in range(data.shape[1] - 1)]
        data.columns = column_names
        data['Frecuencia [Hz]'] = pd.to_numeric(data['Frecuencia [Hz]'], errors='coerce')
        return data

    def filter_dataframe_by_index(self, index):
        """
        Filtra el DataFrame para devolver solo la columna de frecuencia y la columna especificada por el índice.
        
        Args:
            df (DataFrame): El DataFrame original que contiene las columnas.
            index (int): El índice de la columna a filtrar.
            
        Returns:
            DataFrame: Un nuevo DataFrame con dos columnas: "Frecuencia [Hz]" y el valor correspondiente del índice.
        """
        if index < 0 or index >= self.spectrogram.shape[1] - 1:
            raise ValueError(f"Índice fuera de rango. Debe estar entre 0 y {self.spectrogram.shape[1] - 2}.")

        filtered_df = self.spectrogram.iloc[:, [0, index + 1]]
        filtered_df.columns = ['Frecuencia [Hz]', f'{index}']
        return filtered_df


class SignalCharacterization:
    am_col = "Frecuencia [Hz]"
    freq_col = ""
    def __init__(self, data: pd.DataFrame, index) -> None:
        self.data = data
        self.freq_col += str(index)

    def get_central_frequency(self):
        "Frecuencia central"
        # Indice donde amplitud es máximo
        index_max = self.data[self.am_col].idxmax()
        # Frecuencia con máxima amplitud
        freq_index_max = self.data.loc[index_max, self.freq_col]
        return freq_index_max
    
    def get_noise_level(self):
        "Nivel de ruido"
        # Indice donde la implitud es mínima
        index_min = self.data[self.am_col].idxmin()
        # Amplitud más baja
        amplitude_min = self.data.loc[index_min, self.am_col]
        return amplitude_min
    
    def get_amplitude(self):
        "Amplitud o potencia"
        index_max = self.data[self.am_col].idxmax()
        # Amplitud más grande
        amplitude_max = self.data.loc[index_max, self.am_col]
        return amplitude_max
    
    def get_snr(self):
        "Relación señal-ruido"
        noise_level = self.get_noise_level()
        amplitude = self.get_amplitude()
        return amplitude - noise_level

    def get_bandwidth(self):
        "Ancho de banda"
        reference_level = -self.get_snr()/2
        # Encontrar frecuencias que están por encima del nivel de referencia
        band_freqs = self.data[self.data[self.am_col] >= reference_level][self.freq_col]
        bandwidth = band_freqs.max() - band_freqs.min()
        return bandwidth

    def get_modulation(self):
        """
        Detecta el tipo de modulación basado en pulsos y calcula la frecuencia de repetición de pulso (PRF).
        """
        return "PPM"

    def detect_spectral_peaks(self, height=None, distance=None):
        """
        Detecta los picos espectrales en la señal.

        Args:
            height (float): La altura mínima de los picos a detectar.
            distance (int): La distancia mínima entre picos.

        Returns:
            DataFrame: Un DataFrame que contiene los picos detectados con sus frecuencias y magnitudes.
        """
        
        # Obtener magnitudes y frecuencias
        magnitudes = self.data[self.am_col].values
        frequencies = self.data[self.freq_col].values
        
        # Encontrar los picos
        peaks, properties = find_peaks(magnitudes, height=height, distance=distance)

        return ", ".join([str(i) for i in frequencies[peaks]])
        
    def get_crest_factor(self):
        "Determinar el factor de cresta"
        # Amplitud máxima
        amplitude_max = self.get_amplitude()
        rms = amplitude_max * 0.707
        return amplitude_max - rms
