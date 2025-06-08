from load_llm.load_llm import load_model

def main():
    model_name = "mistralai/Mistral-7B-Instruct-v0.1"
    generator = load_model(model_name)
    prompt = "What is the capital of France?"
    output = generator(prompt, max_length=50)
    print("Generated Text:", output[0]['generated_text'])

if __name__ == "__main__":
    main()
