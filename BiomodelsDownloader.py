import requests
import zipfile
import io
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from biomodels_restful_api_client import services as bmservices

class BiomodelsDownloader:
    """
    A class to handle the downloading and extraction of model files from the biomodels database.
    A specified amount of zipfiles are downloaded and then extracted to a common folder.
    This can be done in parallel depending on the number of threads allocated
    """

    def __init__(self, base_url="https://www.ebi.ac.uk/biomodels/search/download", num_models=50, threads=10, output_dir="biomodels", curatedOnly=True):
        """
        Initialize the downloader with the base URL and configuration for downloading.

        base_url (str): The base URL for downloading the models. Default is "https://www.ebi.ac.uk/biomodels/search/download".
        num_models (int): The number of models to download. Default is 50.
        threads (int): The number of threads to use for parallel downloading. Default is 10.
        output_dir (str): The directory where the downloaded models will be stored. Default is "biomodels".
        curatedOnly (bool):Only adds curated models to the database.  

        """
        self.base_url = base_url
        self.num_models = num_models
        self.max_workers = threads
        self.output_dir = output_dir
        self.curatedOnly = curatedOnly

        # Ensure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def download_and_extract(self, model_id):
        """
        Download the zip file for a given model ID and extract the XML file.

        Args:
            model_id (str): The ID of the model to download.

        Returns:
            bool: True if the download and extraction were successful, False otherwise.
        """

        if self.curatedOnly:
            if not self.check_curation_status(model_id):
                print(model_id, ": not curated")
                return False

        url = f"{self.base_url}?models={model_id}"
        response = requests.get(url)
        
        # OK response
        if response.status_code == 200:

            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            for file_info in zip_file.infolist():

                if file_info.filename.endswith('.xml'):
                    xml_content = zip_file.read(file_info.filename)
                    output_path = os.path.join(self.output_dir, file_info.filename)
                    
                    with open(output_path, 'wb') as xml_file:
                        xml_file.write(xml_content)
                    print(f"Extracted {file_info.filename} to {self.output_dir}")

            return True
        
        # Non OK response
        else:
            print(f"Failed to download {model_id}. Status code: {response.status_code}")
            return False


    def run(self): # TODO: could make run automatically as soon as object created
        """
        Start the download and extraction process for all models in parallel.
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

            futures = [executor.submit(self.download_and_extract, f"BIOMD{i:010}") 
                       for i in range(1, self.num_models)]
            
            for future in as_completed(futures):
                future.result()  # Re-raise any exception that was caught during execution
    

    def check_exist_and_up_to_date(self): # TODO: check if biomodel exists and latest version
        pass

    def check_curation_status(self, model_id): # TODO: check if biomodel is curated 
        """
        Queries the restful biomodels api and returns curation status of selected model
        """

        model = bmservices.get_model_info(model_id)
        curationStatus = model['curationStatus']
        return curationStatus
    

# Usage this is an example of how the doanloader should be called

if __name__ == "__main__":

    downloader = BiomodelsDownloader(num_models=50, threads=10, curatedOnly=True)
    downloader.run()
