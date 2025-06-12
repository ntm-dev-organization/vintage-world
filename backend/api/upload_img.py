import base64
import requests

CLIENT_ID = "f0036f53a7821a3"

def upload_imgur(image_path):
    """
    Faz upload da imagem para o Imgur e retorna a URL pública da imagem.
    
    Args:
        image_path (str): caminho do ficheiro da imagem local a enviar.

    Returns:
        str: URL da imagem no Imgur se upload foi bem-sucedido, None caso contrário.
    """
    try:
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode()

        headers = {
            "Authorization": f"Client-ID {CLIENT_ID}"
        }

        data = {
            "image": encoded_image,
            "type": "base64"
        }

        response = requests.post("https://api.imgur.com/3/image", headers=headers, data=data)

        if response.status_code == 200:
            response_json = response.json()
            return response_json['data']['link']
        else:
            print("Erro ao enviar imagem para Imgur:", response.json())
            return None

    except Exception as e:
        print("Exceção ao tentar enviar imagem:", e)
        return None

