import os
import requests

# default_url = "https://jackblk.github.io/my_cv"
response_tunnel = requests.get("http://localhost:4040/api/tunnels").json()
url_tunnel = response_tunnel["tunnels"][0]["public_url"] + "/docs/"
print(f"\nURL Tunnel is: '{url_tunnel}'.")
url = (
    "https://www.web2pdfconvert.com/convert/web/to/pdf?storefile=true&"
    "filename=LePhucDuc_CV"
    f"&url={url_tunnel}"
    "&Zoom=1&FixedElements=absolute&ViewportWidth=1366&ViewportHeight=800&"
    "PageOrientation=portrait&PageSize=a4&MarginLeft=0&MarginRight=0"
)
print(f"\nConverting to PDF from: '{url}'.")
response = requests.get(url).json()
pdf_link = response["Files"][0]["Url"]
print(f"Downloading converted PDF file: '{pdf_link}'.")
os.system(f"wget {pdf_link} -c")
print("Downloaded PDF file.")
