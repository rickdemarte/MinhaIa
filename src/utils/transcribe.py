
import os
import sys
import json
import time
from pathlib import Path
import boto3
import requests
from botocore.exceptions import ClientError

def transcribe_audio_aws(audio_file_path, language_code="pt-BR", media_format="mp3", bucket_name=None):
    """
    Transcreve um arquivo de áudio usando AWS Transcribe e salva o resultado JSON no S3
    Retorna a URI do objeto JSON gerado no bucket
    """
    
    # Clientes AWS
    s3_client = boto3.client('s3')
    transcribe_client = boto3.client('transcribe')
    
    if not bucket_name:
        print("Nenhum bucket especificado.", file=sys.stderr)
        exit(1)
    
    # Nome do arquivo no S3 com timestamp
    file_name = os.path.basename(audio_file_path)
    s3_audio_key = f"audio/{int(time.time())}-{file_name}"
    json_key = None
    
    try:
        # Upload do arquivo para S3
        print(f"Enviando arquivo para S3: s3://{bucket_name}/{s3_audio_key}")
        s3_client.upload_file(audio_file_path, bucket_name, s3_audio_key)
        job_uri = f"s3://{bucket_name}/{s3_audio_key}"
        
        # Nome único para o job
        job_name = f"transcription-{int(time.time())}-{os.getpid()}"
        
        # Inicia o job de transcrição
        print(f"Iniciando transcrição: {job_name}")
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode=language_code,
            MediaFormat=media_format,
            Media={'MediaFileUri': job_uri}
        )
        
        # Aguarda a transcrição terminar
        print("Aguardando conclusão da transcrição...")
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                        
            if job_status in ['COMPLETED', 'FAILED']:
                break
            
            print("Processando...")
            time.sleep(5)
        
        if job_status == 'COMPLETED':
            print("Transcrição concluída!")
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            transcript_json = requests.get(transcript_uri).json()
            
            # Salva o JSON completo no S3
            json_key = f"transcriptions/{job_name}.json"
            s3_client.put_object(
                Bucket=bucket_name,
                Key=json_key,
                Body=json.dumps(transcript_json),
                ContentType='application/json'
            )
            print(f"Resultado JSON salvo em: s3://{bucket_name}/{json_key}")
            
            # Limpeza: remove o arquivo de áudio original
            s3_client.delete_object(Bucket=bucket_name, Key=s3_audio_key)
            print(f"Arquivo de áudio removido: {s3_audio_key}")
            
            return transcript_json['results']['transcripts'][0]['transcript']

            #return f"s3://{bucket_name}/{json_key}"
            
        else:
            failure_reason = status['TranscriptionJob'].get('FailureReason', 'Motivo não especificado')
            raise Exception(f"Transcrição falhou: {failure_reason}")
            
    except Exception as e:
        # Limpeza em caso de erro
        try:
            if s3_audio_key:
                s3_client.delete_object(Bucket=bucket_name, Key=s3_audio_key)
            if json_key:
                s3_client.delete_object(Bucket=bucket_name, Key=json_key)
        except Exception as cleanup_error:
            print(f"Erro na limpeza: {cleanup_error}", file=sys.stderr)
        raise e
