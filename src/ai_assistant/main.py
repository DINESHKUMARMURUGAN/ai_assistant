from ai_assistant.load_llm import load_model

def main():
    model_name = "HuggingFaceTB/SmolLM2-1.7B-Instruct"# "sshleifer/tiny-gpt2"
    generator = load_model(model_name)
    prompt = "What is the capital of France?"
    output = generator(prompt, max_new_tokens=500)
    print("Generated Text:", output[0]['generated_text'])

if __name__ == "__main__":
    main()
