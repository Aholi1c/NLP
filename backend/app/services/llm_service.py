import openai
from typing import List, Dict, Any, Optional
from ..core.config import settings
import json

class LLMService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        进行文本聊天完成
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream
            )

            if stream:
                return response

            result = {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "model_used": model,
                "tokens_used": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            }

            return result

        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")

    async def analyze_image(
        self,
        image_url: str,
        prompt: str = "Describe this image in detail.",
        model: str = "gpt-4-vision-preview"
    ) -> Dict[str, Any]:
        """
        分析图像内容
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            return {
                "analysis": response.choices[0].message.content,
                "model_used": model,
                "tokens_used": response.usage.total_tokens if response.usage else None
            }

        except Exception as e:
            raise Exception(f"Image analysis error: {str(e)}")

    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        转录音频文件
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )

            return {
                "text": response.text,
                "language": language or "detected"
            }

        except Exception as e:
            raise Exception(f"Audio transcription error: {str(e)}")

    async def text_to_speech(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1"
    ) -> str:
        """
        文本转语音
        """
        try:
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text
            )

            # 保存音频文件
            output_file = f"tts_output_{hash(text)}.mp3"
            response.stream_to_file(output_file)

            return output_file

        except Exception as e:
            raise Exception(f"Text-to-speech error: {str(e)}")

    async def generate_embeddings(
        self,
        text: str,
        model: str = "text-embedding-ada-002"
    ) -> List[float]:
        """
        生成文本嵌入向量
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            raise Exception(f"Embedding generation error: {str(e)}")

# 全局LLM服务实例
llm_service = LLMService()