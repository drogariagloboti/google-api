import google_con as api
from googleapiclient.http import MediaFileUpload
from flask import Flask,request, jsonify
from flask_cors import CORS
import os
import tempfile
import re

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


def remover_caracteres_especiais(texto):
    padrao = re.compile(r'[^a-zA-Z0-9\s]')
    texto_sem_especiais = re.sub(padrao, '', texto)
    
    return texto_sem_especiais



@app.route('/modulos', methods=['GET'])
def get_modules():
    service = api.service()
    files = service.files().list(q="parents='15o4bQnoM3bb-JSQtJxC_AxTA-O8kL-Jh'").execute()
    modulos = []
    for i in files['files']:
        if i["mimeType"] == "application/vnd.google-apps.folder":
             modulos.append({'id':i['id'],'title':i['name']})
    return jsonify(modulos)


@app.route('/videos', methods=['POST'])
def videos():
    service = api.service()
    files = service.files().list(q=f"parents='{request.json['id']}'").execute()
    mp4 = []
    for i in files['files']:
        if i['mimeType'] == 'video/mp4':
            service.permissions().create(
            fileId = i['id'],
            body={'role': 'reader', 'type': 'anyone'}
            ).execute()
            shared = service.files().get(fileId=i['id'],fields='webViewLink').execute()
            mp4.append({'id':i['id'], 'url': shared['webViewLink'].replace('https://drive.google.com/file/d/',''), 'title': i['name'].replace(' ','_')})
    return jsonify({'path': 'https://drive.google.com/file/d/','lessons':mp4})


@app.route('/novo_modulo', methods=['POST'])
def create_module():
    service = api.service()
    file_metadata = {
        'name': remover_caracteres_especiais(request.json['nome']),
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': ['15o4bQnoM3bb-JSQtJxC_AxTA-O8kL-Jh']
    }
    service.files().create(body=file_metadata).execute()
    return jsonify({'boleano': True, 'mensagem': "Modulo criado com sucesso!"})


@app.route('/upload_video', methods=['POST'])
def upload_video():
    try:
        service = api.service()
        file_metadata = {
        'name': remover_caracteres_especiais(request.form['nome']),
        'parents':[f"{request.form['id']}"]
        }
        video = request.files['arquivo']

        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, video.filename)
        video.save(temp_path)

        media = MediaFileUpload(filename=temp_path,mimetype='video/mp4', resumable=True)
        envio =service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        )
        response = None
        while response is None:
            # Status de upload
            status, response = envio.next_chunk()
            if status:
                print(f"Upload {int(status.progress() * 100)}% completo.")

        print(f"Upload concluído. ID do arquivo: {response['id']}")
        video.close()
        return jsonify({'mensagem':'Upload concluído com sucesso!'})
    except Exception as e:
        return jsonify({'mensagem':f"Erro durante o upload: {str(e)}"})


@app.route('/update', methods=['POST'])
def update():
    service = api.service()
    body = {'name': remover_caracteres_especiais(request.json['nome'])}
    service.files().update(fileId=request.json['id'],body=body).execute()
    return jsonify({'boleano': True, 'mensagem': 'Nome alterado com sucesso!'})


@app.route('/delete', methods=['POST'])
def delete():
    service = api.service()
    service.files().delete(fileId=request.json['id']).execute()
    return jsonify({'boleano': True, 'mensagem': 'deletado com sucesso!'})

@app.route('/geral', methods=['GET'])
def geral():
    service = api.service()
    files = service.files().list(q=f"parents='15o4bQnoM3bb-JSQtJxC_AxTA-O8kL-Jh'").execute()
    retorno = []
    for i in files['files']:
        if i["mimeType"] == "application/vnd.google-apps.folder":
                mp4 = []
                modulo = service.files().list(q=f"parents='{i['id']}'").execute()
                for y in modulo['files']:
                    if y['mimeType'] == 'video/mp4':
                        resp = service.permissions().create(
                        fileId = y['id'],
                        body={'role': 'reader', 'type': 'anyone'}
                        ).execute()
                        shared = service.files().get(fileId=y['id'],fields='webViewLink').execute()
                        mp4.append({'id':y['id'], 'url': shared['webViewLink'].replace('https://drive.google.com/file/d/','').replace('?usp=drivesdk',''), 'title': y['name'].replace(' ','_')})
                retorno.append({'id':i['id'],'title':i['name'],'path': 'https://drive.google.com/file/d/','lessons':mp4})
    return jsonify({"payload":{"modules":retorno}})


if __name__ == '__main__':
    import multiprocessing
    num_cores = multiprocessing.cpu_count()
    print(f"Servidor executando com {num_cores} cores")
    app.run(debug=True, host='0.0.0.0', port=5000)
