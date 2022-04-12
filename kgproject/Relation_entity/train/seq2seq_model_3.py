import logging
import math
import os
import random
import warnings
from dataclasses import asdict
from multiprocessing import Pool

import numpy as np
import pandas as pd
import torch
from tensorboardX import SummaryWriter
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler

from tqdm.auto import tqdm, trange
from transformers import (
    AdamW,
    AutoConfig,
    AutoModel,
    AutoTokenizer,
    BartConfig,
    BartForConditionalGeneration,
    BartTokenizer,
    BertConfig,
    BertForMaskedLM,
    BertModel,
    BertTokenizer,
    RobertaConfig,
    RobertaModel,
    RobertaTokenizer,
    get_linear_schedule_with_warmup,
    EncoderDecoderModel,
)

from simpletransformers.config.model_args import Seq2SeqArgs
from seq2seq_utils_1 import Seq2SeqDataset, SimpleSummarizationDataset

try:
    import wandb

    wandb_available = True
except ImportError:
    wandb_available = False

logger = logging.getLogger(__name__)

MODEL_CLASSES = {
    "auto": (AutoConfig, AutoModel, AutoTokenizer),
    "bart": (BartConfig, BartForConditionalGeneration, BartTokenizer),
    "bert": (BertConfig, BertModel, BertTokenizer),
    "roberta": (RobertaConfig, RobertaModel, RobertaTokenizer),

}


