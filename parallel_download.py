import requests
import zipfile
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_and_extract(model_id):
    url = f"https://www.ebi.ac.uk/biomodels/search/download?models={model_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))

        for file_info in zip_file.infolist():

            if file_info.filename.endswith('.xml'):
                xml_content = zip_file.read(file_info.filename)
                
                with open(file_info.filename, 'wb') as xml_file:
                    xml_file.write(xml_content)
                print(f"Extracted {file_info.filename} from {model_id}.zip")
    else:
        print(f"Failed to download {model_id}. Status code: {response.status_code}")

def main():
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers based on your system capabilities
        futures = [executor.submit(download_and_extract, f"BIOMD{i:010}") for i in range(1, 101)]
        for future in as_completed(futures):
            future.result()  # If an exception was raised, this will re-raise it

if __name__ == "__main__":
    main()
