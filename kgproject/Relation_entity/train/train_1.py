import pandas as pd
import logging
from seq2seq_model_3 import Seq2SeqModel

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)



with open("/hy-tmp/train_entity_1.txt", 'r') as f:
    s = [i[:-1].split('@_@') for i in f.readlines()]
train_entity_df = pd.DataFrame(s, columns=["input_text", "target_text"])

with open("/hy-tmp/dev_entity_1.txt", 'r') as f:
    s = [i[:-1].split('@_@') for i in f.readlines()]
eval_entity_df = pd.DataFrame(s, columns=["input_text", "target_text"])

with open("/hy-tmp/train_relation_1_new.txt", 'r') as f:
    s = [i[:-1].split('@_@') for i in f.readlines()]
train_relation_df = pd.DataFrame(s, columns=["input_text", "target_text"])

with open("/hy-tmp/dev_relation_1_new.txt", 'r') as f:
    s = [i[:-1].split('@_@') for i in f.readlines()]
eval_relation_df = pd.DataFrame(s, columns=["input_text", "target_text"])


model_args = {
    "reprocess_input_data": True,
    "overwrite_output_dir": True,
    "max_seq_length": 100,
    "train_batch_size": 64,
    "num_train_epochs": 20,
    "save_eval_checkpoints": False,
    "save_model_every_epoch": True,
    "evaluate_during_training": True,
    "evaluate_generated_text": True,
    "evaluate_during_training_verbose": True,
    "use_multiprocessing": False,
    "max_length": 100,
    "manual_seed": 4,
    #"save_steps": 4971,
    #"save_steps": 5908,
    "gradient_accumulation_steps": 1,
    "output_dir": "model_output/",
}

# Initialize model
model = Seq2SeqModel(
    encoder_decoder_type="bart",
    encoder_decoder_name="facebook/bart-base",
    args=model_args,
    use_cuda=True,
)


model.train_model(train_entity_df,
                  train_relation_df,
                  eval_data_1=eval_entity_df,
                  eval_data_2=eval_relation_df
                  )

