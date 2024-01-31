import os

# huggingface에서 가중치 파일 다운로드
def check_and_download_model(file, destination_path):
    import shutil
    from huggingface_hub import hf_hub_download
    model_or_dataset_id = 'gogoring/simulation_ws'
    if not os.path.exists(destination_path):    
        hf_hub_download(repo_id=model_or_dataset_id, filename="config.json") 
        model_path = hf_hub_download(repo_id=model_or_dataset_id, filename=file)
        shutil.copy(model_path, destination_path)
    else:
        pass

def get_path(file_name=None):
    p = os.path.dirname(os.path.abspath(__file__)).split("/")
    LIB_PATH = os.path.join("/", *p[1:4], "src", *p[5:6], *p[5:6], "lib", file_name)
    return LIB_PATH