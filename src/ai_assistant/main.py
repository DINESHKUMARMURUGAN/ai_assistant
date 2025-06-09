from load_llm import load_model

def main():
    model_name = "mistralai/Mistral-7B-Instruct-v0.1"# "HuggingFaceTB/SmolLM2-1.7B-Instruct"# "sshleifer/tiny-gpt2"
    generator = load_model(model_name)
    prompt = "What is the capital of France?"
    output = generator(prompt, max_new_tokens=500)
    print("Generated Text:", output[0])

if __name__ == "__main__":
    main()



