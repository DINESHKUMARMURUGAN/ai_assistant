from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
def load_model(model_name="mistralai/Mistral-7B-Instruct-v0.1"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, use_safetensors=True,device_map="auto",torch_dtype=torch.float16)
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return generator
