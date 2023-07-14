from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import torch


def load_peft_model():
    peft_model_id = "DioulaD/falcon-7b-instruct-qlora-ge-dq-v2"    
    model = AutoModelForCausalLM.from_pretrained(
            "tiiuae/falcon-7b-instruct",
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        )
    model = PeftModel.from_pretrained(model, peft_model_id)
    model = model.merge_and_unload()

    config = PeftConfig.from_pretrained(peft_model_id)

    tknizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
    tknizer.pad_token = tknizer.eos_token
    return model, tknizer



def get_expectations(prompt, model, tknizer):
  """
  Convert natural language query to great expectation methods using finetuned falcon 7b
  Params:
    prompt : Natural language query
    model : Model download from huggingface hub
    tknizer = Tokenizer from peft model
  """
  try:
    # If CUDA support is not available, encoding will silenty fail if cuda:0 is hardcoded
    if torch.cuda.is_available():
      device = 'cuda:0'
    else:
      device = 'cpu'
    
    encoding = tknizer(prompt, return_tensors="pt").to(device)

    with torch.inference_mode():
      out = model.generate(
          input_ids=encoding.input_ids,
          attention_mask=encoding.attention_mask,
          max_new_tokens=100, do_sample=True, temperature=0.3,
          eos_token_id=tknizer.eos_token_id,
          top_k=0
      )
    response = tknizer.decode(out[0], skip_special_tokens=True)
    return response.split("\n")[1]

  except Exception as e:
    print("An error occurred: ", e)
