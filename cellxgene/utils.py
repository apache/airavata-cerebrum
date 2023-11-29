import requests
import urllib.request
import shutil
import pathlib
import time


def get_collection_metadata(collection_id):
    """Retrieve collection meta data in JSON format."""
    domain_name = "cellxgene.cziscience.com"
    api_url_base = f"https://api.{domain_name}"
    collection_path = f"/curation/v1/collections/{collection_id}"
    collection_url = f"{api_url_base}{collection_path}"
    res = requests.get(url=collection_url)
    res.raise_for_status()
    res_content = res.json()
    return res_content


def get_h5ad_url(dataset_mdata):
    """
    Retrieve the URL to the h5ad file from the dataset meta data,
    which is available in the asssets entry of the dataset
      {
        assets:{
            'filetype': 'H5AD',
            'url' : 'https://...URL Link..'
        }
      }
    """
    for ax in dataset_mdata['assets']:
        if ax['filetype'] == 'H5AD':
            return ax['url']


def get_dataset_links(collection_mdata):
    """
    Retrieve the URLs to the h5ad file from the collection meta data,
    which is available in the asssets entry of each of the dataset
      {
        assets:{
            'filetype': 'H5AD',
            'url' : 'https://...URL Link..'
        }
      }
    Return a list of pairs (dataset tilt, h5ad url)
    """
    dstx = [(dx['title'],
             get_h5ad_url(dx)) for dx in collection_mdata['datasets']]
    return dstx


def download_file(url, dest_file):
    """
    Download the File, using requests library.
    """
    with requests.get(url, stream=True) as r:
        with open(dest_file, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return dest_file


def download_file_urlr(url, dest_file):
    """
    Download the File, using urllib/retrieve library.
    """
    return urllib.request.urlretrieve(url, dest_file)


def download_datasets(dataset_links, out_dir):
    """
    Given a list of (title, url), downloads the datasets to the
    out_dir directory with the name derived form the title.
    """
    for title, url in dataset_links:
        dest_file = pathlib.Path(out_dir,
                                 title.replace(' ', '_') + '.h5ad')
        download_file(url, dest_file)
        print(f"Downloaded data for {title}")
        time.sleep(0.1)


def download_collection(collection_id, out_dir):
    """
    For a given collection id in CELLxGENE, download all the
    gene expression datasets to the out_dir.
    """
    collection_mdata = get_collection_metadata(collection_id)
    dataset_links = get_dataset_links(collection_mdata)
    download_datasets(dataset_links, out_dir)
