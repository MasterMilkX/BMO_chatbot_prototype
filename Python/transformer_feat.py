## FINE-TUNES A GPT-NEO MODEL TO OUTPUT NEW FEATURE RECOMMENDATIONS FROM A LIST OF TAGS AND ENTITIES
# Written by Milk
# I'm honestly skeptical this will work but fuckit

####  IMPORT PACKAGES  ####
import re
import torch
import random
import pandas as pd
from tqdm import tqdm
from torch.utils.data import Dataset
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from transformers import GPT2Tokenizer, TrainingArguments, Trainer, GPT2LMHeadModel


####   VARIABLES   ####

EPOCHS = 3
BATCH_SIZE = 2
MAX_LEN = 512

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


#### DATASET PREPROCESSING  ####

class GameFeatDataset(Dataset):
    def __init__(self, game_dat, tokenizer, max_length):
        # define variables    
        self.input_ids = []
        self.attn_masks = []
        self.labels = []

        # iterate through the dataset
        for k in game_dat.keys():
            # get the tags, entities, and features
            tag = game_dat[k]["tags"]
            entity = game_dat[k]["entities"]
            feats = game_dat[k]["features"]
            feat_txt = "\n".join(feats)

            # prepare the game data set
            prep_txt = f'<|startoftext|>{tag}\n{entity}\n{feat_txt}<|endoftext|>'

            # tokenize
            encodings_dict = tokenizer(prep_txt, truncation=True, max_length=max_length, padding="max_length")

            # append to list
            self.input_ids.append(torch.tensor(encodings_dict['input_ids']))
            self.attn_masks.append(torch.tensor(encodings_dict['attention_mask']))
            self.labels.append(f"{k} - {len(feats)}")  #not really used - just for counting + debugging

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.attn_masks[idx], self.labels[idx]

# Data load function
def load_game_dataset(tokenizer):
    # load dataset and sample 10k reviews.
    file_path = "data/game_trans_train_datfeat.txt"
    DAT = {}
    with open(file_path, "r") as f:
        lines = [l.strip() for l in f.readlines()]
        CUR_GAME = ""
        for l in lines:
            # empty line (between entries)
            if l == "":
                continue
            #new entry
            else:
                if l[0] == "+":
                    CUR_GAME = l[2:]
                    DAT[CUR_GAME] = {"tags":[],"entities":[],"features":[]}
                elif l[0] == "#":
                    DAT[CUR_GAME]["tags"] = l[2:]
                elif l[0] == "@":
                    DAT[CUR_GAME]["entities"] = l[2:]
                else:
                    DAT[CUR_GAME]["features"].append(l)

    # # divide into test and train and eval
    # X_train_k, X_test_k = train_test_split(list(DAT.keys()), shuffle=True, test_size=0.05, random_state=1)
    # X_train_k, X_eval_k = train_test_split(X_train_k, shuffle=True, test_size=0.2, random_state=1)

    # train_gdat = {k:DAT[k] for k in X_train_k}
    # eval_gdat = {k:DAT[k] for k in X_eval_k}
    # test_gdat = {k:DAT[k] for k in X_test_k}

    # # format into SentimentDataset class
    # train_dataset = GameFeatDataset(train_gdat, tokenizer, max_length=512)
    # eval_dataset = GameFeatDataset(eval_gdat, tokenizer,max_length=512)

    # # return
    # return train_dataset, eval_dataset, test_gdat

    # train on everything heheh
    return GameFeatDataset(DAT, tokenizer, max_length=MAX_LEN)



####  MODEL TRAINING  ####

## Load model and data
#--------

# set model name
model_name = "gpt2"
# seed
torch.manual_seed(42)

# load tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained(model_name, bos_token='<|startoftext|>',eos_token='<|endoftext|>', pad_token='<|pad|>')
model = GPT2LMHeadModel.from_pretrained(model_name).to(DEVICE)
model.resize_token_embeddings(len(tokenizer))

# prepare and load dataset
# train_dataset, eval_dataset, test_dataset = load_game_dataset(tokenizer)
train_dataset = load_game_dataset(tokenizer)
custom_games = {"skateboard":{"tags":'SKATEBOARDING,CYBERPUNK',"entities":'pixel,future',"features":["fight the corporations", "vandalize properties", "ride your hoverboard", "race the street gangs", "upgrade your tech"]},
                "dungeon":{"tags":'DUNGEON,ADVENTURE',"entities":'dungeon,monster,hero,loot,traps',"features":["fight the monsters", "collect the loot", "explore the dungeon", "upgrade your gear", "find the exit"]},
                "mall":{"tags":"PHYSICS, 90s, RETRO", "entities":"mall,shopping,simulator", "features":["buy the random junk", "shop for the holidays", "find the best deals", "fight other shoppers", "escape the mall cops"]}}
eval_dataset = GameFeatDataset(custom_games, tokenizer, max_length=MAX_LEN)


## Train
#--------

# creating training arguments
training_args = TrainingArguments(output_dir='TRANSFORMER/results', num_train_epochs=EPOCHS, logging_steps=10,
                                 load_best_model_at_end=True, save_strategy="epoch", evaluation_strategy="epoch",
                                 per_device_train_batch_size=BATCH_SIZE, per_device_eval_batch_size=BATCH_SIZE,
                                 warmup_steps=100, weight_decay=0.01, logging_dir='logs')

# start training
Trainer(model=model, args=training_args, train_dataset=train_dataset, eval_dataset=eval_dataset,
        data_collator=lambda data: {'input_ids': torch.stack([f[0] for f in data]),
                                    'attention_mask': torch.stack([f[1] for f in data]),
                                    'labels': torch.stack([f[0] for f in data])}).train()


## Test
#----------

# set the model to eval mode
_ = model.eval()

# create prompt (in compliance with the one used during training)
TEST_TAG = 'CUTE,RELAXING,ATMOSPHERIC,RPG'
TEST_ENTITY = 'farming,animal,characters'

prompt = f'<|startoftext|>{TEST_TAG}\n{TEST_ENTITY}\n-'
generated = tokenizer(f"{prompt}", return_tensors="pt").input_ids.to(DEVICE)

# perform prediction
sample_outputs = model.generate(generated, do_sample=False, top_k=50, max_length=MAX_LEN, top_p=1, temperature=0.75, pad_token_id=tokenizer.convert_tokens_to_ids('<|pad|>'))

# decode the predicted tokens into texts
pred_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)

# print the predicted text
print(pred_text)
