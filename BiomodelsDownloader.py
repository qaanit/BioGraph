import requests
import zipfile
import io
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class BiomodelsDownloader: # TODO: some methods uncalled private?
    """
    A class to handle the downloading and extraction of model files from the biomodels database.
    A specified amount of zipfiles are downloaded and then extracted to a common folder.
    This can be done in parallel depending on the number of threads allocated
    """

    def __init__(self, base_url="https://www.ebi.ac.uk/biomodels/search/download", threads=10, output_dir="biomodels", curatedOnly=True):
        """
        Initialize the downloader with the base URL and configuration for downloading.

        base_url (str): The base URL for downloading the models. Default is "https://www.ebi.ac.uk/biomodels/search/download".
        threads (int): The number of threads to use for parallel downloading. Default is 10.
        output_dir (str): The directory where the downloaded models will be stored. Default is "biomodels".
        curatedOnly (bool):Only adds curated models to the database.  

        """
        self.base_url = base_url
        self.max_workers = threads
        self.output_dir = output_dir
        self.curatedOnly = curatedOnly
        self.curated_models = []
        self.uncurated_models = []
        self.missing_damaged_models = [] 

        # TODO: simplify list data storage

        # Ensure output directory exists
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
        
        url = f"{self.base_url}?models={model_id}"
        response = requests.get(url)
        
        # OK response - File downloaded
        if response.status_code == 200:
            
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            
            # Extract xml from downloaded zip file 
            for file_info in zip_file.infolist():
                
                if file_info.filename.endswith('.xml'):
                    xml_content = zip_file.read(file_info.filename)
                    output_path = os.path.join(self.output_dir, file_info.filename)

                    with open(output_path, 'wb') as xml_file:
                        xml_file.write(xml_content)
                    print(f"Extracted {file_info.filename} to {self.output_dir}")

            return True
        
        # Non OK response - Error downloading file
        else:
            print(f"Failed to download {model_id}. Status code: {response.status_code}")
            return False


    def run(self):
        """
        Start the download and extraction process for all models in parallel.
        Based on parameter data - a select number of models will be downloaded
        download_missing_models=False : all missing models will be downloaded
        """
            
        downloadable_models = self.missing_damaged_models

        """
        if self.curatedOnly:
            downloadable_models = self.curated_models
        else:
            downloadable_models = self.curated_models + self.uncurated_models
        """

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

            futures = [executor.submit(self.download_and_extract, model) 
                       for model in downloadable_models]
            
            for future in as_completed(futures):
                future.result()  # Re-raise any Unsuccesful Download that was caught during execution
    

    def verifiy_models(self, MODEL_LIMIT=-1): 
        
        """
        Checks if models listed on biomodels API are downloaded, and up to date 
        if not, will start the download process for lost/damaged models

        returns: list of new/updated models -> to be added/readded to database (manage collsions)
        """
        
        # update current models
        self.check_available_models()
        
        self.missing_damaged_models = []
        path = self.output_dir

        # Check if models exists
        counter = 0
        for model in self.curated_models:   # TODO: Add non-curated - may need to change some logic
            
            counter += 1
            if counter >= MODEL_LIMIT:break

            model_file = f"{path}/{model}.xml"
            if not os.path.isfile(model_file):
                self.missing_damaged_models.append(model)

            else:
                pass
                """ Check that the model is latest version according to biomodels api 
                    This is done by checking file size on machine vs api file size
                    Model will be redownloaded if not latest version
                    Slows down the verify stage a bit
                """
                """  
                metadata_url = f"https://www.ebi.ac.uk/biomodels/model/files/{model}?format=json"
                response = requests.get(metadata_url).json()
                url_file_size = response["main"][0]["fileSize"]
                os_file_size = str(os.path.getsize(model_file))
                
                if url_file_size != os_file_size:
                    self.missing_damaged_models.append(model)
                    print(f"{model} version not up to date")
                """  
        
        if MODEL_LIMIT == -1:
            print(f"[{len(self.missing_damaged_models)}/{len(self.curated_models)}] - models damaged or lost")
        else:
            print(f"[{len(self.missing_damaged_models)}/{MODEL_LIMIT}] - model damaged or lost")
        # redownload missing models in parallel
        self.run()

        # returns new/updated models
        return self.missing_damaged_models

    def check_available_models(self):
        """
        Queries the restful biomodels api and returns a list of all curated and non curated models - removes problematic models 
        """

        url = "https://www.ebi.ac.uk/biomodels/model/identifiers?format=json"
        response = requests.get(url).json()

        # Extract list of avaialble models from json 
        model_names = response["models"]

        # Split models into curated and uncurated using list comprehensions 
        # All curated models are prefixed with BIOMD
        # All non-curated models are prefixed with MODEL
        self.curated_models = [model for model in model_names if model.startswith("BIOMD")]
        self.uncurated_models = [model for model in model_names if model.startswith("MODEL")]

        # SERVER ISSUES WITH FEW PROBLAMATIC MODELS - can be removed if resolved
        # According to docs these models do not contain sbml/xml files 
        curated_problematic_models = ["BIOMD0000001069", "BIOMD0000001075", "BIOMD0000001066", "BIOMD0000001067", "BIOMD0000001068", "BIOMD0000001070", 
                              "BIOMD0000001071", "BIOMD0000001073", "BIOMD0000001074", "BIOMD0000001076"]
        
        for p in curated_problematic_models:
            self.curated_models.remove(p)


# Usage this is an example of how the downloader should be called

if __name__ == "__main__":

    # create downloder
    downloader = BiomodelsDownloader()

    # all models will be searched for and downloaded if missing/damaged - no need to call run 
    # TODO: make unused methods private (run)
    # TODO: non-curated ?? + logic

    downloader.verifiy_models()
    downloader.verifiy_models() # second check