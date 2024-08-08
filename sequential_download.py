import requests
import zipfile
import io

# Set model ID and the URL
for i in range (1, 10):
    model_id = f"BIOMD{i:010}"  
    url = f"https://www.ebi.ac.uk/biomodels/search/download?models={model_id}"

    # GET request to API for download
    response = requests.get(url)

    # Successful
    if response.status_code == 200:
        
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        
        
        for file_info in zip_file.infolist():

            
            if file_info.filename.endswith('.xml'):
                xml_content = zip_file.read(file_info.filename)
                
                # Save the extracted XML to file
                with open(file_info.filename, 'wb') as xml_file:
                    xml_file.write(xml_content)
                
                print(f"Extracted {file_info.filename} from zip")
    else:
        print(f"Failed to download model. Status code: {response.status_code}")