class Seq2SeqModel:
    def __init__(
            self,
            encoder_type=None,
            encoder_name=None,
            decoder_name=None,
            encoder_decoder_type=None,
            encoder_decoder_name=None,
            config=None,
            args=None,
            use_cuda=True,
            cuda_device=-1,
            **kwargs
    ):

      
        if not config:
            # if not ((encoder_name and decoder_name) or encoder_decoder_name) and not encoder_type:
            if not ((encoder_name and decoder_name) or encoder_decoder_name):
                raise ValueError(
                    "You must specify a Seq2Seq config \t OR \t"
                    "encoder_type, encoder_name, and decoder_name OR \t \t"
                    "encoder_type and encoder_decoder_name"
                )
            elif not (encoder_type or encoder_decoder_type):
                raise ValueError(
                    "You must specify a Seq2Seq config \t OR \t"
                    "encoder_type, encoder_name, and decoder_name \t OR \t"
                    "encoder_type and encoder_decoder_name"
                )

        self.args = self._load_model_args(encoder_decoder_name)  

        if isinstance(args, dict):  
            self.args.update_from_dict(args)  
        elif isinstance(args, Seq2SeqArgs):  
            self.args = args

        if "sweep_config" in kwargs:
            sweep_config = kwargs.pop("sweep_config")
            sweep_values = {key: value["value"] for key, value in sweep_config.as_dict().items() if key != "_wandb"}
            
            self.args.update_from_dict(sweep_values) 

        if self.args.manual_seed:  
            random.seed(self.args.manual_seed)
            np.random.seed(self.args.manual_seed)
            torch.manual_seed(self.args.manual_seed)  
            if self.args.n_gpu > 0:  
                torch.cuda.manual_seed_all(self.args.manual_seed)  

        if use_cuda: 
            if torch.cuda.is_available():
                if cuda_device == -1:  
                    self.device = torch.device("cuda")  
                else:
                    self.device = torch.device(f"cuda:{cuda_device}")  
            else:
                raise ValueError(
                    "'use_cuda' set to True when cuda is unavailable."
                    "Make sure CUDA is available or set `use_cuda=False`."
                )
        else:
            self.device = "cpu"

        self.results = {}

        if not use_cuda:
            self.args.fp16 = False 

        # config = EncoderDecoderConfig.from_encoder_decoder_configs(config, config)
        if encoder_decoder_type:
            config_class, model_class, tokenizer_class = MODEL_CLASSES[encoder_decoder_type]
        else:
            config_class, model_class, tokenizer_class = MODEL_CLASSES[encoder_type]

        if encoder_decoder_type in ["bart", "marian", "blender", "blender-large"]:
            self.model = model_class.from_pretrained(encoder_decoder_name)
       
            if encoder_decoder_type in ["bart", "blender", "blender-large"]:
                self.encoder_tokenizer = tokenizer_class.from_pretrained(encoder_decoder_name)
                # self.encoder_tokenizer = tokenizer_class.from_pretrained(encoder_decoder_name, additional_special_tokens=['__defi__', '__sim__'])
                # self.model.resize_token_embeddings(len(self.encoder_tokenizer))
            elif encoder_decoder_type == "marian":
                if self.args.base_marian_model_name:
                    self.encoder_tokenizer = tokenizer_class.from_pretrained(self.args.base_marian_model_name)
                else:
                    self.encoder_tokenizer = tokenizer_class.from_pretrained(encoder_decoder_name)
            self.decoder_tokenizer = self.encoder_tokenizer 
            self.config = self.model.config  
        else:
            if encoder_decoder_name:  
                # self.model = EncoderDecoderModel.from_pretrained(encoder_decoder_name)
                self.model = EncoderDecoderModel.from_encoder_decoder_pretrained(
                    os.path.join(encoder_decoder_name, "encoder"), os.path.join(encoder_decoder_name, "decoder")
                )
                self.model.encoder = model_class.from_pretrained(os.path.join(encoder_decoder_name, "encoder"))
                self.model.decoder = BertForMaskedLM.from_pretrained(os.path.join(encoder_decoder_name, "decoder"))
                self.encoder_tokenizer = tokenizer_class.from_pretrained(os.path.join(encoder_decoder_name, "encoder"))
                self.decoder_tokenizer = BertTokenizer.from_pretrained(os.path.join(encoder_decoder_name, "decoder"))
            else:  
                self.model = EncoderDecoderModel.from_encoder_decoder_pretrained(
                    encoder_name, decoder_name, config=config
                )
                self.encoder_tokenizer = tokenizer_class.from_pretrained(encoder_name)
                self.decoder_tokenizer = BertTokenizer.from_pretrained(decoder_name)
            self.encoder_config = self.model.config.encoder
            self.decoder_config = self.model.config.decoder

        if self.args.wandb_project and not wandb_available:
            warnings.warn("wandb_project specified but wandb is not available. Wandb disabled.")
           
            self.args.wandb_project = None

        if encoder_decoder_name:
            self.args.model_name = encoder_decoder_name


            self.args.base_marian_model_name = encoder_decoder_name

        elif encoder_name and decoder_name:
            self.args.model_name = encoder_name + "-" + decoder_name
        else:
            self.args.model_name = "encoder-decoder"

        if encoder_decoder_type:
            self.args.model_type = encoder_decoder_type
        elif encoder_type:
            self.args.model_type = encoder_type + "-bert"  
        else:
            self.args.model_type = "encoder-decoder"

   
    def train_model(
            self, train_data_1, train_data_2, output_dir=None, show_running_loss=True, args=None, eval_data_1=None,
            eval_data_2=None, verbose=True,
            **kwargs,
    ):

        if args:
            self.args.update_from_dict(args)

        if self.args.evaluate_during_training and eval_data_1 is None and eval_data_2 is None:
            raise ValueError(
                "evaluate_during_training is enabled but eval_data is not specified."
                " Pass eval_data to model.train_model() if using evaluate_during_training."
            )

        if not output_dir:
            output_dir = self.args.output_dir

        if os.path.exists(output_dir) and os.listdir(output_dir) and not self.args.overwrite_output_dir:
            raise ValueError(
                "Output directory ({}) already exists and is not empty."
                " Set args.overwrite_output_dir = True to overcome.".format(output_dir)
            )

        self._move_model_to_device() 

        train_dataset = self.load_and_cache_examples(train_data_1, train_data_2, verbose=verbose) 



        os.makedirs(output_dir, exist_ok=True)  

        global_step, tr_loss = self.train(  
            train_dataset,
            output_dir,
            show_running_loss=show_running_loss,
            eval_data_1=eval_data_1,
            eval_data_2=eval_data_2,
            verbose=verbose,
            **kwargs,
        )

        self._save_model(self.args.output_dir, model=self.model)


        if verbose:  
            logger.info(" Training of {} model complete. Saved to {}.".format(self.args.model_name, output_dir))

    def train(
            self, train_dataset, output_dir, show_running_loss=True, eval_data_1=None, eval_data_2=None,verbose=True, **kwargs,
    ):

        model = self.model

        args = self.args

        tb_writer = SummaryWriter(logdir=args.tensorboard_dir)

        train_sampler = RandomSampler(train_dataset) 
        train_dataloader = DataLoader(
            train_dataset,
            sampler=train_sampler,
            batch_size=args.train_batch_size,
            num_workers=self.args.dataloader_num_workers, 
        )

        if args.max_steps > 0:
            t_total = args.max_steps 
            args.num_train_epochs = args.max_steps // (len(train_dataloader) // args.gradient_accumulation_steps) + 1
     
        else:
            t_total = len(train_dataloader) // args.gradient_accumulation_steps * args.num_train_epochs

        no_decay = ["bias", "LayerNorm.weight"]

        optimizer_grouped_parameters = [] 
        custom_parameter_names = set()  
        for group in self.args.custom_parameter_groups:  
            params = group.pop("params")
            custom_parameter_names.update(params)  
            param_group = {**group} 
            param_group["params"] = [p for n, p in model.named_parameters() if n in params]  
           
            optimizer_grouped_parameters.append(param_group)  

        for group in self.args.custom_layer_parameters:  
            layer_number = group.pop("layer")
            layer = f"layer.{layer_number}."
            group_d = {**group}
            group_nd = {**group}
            group_nd["weight_decay"] = 0.0
          
            params_d = []
            params_nd = []
            for n, p in model.named_parameters():
                if n not in custom_parameter_names and layer in n: 
                    if any(nd in n for nd in no_decay):  
                        params_nd.append(p)
                    else:
                        params_d.append(p)
                    custom_parameter_names.add(n)
            group_d["params"] = params_d
            group_nd["params"] = params_nd

            optimizer_grouped_parameters.append(group_d)
            optimizer_grouped_parameters.append(group_nd)

        if not self.args.train_custom_parameters_only:  
            optimizer_grouped_parameters.extend(  
                [
                    {
                        "params": [
                            p
                            for n, p in model.named_parameters()
                            if n not in custom_parameter_names and not any(nd in n for nd in no_decay)
                          
                        ],
                        "weight_decay": args.weight_decay,
                    },
                    {
                        "params": [
                            p
                            for n, p in model.named_parameters()
                            if n not in custom_parameter_names and any(nd in n for nd in no_decay)
                        ],
                        "weight_decay": 0.0,
                    },
                ]
            )

        warmup_steps = math.ceil(t_total * args.warmup_ratio)  
     
        args.warmup_steps = warmup_steps if args.warmup_steps == 0 else args.warmup_steps

      
        optimizer = AdamW(optimizer_grouped_parameters, lr=args.learning_rate, eps=args.adam_epsilon)
      
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=args.warmup_steps, num_training_steps=t_total
        )
       

        if (
                args.model_name
                and os.path.isfile(os.path.join(args.model_name, "optimizer.pt"))
                and os.path.isfile(os.path.join(args.model_name, "scheduler.pt"))
        ):
           
            optimizer.load_state_dict(torch.load(os.path.join(args.model_name, "optimizer.pt")))
            scheduler.load_state_dict(torch.load(os.path.join(args.model_name, "scheduler.pt")))

        if args.n_gpu > 1:  
            model = torch.nn.DataParallel(model)

        logger.info(" Training started")

        global_step = 0
        tr_loss, logging_loss = 0.0, 0.0
        model.zero_grad()
        train_iterator = trange(int(args.num_train_epochs), desc="Epoch", disable=args.silent, mininterval=0)
      
        epoch_number = 0
        best_eval_metric = None
        early_stopping_counter = 0
        steps_trained_in_current_epoch = 0
        epochs_trained = 0

        if args.model_name and os.path.exists(args.model_name):
            try:
               
                checkpoint_suffix = args.model_name.split("/")[-1].split("-")
                if len(checkpoint_suffix) > 2:
                    checkpoint_suffix = checkpoint_suffix[1]
                else:
                    checkpoint_suffix = checkpoint_suffix[-1]
                global_step = int(checkpoint_suffix)
                epochs_trained = global_step // (len(train_dataloader) // args.gradient_accumulation_steps)
               

                steps_trained_in_current_epoch = global_step % (
                        len(train_dataloader) // args.gradient_accumulation_steps
                ) 

                logger.info("   Continuing training from checkpoint, will skip to saved global_step")
                logger.info("   Continuing training from epoch %d", epochs_trained)
                logger.info("   Continuing training from global step %d", global_step)
                logger.info("   Will skip the first %d steps in the current epoch", steps_trained_in_current_epoch)

            except ValueError:
                logger.info("   Starting fine-tuning.")

        if args.evaluate_during_training:  
            training_progress_scores = self._create_training_progress_scores(**kwargs) 

        if args.wandb_project: 
            wandb.init(project=args.wandb_project, config={**asdict(args)}, **args.wandb_kwargs)
          
            wandb.watch(self.model)
           

        if args.fp16:
            from torch.cuda import amp

            scaler = amp.GradScaler() 
          

        model.train()
        for current_epoch in train_iterator:
            if epochs_trained > 0:
                epochs_trained -= 1
                continue
            train_iterator.set_description(f"Epoch {epoch_number + 1} of {args.num_train_epochs}") 
            batch_iterator = tqdm(  
                train_dataloader,
                desc=f"Running Epoch {epoch_number} of {args.num_train_epochs}",
                disable=args.silent,
                mininterval=0,
            )
            for step, batch in enumerate(batch_iterator): 
                if steps_trained_in_current_epoch > 0:
                    steps_trained_in_current_epoch -= 1
                    continue
              

                inputs_1, inputs_2 = self._get_inputs_dict(batch)
              
                if args.fp16:
                    with amp.autocast(): 
                       
                        outputs_1 = model(**inputs_1)
                        
                        loss_1 = outputs_1[0]


                else:
                    outputs_1 = model(**inputs_1)
                   
                    loss_1 = outputs_1[0]


                if args.n_gpu > 1:
                    loss = loss_1.mean()   
                else:
                    loss_1 = loss_1




                if args.gradient_accumulation_steps > 1:
                    loss_1 = loss_1 / args.gradient_accumulation_steps

                if args.fp16:
                    scaler.scale(loss_1).backward()
                   
                else:
                    loss_1.backward()


                if (step + 1) % args.gradient_accumulation_steps == 0:
                  
                    if args.fp16:
                        scaler.unscale_(optimizer)
                     
                    torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

                    if args.fp16:
                        scaler.step(optimizer)
                  
                        scaler.update()
              
                    else:
                        optimizer.step()

                    scheduler.step()  
                    model.zero_grad()
                if args.fp16:
                    with amp.autocast():  
                        outputs_2 = model(**inputs_2)

                        loss_2 = outputs_2[0]


                else:
                    outputs_2 = model(**inputs_2)
                
                    loss_2 = outputs_2[0]


                if args.n_gpu > 1:
                    loss_2 = loss_2.mean()   
                else:
                    loss_2 = loss_2
                current_loss = loss_2.item()+loss_1.item()

                if show_running_loss:
                    batch_iterator.set_description(
                        f"Epochs {epoch_number}/{args.num_train_epochs}. Running Loss: {current_loss:9.4f}"
                    )

                if args.gradient_accumulation_steps > 1:
                    loss_2 = loss_2 / args.gradient_accumulation_steps

                if args.fp16:
                    scaler.scale(loss_2).backward()
                   
                else:
                    loss_2.backward()

                tr_loss =tr_loss+ loss_1.item()+loss_2.item()  
                if (step + 1) % args.gradient_accumulation_steps == 0:
                 
                    if args.fp16:
                        scaler.unscale_(optimizer)

                    torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

                    if args.fp16:
                        scaler.step(optimizer)

                        scaler.update()

                    else:
                        optimizer.step()

                    scheduler.step()  # Update learning rate schedule
                    model.zero_grad()



                    global_step += 1

                    if args.logging_steps > 0 and global_step % args.logging_steps == 0:

                        tb_writer.add_scalar("lr", scheduler.get_lr()[0], global_step)

                        tb_writer.add_scalar("loss", (tr_loss - logging_loss) / args.logging_steps, global_step)
                        logging_loss = tr_loss
                        if args.wandb_project:
                            wandb.log(
                                {
                                    "Training loss": current_loss,
                                    "lr": scheduler.get_lr()[0],
                                    "global_step": global_step,
                                }
                            )



            epoch_number += 1
            output_dir_current = os.path.join(output_dir, "checkpoint-{}-epoch-{}".format(global_step, epoch_number))

            if args.save_model_every_epoch or args.evaluate_during_training:
                os.makedirs(output_dir_current, exist_ok=True)

            if args.save_model_every_epoch and epoch_number%2==0: 
                self._save_model(output_dir_current, optimizer, scheduler, model=model)

            if args.evaluate_during_training:
                results = self.eval_model(
                    eval_data_1,
                    eval_data_2,
                    verbose=verbose and args.evaluate_during_training_verbose,
                    silent=args.evaluate_during_training_silent,
                    **kwargs,
                )

                if args.save_eval_checkpoints:
                    self._save_model(output_dir_current, optimizer, scheduler, results=results)

                training_progress_scores["global_step"].append(global_step)
                training_progress_scores["train_loss"].append(current_loss)
                for key in results: 
                    training_progress_scores[key].append(results[key])
                report = pd.DataFrame(training_progress_scores)
                report.to_csv(os.path.join(args.output_dir, "training_progress_scores.csv"), index=False) 

                if args.wandb_project:
                    wandb.log(self._get_last_metrics(training_progress_scores))

                if not best_eval_metric:
                    best_eval_metric = results[args.early_stopping_metric]
                    if args.save_best_model:
                        self._save_model(args.best_model_dir, optimizer, scheduler, model=model, results=results)
                if best_eval_metric and args.early_stopping_metric_minimize:
                    if results[args.early_stopping_metric] - best_eval_metric < args.early_stopping_delta:
                        best_eval_metric = results[args.early_stopping_metric]
                        if args.save_best_model:
                            self._save_model(args.best_model_dir, optimizer, scheduler, model=model, results=results)
                        early_stopping_counter = 0
                    else:
                        if args.use_early_stopping and args.early_stopping_consider_epochs:
                            if early_stopping_counter < args.early_stopping_patience:
                                early_stopping_counter += 1
                                if verbose:
                                    logger.info(f" No improvement in {args.early_stopping_metric}")
                                    logger.info(f" Current step: {early_stopping_counter}")
                                    logger.info(f" Early stopping patience: {args.early_stopping_patience}")
                            else:
                                if verbose:
                                    logger.info(f" Patience of {args.early_stopping_patience} steps reached")
                                    logger.info(" Training terminated.")
                                    train_iterator.close()
                                return global_step, tr_loss / global_step
                else:
                    if results[args.early_stopping_metric] - best_eval_metric > args.early_stopping_delta:
                        best_eval_metric = results[args.early_stopping_metric]
                        if args.save_best_model:
                            self._save_model(args.best_model_dir, optimizer, scheduler, model=model, results=results)
                        early_stopping_counter = 0
                    else:
                        if args.use_early_stopping and args.early_stopping_consider_epochs:
                            if early_stopping_counter < args.early_stopping_patience:
                                early_stopping_counter += 1
                                if verbose:
                                    logger.info(f" No improvement in {args.early_stopping_metric}")
                                    logger.info(f" Current step: {early_stopping_counter}")
                                    logger.info(f" Early stopping patience: {args.early_stopping_patience}")
                            else:
                                if verbose:
                                    logger.info(f" Patience of {args.early_stopping_patience} steps reached")
                                    logger.info(" Training terminated.")
                                    train_iterator.close()
                                return global_step, tr_loss / global_step

        return global_step, tr_loss / global_step

    def eval_model(self, eval_data_1,eval_data_2, output_dir=None, verbose=True, silent=False, **kwargs):
     

        if not output_dir:
            output_dir = self.args.output_dir

        self._move_model_to_device() 

        eval_dataset = self.load_and_cache_examples(eval_data_1,eval_data_2, evaluate=True, verbose=verbose, silent=silent)
        os.makedirs(output_dir, exist_ok=True)
        result = self.evaluate(eval_dataset, output_dir, verbose=verbose, silent=silent, **kwargs)
       
        self.results.update(result)

        if self.args.evaluate_generated_text:
           
            result = self.evaluate_decode(eval_dataset, output_dir, verbose=verbose, silent=silent, **kwargs)
            self.results.update(result)

        if verbose:
            logger.info(self.results)

        return self.results

    def evaluate(self, eval_dataset, output_dir, verbose=True, silent=False, **kwargs):
    
        model = self.model
        args = self.args
        eval_output_dir = output_dir

        results = {}

        eval_sampler = SequentialSampler(eval_dataset)
        eval_dataloader = DataLoader(eval_dataset, sampler=eval_sampler, batch_size=args.eval_batch_size)

        if args.n_gpu > 1:
            model = torch.nn.DataParallel(model)

        eval_loss_1 = 0.0
        eval_loss_2=0.0
        nb_eval_steps = 0
        model.eval()

        for batch in tqdm(eval_dataloader, disable=args.silent or silent, desc="Running Evaluation"):
           

            inputs_1,inputs_2 = self._get_inputs_dict(batch)
            with torch.no_grad():
                outputs_1 = model(**inputs_1)
                loss_1 = outputs_1[0]
                eval_loss_1 += loss_1.mean().item()
            with torch.no_grad():
                outputs_2=model(**inputs_2)
                loss_2=outputs_2[0]
                eval_loss_2+=loss_2.mean().item()
            nb_eval_steps += 1
            eval_loss=eval_loss_1+eval_loss_2
        eval_loss = eval_loss / nb_eval_steps
        results["eval_loss"] = eval_loss

        output_eval_file = os.path.join(eval_output_dir, "eval_results.txt")
        with open(output_eval_file, "w") as writer:
            for key in sorted(results.keys()):
                writer.write("{} = {}\n".format(key, str(results[key])))

        return results

    def evaluate_decode(self, eval_dataset, output_dir, verbose=True, silent=False, **kwargs):
  

        model = self.model
        args = self.args
        eval_output_dir = output_dir

        results = {}

        eval_sampler = SequentialSampler(eval_dataset)
        eval_dataloader = DataLoader(eval_dataset, sampler=eval_sampler, batch_size=args.eval_batch_size)

        if args.n_gpu > 1:
            model = torch.nn.DataParallel(model)

        eval_loss = 0.0
        eval_loss_1=0.0
        eval_loss_2=0.0
        nb_eval_steps = 0
        model.eval()
        correct_1, count_1 = 0, 0
        correct_2, count_2 = 0, 0
        for batch in tqdm(eval_dataloader, disable=args.silent or silent, desc="Running Evaluation"):
           
            inputs_1,inputs_2 = self._get_inputs_dict(batch)
            
            with torch.no_grad(): 
                outputs_1 = model(**inputs_1)
                loss_1 = outputs_1[0]
                eval_loss_1 += loss_1.mean().item()
                decode_outputs_1 = torch.argmax(outputs_1[1], dim=-1).view(-1)  
                labels_1 = inputs_1["labels"].view(-1)
                for i, j in zip(labels_1, decode_outputs_1):
                    if i == j and i != -100:
                        correct_1 += 1
                    if i != -100:
                        count_1 += 1
            with torch.no_grad(): 
                outputs_2 = model(**inputs_2)
                loss_2 = outputs_2[0]
                eval_loss_2 += loss_2.mean().item()
                decode_outputs_2 = torch.argmax(outputs_2[1], dim=-1).view(-1) 
                labels_2 = inputs_2["labels"].view(-1)
                for i, j in zip(labels_2, decode_outputs_2):
                    if i == j and i != -100:
                        correct_2 += 1
                    if i != -100:
                        count_2 += 1
            nb_eval_steps += 1

        results["eval_acc_1"] = correct_1 / count_1
        results["eval_acc_2"] = correct_2 / count_2

        return results

    def predict(self, to_predict):
     

        self._move_model_to_device()

        all_outputs = []
        # Batching
        for batch in [
            to_predict[i: i + self.args.eval_batch_size] for i in range(0, len(to_predict), self.args.eval_batch_size)
        ]:  
            if self.args.model_type == "marian":
                input_ids = self.encoder_tokenizer.prepare_translation_batch(
                    batch, max_length=self.args.max_seq_length, padding='max_length', truncation=True,
                    return_tensors="pt",
                )["input_ids"]
            else:
                input_ids = self.encoder_tokenizer.batch_encode_plus(
                    batch, max_length=self.args.max_seq_length, padding='max_length', truncation=True,
                    return_tensors="pt",
                )["input_ids"]
            input_ids = input_ids.to(self.device)

            if self.args.model_type in ["bart", "marian", "blender", "blender-large"]:

                outputs = self.model.generate( 
                    input_ids=input_ids,
                    num_beams=self.args.num_beams,
                  
                    max_length=self.args.max_length, 
                    length_penalty=self.args.length_penalty,
                    early_stopping=self.args.early_stopping, 
                    repetition_penalty=self.args.repetition_penalty, 
                    do_sample=self.args.do_sample,
                  
                    top_k=self.args.top_k, 
                    top_p=self.args.top_p,  
                    num_return_sequences=self.args.num_return_sequences,  
                   
                )
            else:
                outputs = self.model.generate(
                    input_ids=input_ids,
                    decoder_start_token_id=self.model.config.decoder.pad_token_id,
                    num_beams=self.args.num_beams,
                    max_length=self.args.max_length,
                    length_penalty=self.args.length_penalty,
                    early_stopping=self.args.early_stopping,
                    repetition_penalty=self.args.repetition_penalty,
                    do_sample=self.args.do_sample,
                    top_k=self.args.top_k,
                    top_p=self.args.top_p,
                    num_return_sequences=self.args.num_return_sequences,
                )

            all_outputs.extend(outputs.cpu().numpy())

        if self.args.use_multiprocessed_decoding:
            self.model.to("cpu")
            with Pool(self.args.process_count) as p:
                outputs = list(
                    tqdm(
                        p.imap(self._decode, all_outputs, chunksize=self.args.multiprocessing_chunksize),
                        total=len(all_outputs),
                        desc="Decoding outputs",
                        disable=self.args.silent,
                    )
                )
            self._move_model_to_device()
        else:
            outputs = [
                self.decoder_tokenizer.decode(output_id, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                for output_id in all_outputs
            ]

        if self.args.num_return_sequences > 1: 
            return [
                outputs[i: i + self.args.num_return_sequences]
                for i in range(0, len(outputs), self.args.num_return_sequences)
            ]
        else:
            return outputs

    def predict_sep(self, to_predict, decoder_input_token_id):


        self._move_model_to_device()

        all_outputs = []

        for batch in [
            to_predict[i: i + self.args.eval_batch_size] for i in range(0, len(to_predict), self.args.eval_batch_size)
        ]:
            if self.args.model_type == "marian":
                input_ids = self.encoder_tokenizer.prepare_translation_batch(
                    batch, max_length=self.args.max_seq_length, padding='max_length', truncation=True,
                    return_tensors="pt",
                )["input_ids"]
            else:
                input_ids = self.encoder_tokenizer.batch_encode_plus(
                    batch, max_length=self.args.max_seq_length, padding='max_length', truncation=True,
                    return_tensors="pt",
                )["input_ids"]
            input_ids = input_ids.to(self.device)

            if self.args.model_type in ["bart", "marian", "blender", "blender-large"]:
                outputs = self.model.generate(
                    input_ids=input_ids,
                    num_beams=self.args.num_beams,
                    max_length=self.args.max_length,
                    length_penalty=self.args.length_penalty,
                    early_stopping=self.args.early_stopping,
                    repetition_penalty=self.args.repetition_penalty,
                    do_sample=self.args.do_sample,
                    top_k=self.args.top_k,
                    top_p=self.args.top_p,
                    num_return_sequences=self.args.num_return_sequences,
                    decoder_start_token_id=decoder_input_token_id
                    # temperature=0.7
                )
            else:
                outputs = self.model.generate(
                    input_ids=input_ids,
                    decoder_start_token_id=self.model.config.decoder.pad_token_id,
                    num_beams=self.args.num_beams,
                    max_length=self.args.max_length,
                    length_penalty=self.args.length_penalty,
                    early_stopping=self.args.early_stopping,
                    repetition_penalty=self.args.repetition_penalty,
                    do_sample=self.args.do_sample,
                    top_k=self.args.top_k,
                    top_p=self.args.top_p,
                    num_return_sequences=self.args.num_return_sequences,
                )

            all_outputs.extend(outputs.cpu().numpy())

        if self.args.use_multiprocessed_decoding:
            self.model.to("cpu")
            with Pool(self.args.process_count) as p:
                outputs = list(
                    tqdm(
                        p.imap(self._decode, all_outputs, chunksize=self.args.multiprocessing_chunksize),
                        total=len(all_outputs),
                        desc="Decoding outputs",
                        disable=self.args.silent,
                    )
                )
            self._move_model_to_device()
        else:
            outputs = [
                self.decoder_tokenizer.decode(output_id, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                for output_id in all_outputs
            ]

        if self.args.num_return_sequences > 1:
            return [
                outputs[i: i + self.args.num_return_sequences]
                for i in range(0, len(outputs), self.args.num_return_sequences)
            ]
        else:
            return outputs


    def _decode(self, output_id):
        return self.decoder_tokenizer.decode(output_id, skip_special_tokens=True, clean_up_tokenization_spaces=True)

    def compute_metrics(self, labels, preds, **kwargs):

        assert len(labels) == len(preds)
        acc = 0
        total_count = 0
        results = {}
        for sentence_i, sentence_j in zip(labels, preds):
            sentence_i = sentence_i.strip()
            sentence_i = sentence_i.replace(".", " .")
            sentence_i = sentence_i.replace(",", " ,")
            sentence_i = sentence_i.replace("?", " ?")
            total_count += len(sentence_i.split())
            print(sentence_i.split())
            print(sentence_j.split())
            print('-------')
            for word_i, word_j in zip(sentence_i.split(), sentence_j.split()):
                if word_i == word_j:
                    acc += 1
        results['acc'] = acc / total_count


        return results


    def load_and_cache_examples(self, data_1, data_2, evaluate=False, no_cache=False, verbose=True, silent=False):

        encoder_tokenizer = self.encoder_tokenizer
        decoder_tokenizer = self.decoder_tokenizer
        args = self.args

        if not no_cache:
            no_cache = args.no_cache

        if not no_cache:
            os.makedirs(self.args.cache_dir, exist_ok=True)

        mode = "dev" if evaluate else "train"

        if args.dataset_class:  
            CustomDataset = args.dataset_class
            return CustomDataset(encoder_tokenizer, decoder_tokenizer, args, data_1, data_2, mode)
        else:
            if args.model_type in ["bart", "marian", "blender", "blender-large"]:
                return SimpleSummarizationDataset(encoder_tokenizer, self.args, data_1, data_2, mode) 
            else:
                return Seq2SeqDataset(encoder_tokenizer, decoder_tokenizer, self.args, data_1, data_2,
                                      mode, )  

  
    def _create_training_progress_scores(self, **kwargs):
        extra_metrics = {key: [] for key in kwargs}
        training_progress_scores = {
            "global_step": [],
            "eval_loss": [],
            "train_loss": [],
            "eval_acc_1": [],
            "eval_acc_2":[],
            **extra_metrics,
        }

        return training_progress_scores

   
    def _get_last_metrics(self, metric_values):
        return {metric: values[-1] for metric, values in metric_values.items()}

 
    def _save_model(self, output_dir=None, optimizer=None, scheduler=None, model=None, results=None):
        if not output_dir:  
            output_dir = self.args.output_dir
        os.makedirs(output_dir, exist_ok=True) 

        logger.info(f"Saving model into {output_dir}")

        if model and not self.args.no_save:  
            # Take care of distributed/parallel training

            model_to_save = model.module if hasattr(model, "module") else model

            self._save_model_args(output_dir)  

            if self.args.model_type in ["bart", "marian", "blender", "blender-large"]:
                os.makedirs(os.path.join(output_dir), exist_ok=True)
                model_to_save.save_pretrained(output_dir) 


                self.config.save_pretrained(output_dir) 
                if self.args.model_type in ["bart", "blender", "blender-large"]:
                    self.encoder_tokenizer.save_pretrained(output_dir) 
            else:
                os.makedirs(os.path.join(output_dir, "encoder"), exist_ok=True)
                os.makedirs(os.path.join(output_dir, "decoder"), exist_ok=True)
                self.encoder_config.save_pretrained(os.path.join(output_dir, "encoder")) 
                self.decoder_config.save_pretrained(os.path.join(output_dir, "decoder")) 

                model_to_save = (
                    self.model.encoder.module if hasattr(self.model.encoder, "module") else self.model.encoder
                )
                model_to_save.save_pretrained(os.path.join(output_dir, "encoder"))
               

                model_to_save = (
                    self.model.decoder.module if hasattr(self.model.decoder, "module") else self.model.decoder
                )

                model_to_save.save_pretrained(os.path.join(output_dir, "decoder"))
              
                self.encoder_tokenizer.save_pretrained(os.path.join(output_dir, "encoder"))  
                self.decoder_tokenizer.save_pretrained(os.path.join(output_dir, "decoder"))  

            torch.save(self.args, os.path.join(output_dir, "training_args.bin"))
       
            if optimizer and scheduler and self.args.save_optimizer_and_scheduler:
                torch.save(optimizer.state_dict(), os.path.join(output_dir, "optimizer.pt"))
             
                torch.save(scheduler.state_dict(), os.path.join(output_dir, "scheduler.pt"))
             
        if results: 
            output_eval_file = os.path.join(output_dir, "eval_results.txt")
            with open(output_eval_file, "w") as writer:
                for key in sorted(results.keys()):
                    writer.write("{} = {}\n".format(key, str(results[key])))

  
    def _move_model_to_device(self):

        self.model.to(self.device)
     

   
    def _get_inputs_dict(self, batch):
        device = self.device
        if self.args.model_type in ["marian"]:
            pad_token_id = self.encoder_tokenizer.pad_token_id  
            source_ids_1 = batch["source_ids_1"]
            source_mask_1 = batch["source_mask_1"]
            y_1 = batch["target_ids_1"]
            source_ids_2 = batch["source_ids_2"]
            source_mask_2 = batch["source_mask_2"]
            y_2 = batch["target_ids_2"]

            y_1_ids = y_1[:, :-1].contiguous()
            lm_labels_1 = y_1[:, 1:].clone()
            lm_labels_1[y_1[:, 1:] == pad_token_id] = -100
            y_2_ids = y_2[:, :-1].contiguous()
            lm_labels_2 = y_2[:, 1:].clone()
            lm_labels_2[y_2[:, 1:] == pad_token_id] = -100
            inputs_1 = {
                "input_ids": source_ids_1.to(device),
                "attention_mask": source_mask_1.to(device),
                "decoder_input_ids": y_1_ids.to(device),
                "lm_labels": lm_labels_1.to(device)
            }
            inputs_2 = {
                "input_ids": source_ids_2.to(device),
                "attention_mask": source_mask_2.to(device),
                "decoder_input_ids": y_2_ids.to(device),
                "lm_labels": lm_labels_2.to(device)
            }


        elif self.args.model_type in ["blender", "bart", "blender-large"]:
            pad_token_id = self.encoder_tokenizer.pad_token_id

            source_ids_1 = batch["source_ids_1"]
            source_mask_1 = batch["source_mask_1"]
            y_1 = batch["target_ids_1"]
            source_ids_2 = batch["source_ids_2"]
            source_mask_2 = batch["source_mask_2"]
            y_2 = batch["target_ids_2"]
            y_1_ids = y_1[:, :-1].contiguous()
            labels_1 = y_1[:, 1:].clone()
            labels_1[y_1[:, 1:] == pad_token_id] = -100
            y_2_ids = y_2[:, :-1].contiguous()
            labels_2 = y_2[:, 1:].clone()
            labels_2[y_2[:, 1:] == pad_token_id] = -100
            inputs_1 = {
                "input_ids": source_ids_1.to(device),
                "attention_mask": source_mask_1.to(device),
                "decoder_input_ids": y_1_ids.to(device),
                "labels": labels_1.to(device)
            }
            inputs_2 = {
                "input_ids": source_ids_2.to(device),
                "attention_mask": source_mask_2.to(device),
                "decoder_input_ids": y_2_ids.to(device),
                "labels": labels_2.to(device)
            }
        else:

            lm_labels_1 = batch[1]
            lm_labels_masked_1 = lm_labels_1.clone()
            lm_labels_masked_1[lm_labels_masked_1 == self.decoder_tokenizer.pad_token_id] = -100
          
            inputs_1 = {
                "input_ids": batch[0].to(device),
                "decoder_input_ids": lm_labels_1.to(device),
                "labels": lm_labels_masked_1.to(device),
            }
            lm_labels_2 = batch[3]
            lm_labels_masked_2 = lm_labels_2.clone()
            lm_labels_masked_2[lm_labels_masked_2 == self.decoder_tokenizer.pad_token_id] = -100
           
            inputs_2 = {
                "input_ids": batch[2].to(device),
                "decoder_input_ids": lm_labels_2.to(device),
                "labels": lm_labels_masked_2.to(device),
            }

        return inputs_1, inputs_2


    def _save_model_args(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        self.args.save(output_dir)


    def _load_model_args(self, input_dir):
        args = Seq2SeqArgs() 
        args.load(input_dir)  
        return args  

    def get_named_parameters(self):
        return [n for n, p in self.model.named_parameters()]
