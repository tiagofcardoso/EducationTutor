import boto3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(
    dotenv_path='/home/tiagocardoso/Projects/EducationTutor/audio_processing/api_keys/.env')

# Configure the AWS client


def get_polly_client():
    try:
        client = boto3.client(
            'polly',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        return client
    except Exception as e:
        print(f"Error configuring AWS Polly client: {str(e)}")
        return None


def texto_para_audio(texto, voice_id="Camila", output_format="mp3", arquivo="static/audio/response.mp3"):
    """
    Convert text to speech using Amazon Polly

    Args:
        texto (str): The text to convert to speech
        voice_id (str): The voice ID to use (default: Camila - Brazilian Portuguese)
        output_format (str): The output format (default: mp3)
        arquivo (str): The output file path (default: static/audio/response.mp3)

    Returns:
        str: Path to the generated audio file or None if an error occurred
    """
    try:
        # Get the Polly client
        polly_client = get_polly_client()
        if not polly_client:
            raise Exception("Failed to create Polly client")

        # Ensure the directory exists
        os.makedirs(os.path.dirname(arquivo), exist_ok=True)

        # Request speech synthesis
        response = polly_client.synthesize_speech(
            Text=texto,
            OutputFormat=output_format,
            VoiceId=voice_id,
            Engine='neural'  # Using the neural engine for better quality
        )

        # Save the audio stream to file
        if "AudioStream" in response:
            with open(arquivo, 'wb') as file:
                file.write(response['AudioStream'].read())
            return arquivo
        else:
            print("No AudioStream found in the response")
            return None

    except Exception as e:
        print(f"Error generating audio with Amazon Polly: {str(e)}")
        return None
