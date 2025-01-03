import os
import pydicom
import numpy as np
from pathlib import Path
from pydicom.pixel_data_handlers.util import apply_voi_lut
from PIL import Image


# DICOM Dosyasını Okuma Fonksiyonu
def read_xray(path, voi_lut=True, fix_monochrome=True):
    dicom = pydicom.dcmread(path)

    # VOI LUT (DICOM cihazından sağlanan) veriyi "insan dostu" şekilde dönüştürür
    if voi_lut:
        data = apply_voi_lut(dicom.pixel_array, dicom)
    else:
        data = dicom.pixel_array

    # X-ray görüntüsünün ters dönüp dönmediğine göre düzeltme yapıyoruz
    if fix_monochrome and dicom.PhotometricInterpretation == "MONOCHROME1":
        data = np.amax(data) - data

    # Görüntüyü normalize etme (0-255 arası)
    data = data - np.min(data)
    data = data / np.max(data)
    data = (data * 255).astype(np.uint8)

    return data


# PNG olarak kaydetme fonksiyonu
def save_as_png(img_data, output_path):
    img = Image.fromarray(img_data)
    img.save(output_path)


# Klasördeki tüm DICOM dosyalarını işleme
def process_directory(directory_path, output_directory):
    dicom_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".dcm"):
                full_path = Path(root) / file
                dicom_files.append(full_path)


    # Çıktı klasörünü oluştur
    os.makedirs(output_directory, exist_ok=True)

    # Her DICOM dosyasını işleme
    processed_count = 0
    for dicom_path in dicom_files:
        try:
            # DICOM dosyasını oku
            img_data = read_xray(dicom_path)

            # PNG formatında kaydet
            processed_count += 1
            output_path = os.path.join(output_directory, dicom_path.stem + f'{processed_count}.png')
            save_as_png(img_data, output_path)


            print(f"Processed {processed_count}/{len(dicom_files)}: {dicom_path.name}")

        except Exception as e:
            print(f"Error processing {dicom_path.name}: {e}")

    print(f"\nProcessing completed. {processed_count} files were successfully processed.")


if __name__ == "__main__":

    output_folder_path = r"C:\Users\Agah\Desktop\BI-RADS_5"
    yol = r"C:\Users\Agah\Desktop\Kategori5"

    process_directory(yol, output_folder_path)

