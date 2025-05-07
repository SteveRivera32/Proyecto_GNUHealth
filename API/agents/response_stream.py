

import json

""""
    la funcon stream_response permite enviar respuestas en tiempo real al cliente.
    se toma parametro response response con chunks que se se retorna al hablitar 
    stream en el cliente de ollama.

"""


def stream_response(response_chunks,model,chat_id,created_time):
        

        for chunk in response_chunks:
            delta = {"role": "assistant", "content": chunk['message']['content']}
            json_chunk = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": model,
                "system_fingerprint": "fp_dummy",
                "choices": [
                    {
                        "index": 0,
                        "delta": delta,
                        "logprobs": None,
                        "finish_reason": None
                    }
                ]
            }
            
            yield f"data: {json.dumps(json_chunk)}\n\n"

        # Final message
        final_chunk = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": model,
            "system_fingerprint": "fp_dummy",
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ]
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"