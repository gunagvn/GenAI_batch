import requests

# Paste the access token you got from OAuth Playground
ACCESS_TOKEN = "ya29.a0ATi6K2vnsq9CMPEKxPZQJILByu7jAkRE7IfyjVU2oQDA1G_ToqZoTdK6llIUjD81BM_AKGpmWoUpLjQvisce6_U8gOzfh1p_Z3dJb6k3BtRyWJxznCIxZHWIeCUFxFAuuN06aD2Q0aaseFKgElaC5eJHm6MHnPSnSyBbLx-BjzIGbGYiIx_Qvi0GD00Sf_dZ2S4jnC8aCgYKAS0SARESFQHGX2MifNpuYTQrkeEyypR9JXj8EA0206"

url = "https://www.googleapis.com/drive/v3/files"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

params = {
    "pageSize": 20,          # Number of files to list
    "fields": "files(id, name, mimeType)"  # Info you want
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    print("Files in your Google Drive:")
    for f in response.json().get("files", []):
        print(f"{f['name']} ({f['id']}) - {f['mimeType']}")
else:
    print("Error:", response.text)