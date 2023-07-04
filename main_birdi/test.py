from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import torch
import os

peft_model_id = "DioulaD/falcon-7b-instruct-qlora-ge-dq-v2"

model_path = "model/saved_model"  # Set the path to save the model

# Check if the model is already downloaded
if os.path.exists(model_path):
    model = PeftModel.from_pretrained(model_path)
else:
    model = AutoModelForCausalLM.from_pretrained(
        "tiiuae/falcon-7b-instruct",
        torch_dtype=torch.bfloat16,
        device_map="auto",
        resume_download=True,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(model, peft_model_id)
    model = model.merge_and_unload()

    # Save the downloaded model locally
    model.save_pretrained(model_path)

config = PeftConfig.from_pretrained(peft_model_id)

tknizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
tknizer.pad_token = tknizer.eos_token

prompt = "Verify that for rows where the category is Electronics, the userType column vaues are in the set: member, guest"

encoding = tknizer(prompt, return_tensors="pt").to("cuda:0")

with torch.inference_mode():
    out = model.generate(
        input_ids=encoding.input_ids,
        attention_mask=encoding.attention_mask,
        max_new_tokens=100, do_sample=True, temperature=0.3,
        eos_token_id=tknizer.eos_token_id,
        top_k=0
    )

response = tknizer.decode(out[0], skip_special_tokens=True)
print(response)
