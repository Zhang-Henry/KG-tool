import logging
import os
import pickle
from multiprocessing import Pool
from typing import Tuple

import pandas as pd
import torch
from tokenizers.implementations import ByteLevelBPETokenizer
from tokenizers.processors import BertProcessing
from torch.utils.data import Dataset
from tqdm.auto import tqdm
from transformers import PreTrainedTokenizer

logger = logging.getLogger(__name__)


def preprocess_data(data):
    input_text_1, target_text_1, input_text_2, target_text_2, encoder_tokenizer, decoder_tokenizer, args = data

    input_text_1 = encoder_tokenizer.encode(
        input_text_1, max_length=args.max_seq_length, pad_to_max_length=True, return_tensors="pt",
    )
    target_text_1 = decoder_tokenizer.encode(
        target_text_1, max_length=args.max_seq_length, pad_to_max_length=True, return_tensors="pt"
    )
    input_text_2 = encoder_tokenizer.encode(
        input_text_2, max_length=args.max_seq_length, pad_to_max_length=True, return_tensors="pt",
    )
    target_text_2 = decoder_tokenizer.encode(
        target_text_2, max_length=args.max_seq_length, pad_to_max_length=True, return_tensors="pt"
    )
    return (torch.flatten(input_text_1), torch.flatten(target_text_1), torch.flatten(input_text_2),
            torch.flatten(target_text_2))


class Seq2SeqDataset(Dataset):
    def __init__(self, encoder_tokenizer, decoder_tokenizer, args, data_1, data_2, mode):
        cached_features_file = os.path.join(
            args.cache_dir, args.model_name + "_cached_" + str(args.max_seq_length) + str(len(data_1))
        )

        if os.path.exists(cached_features_file) and (
                (not args.reprocess_input_data and not args.no_cache)
                or (mode == "dev" and args.use_cached_eval_features and not args.no_cache)
        ):
            logger.info(" Loading features from cached file_1 %s", cached_features_file)
            with open(cached_features_file, "rb") as handle:
                self.examples = pickle.load(handle)
        else:
            logger.info(" Creating features from dataset file at %s", args.cache_dir)

            data = []
            for input_text_1, target_text_1, input_text_2, target_text_2 in zip(data_1["input_text"],
                                                                                data_1["target_text"],
                                                                                data_2["input_text"],
                                                                                data_2["target_text"]):
                data.append[(
                input_text_1, target_text_1, input_text_2, target_text_2, encoder_tokenizer, decoder_tokenizer, args)]

            if args.use_multiprocessing:
                with Pool(args.process_count) as p:
                    self.examples = list(
                        tqdm(
                            p.imap(preprocess_data, data, chunksize=args.multiprocessing_chunksize),
                            total=len(data),
                            disable=args.silent,
                        )
                    )
            else:
                self.examples = [preprocess_data(d) for d in tqdm(data, disable=args.silent)]

            logger.info(" Saving features into cached file %s", cached_features_file)
            with open(cached_features_file, "wb") as handle:
                pickle.dump(self.examples, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, index):
        return self.examples[index]



def preprocess_data_bart(data):
    input_text_1, target_text_1, input_text_2, target_text_2, tokenizer, args = data

    input_ids_1 = tokenizer.batch_encode_plus(
        [input_text_1], max_length=args.max_seq_length, padding='max_length', truncation=True, return_tensors="pt",
    )  

    target_ids_1 = tokenizer.batch_encode_plus(
        [target_text_1], max_length=args.max_seq_length, padding='max_length', truncation=True, return_tensors="pt"
    )
    input_ids_2 = tokenizer.batch_encode_plus(
        [input_text_2], max_length=args.max_seq_length, padding='max_length', truncation=True, return_tensors="pt",
    )
    target_ids_2 = tokenizer.batch_encode_plus(
        [target_text_2], max_length=args.max_seq_length, padding='max_length', truncation=True, return_tensors="pt"
    )

    return {
        "source_ids_1": input_ids_1["input_ids"].squeeze(),  
        "source_mask_1": input_ids_1["attention_mask"].squeeze(),
        "target_ids_1": target_ids_1["input_ids"].squeeze(),
        "source_ids_2": input_ids_2["input_ids"].squeeze(),  
        "source_mask_2": input_ids_2["attention_mask"].squeeze(),
        "target_ids_2": target_ids_2["input_ids"].squeeze(),
    }



class SimpleSummarizationDataset(Dataset):
    def __init__(self, tokenizer, args, data_1, data_2, mode):
        self.tokenizer = tokenizer
       
        cached_features_file = os.path.join(
            args.cache_dir, args.model_name + "_cached_" + str(args.max_seq_length) + str(len(data_1))
        )
      
        if os.path.exists(cached_features_file) and (
                (not args.reprocess_input_data and not args.no_cache)
                or (mode == "dev" and args.use_cached_eval_features and not args.no_cache)
        ):
            logger.info(" Loading features from cached file %s", cached_features_file)  
            with open(cached_features_file, "rb") as handle:
                self.examples = pickle.load(handle)  
        else:
            logger.info(" Creating features from dataset file at %s", args.cache_dir)

            data = []
            for input_text_1, target_text_1, input_text_2, target_text_2 in zip(data_1["input_text"],
                                                                                data_1["target_text"],
                                                                                data_2["input_text"],
                                                                                data_2["target_text"]):
                data.append((input_text_1, target_text_1, input_text_2, target_text_2, tokenizer, args))  


            if args.use_multiprocessing: 
                with Pool(args.process_count) as p:  
                    self.examples = list(
                        tqdm(  
                            p.imap(preprocess_data_bart, data, chunksize=args.multiprocessing_chunksize),

                            total=len(data),  
                            disable=args.silent,  
                        )
                    )

            else:
                self.examples = [preprocess_data_bart(d) for d in tqdm(data, disable=args.silent)]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, index):
        return self.examples[index]
