import argparse
import os
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

def finetune_lora(
    model_name: str,
    dataset_path: str,
    output_dir: str,
    lora_r: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.05,
    batch_size: int = 4,
    gradient_accumulation_steps: int = 4,
    learning_rate: float = 2e-4,
    num_train_epochs: int = 3,
    max_seq_length: int = 512,
    packing: bool = False,
    fp16: bool = False,
    bf16: bool = True,
):
    """
    Fine-tunes a pre-trained language model using LoRA (Low-Rank Adaptation).

    Args:
        model_name (str): The name of the pre-trained model to load from Hugging Face.
        dataset_path (str): Path to the dataset (e.g., a JSON file or a directory containing text files).
        output_dir (str): Directory to save the fine-tuned model and logs.
        lora_r (int): LoRA attention dimension.
        lora_alpha (int): Alpha parameter for LoRA scaling.
        lora_dropout (float): Dropout probability for LoRA layers.
        batch_size (int): Batch size per device during training.
        gradient_accumulation_steps (int): Number of updates steps to accumulate before performing a backward/update pass.
        learning_rate (float): Initial learning rate for the AdamW optimizer.
        num_train_epochs (int): Total number of training epochs to perform.
        max_seq_length (int): Maximum sequence length for tokenization.
        packing (bool): Whether to pack sequences into a single input.
        fp16 (bool): Whether to use fp16 (mixed precision) training.
        bf16 (bool): Whether to use bf16 (bfloat16) training.
    """

    # 1. Load Tokenizer and Model
    print(f"Loading tokenizer and model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right" # For causal models

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.bfloat16 if bf16 else (torch.float16 if fp16 else torch.float32),
        trust_remote_code=True,
    )
    model.config.use_cache = False # Disable cache for gradient checkpointing

    # 2. Prepare Model for LoRA Training
    model = prepare_model_for_kbit_training(model)
    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 3. Load and Preprocess Dataset
    print(f"Loading dataset from: {dataset_path}")
    # Assuming dataset_path points to a directory with text files or a single JSON file
    # For a simple text dataset, you might use:
    # dataset = load_dataset("text", data_files={"train": dataset_path})
    # For a JSON dataset, you might use:
    # dataset = load_dataset("json", data_files={"train": dataset_path})
    # For demonstration, let's assume a simple text dataset for now.
    # In a real scenario, you'd need to adapt this based on your dataset format.
    try:
        dataset = load_dataset("text", data_files={"train": dataset_path})
    except Exception as e:
        print(f"Error loading dataset as text: {e}. Trying as JSON...")
        try:
            dataset = load_dataset("json", data_files={"train": dataset_path})
        except Exception as e_json:
            print(f"Error loading dataset as JSON: {e_json}. Please ensure your dataset is in a supported format.")
            return

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=max_seq_length,
            padding="max_length" if not packing else False,
        )

    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text"], # Remove original text column after tokenization
    )

    # 4. Configure Training Arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate,
        num_train_epochs=num_train_epochs,
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        save_steps=500,
        save_total_limit=2,
        fp16=fp16,
        bf16=bf16,
        optim="paged_adamw_8bit", # Use 8-bit AdamW for memory efficiency
        report_to="none", # Disable reporting to external services like Weights & Biases
    )

    # 5. Create Trainer and Start Training
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
    )

    print("Starting training...")
    trainer.train()

    # 6. Save the fine-tuned model
    final_output_dir = os.path.join(output_dir, "lora_adapters")
    trainer.save_model(final_output_dir)
    print(f"Fine-tuned LoRA model saved to {final_output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune a language model using LoRA.")
    parser.add_argument("--model_name", type=str, default="mistralai/Mistral-7B-v0.1",
                        help="Name of the pre-trained model to load from Hugging Face.")
    parser.add_argument("--dataset_path", type=str, required=True,
                        help="Path to the dataset for fine-tuning (e.g., a JSON file or a directory containing text files).")
    parser.add_argument("--output_dir", type=str, default="./lora_finetuned_model",
                        help="Directory to save the fine-tuned model and logs.")
    parser.add_argument("--lora_r", type=int, default=32, help="LoRA attention dimension.")
    parser.add_argument("--lora_alpha", type=int, default=16, help="Alpha parameter for LoRA scaling.")
    parser.add_argument("--lora_dropout", type=float, default=0.05, help="Dropout probability for LoRA layers.")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size per device during training.")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=4,
                        help="Number of updates steps to accumulate before performing a backward/update pass.")
    parser.add_argument("--learning_rate", type=float, default=2e-4, help="Initial learning rate for the AdamW optimizer.")
    parser.add_argument("--num_train_epochs", type=int, default=3, help="Total number of training epochs to perform.")
    parser.add_argument("--max_seq_length", type=int, default=512, help="Maximum sequence length for tokenization.")
    parser.add_argument("--packing", action="store_true", help="Whether to pack sequences into a single input.")
    parser.add_argument("--fp16", action="store_true", help="Whether to use fp16 (mixed precision) training.")
    parser.add_argument("--bf16", action="store_true", help="Whether to use bf16 (bfloat16) training.")
    args = parser.parse_args()

    finetune_lora(**vars(args))