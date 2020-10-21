import aiohttp
import asyncio
import uvicorn
import numpy #
from io import BytesIO
from pathlib import Path
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from fast_bert.data_cls import BertDataBunch
from fast_bert.learner_cls import *
from fast_bert.prediction import *
import torch
import sys

export_file_url = "https://www.googleapis.com/drive/v3/files/1KjrRxptv78tXKGYCE-B6EsRJ2e8YkUDm?alt=media&key=AIzaSyCNoRufM9Z-HSsX566HZv-Qj2shWUI7BBs"
export_file_name = 'pytorch_model.bin'

path = Path('/root/Capstone2/app')

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='/root/Capstone2/app/static'))


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):

    data_bunch = await BertDataBunch(path, path,
                                     tokenizer = path,
                                     train_file = None,
                                     val_file = None,
                                     label_file = 'l2.csv',
                                     batch_size_per_gpu = 120,
                                     max_seq_length = 40,
                                     multi_gpu = False,
                                     multi_label = False,
                                     model_type = None)

    model = await load_model(data_bunch, path, path / export_file_name, device = "cpu", multi_label = False)
    learner = await BertLearner(data_bunch, model, path, metrics = [], output_dir = None, device = 'cpu', logger = None)

    text = request.form.get('text')
    preds = learner.predict_batch([text])
    return JSONResponse({'result': str(preds), 'probability': str(probability)})


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
