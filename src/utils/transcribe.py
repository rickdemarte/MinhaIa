import os
import sys
import re
from pathlib import Path
import boto3
import requests
import time
from botocore.exceptions import ClientError

def transcribe_audio_aws(audio_file_path, language_code="pt-BR", media_format="mp3", bucket_name=None):
    """
    Transcreve um arquivo de áudio usando AWS Transcribe
    O arquivo será automaticamente enviado para S3 se necessário
    """
    
    # Clientes AWS
    s3_client = boto3.client('s3')
    transcribe_client = boto3.client('transcribe')
    
    # Se não especificar bucket, cria um nome padrão
    if not bucket_name:
        print("Nenhum bucket especificado.", file=sys.stderr)
        exit(1)
    
    # Nome do arquivo no S3 com timestamp
    file_name = os.path.basename(audio_file_path)
    s3_key = f"audio/{int(time.time())}-{file_name}"
    
    try:
        
        # Upload do arquivo para S3
        print(f"Enviando arquivo para S3: s3://{bucket_name}/{s3_key}")
        s3_client.upload_file(audio_file_path, bucket_name, s3_key)
        
        # URI do arquivo no S3
        job_uri = f"s3://{bucket_name}/{s3_key}"
        
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
            # Verifica o status do job
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                        
            if job_status in ['COMPLETED', 'FAILED']:
                break
            
            print("Processando...")
            time.sleep(5)  # Aguarda 5 segundos antes de verificar novamente
        
        # Verifica o resultado
        if job_status == 'COMPLETED':
            print("Transcrição concluída!")
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            transcript_json = requests.get(transcript_uri).json()
            
            # Limpeza: remove o arquivo do S3
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
                print(f"Arquivo removido do S3: {s3_key}")
            except:
                pass
            # retorna json puro
            return transcript_json['results']['transcripts'][0]['transcript']
            
        else:
            failure_reason = status['TranscriptionJob'].get('FailureReason', 'Motivo não especificado')
            raise Exception(f"Transcrição falhou: {failure_reason}")
            
    except Exception as e:
        # Limpeza em caso de erro
        try:
            s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
        except:
            pass
        raise e
