''''
    IMAGE CAPTION ATTENTION MODEL
    by Milk
    Modified from this tutorial: https://towardsdatascience.com/image-captions-with-attention-in-tensorflow-step-by-step-927dad3569fa

    For use with sprites specifically but generates captions for an image based on some input label
'''


####################          IMPORTS          ####################

import numpy as np
import matplotlib.pyplot as plt
import random
import math
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, colorConverter
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import re
import time
import os

# tensorflow
import tensorflow as tf

# PICO-8 Palette => use colormap for matplotlib
PICO_PALETTE = ['#000000','#1D2B53','#7E2553','#008751','#AB5236','#5F574F','#C2C3C7','#FFF1E8','#FF004D','#FFA300','#FFEC27','#00E436','#29ADFF','#83769C','#FF77A8','#FFCCAA']


####################          MODEL DEFINITIONS          ####################


######    SUB-MODEL DESIGN    ######

# creates the attention model
class Attention_B2(tf.keras.Model):
    def __init__(self,units):
        super(Attention_B2,self).__init__()
        self.W1 = tf.keras.layers.Dense(units)
        self.W2 = tf.keras.layers.Dense(units)
        self.V = tf.keras.layers.Dense(1)

    def call(self,features,hidden):
        hidden_w_time_axis = tf.expand_dims(hidden,1)  
        attn_hidden_layer = (tf.nn.tanh(self.W1(features) + self.W2(hidden_w_time_axis)))
        score = self.V(attn_hidden_layer)

        attention_weights = tf.nn.softmax(score,axis=1)

        context_vector = attention_weights * features
        context_vector = tf.reduce_sum(context_vector,axis=1)

        return context_vector, attention_weights
    
# encoder layer for the image
class Encoder_B2(tf.keras.Model):
    def __init__(self,embed_dim):
        super(Encoder_B2,self).__init__()
        self.fc = tf.keras.layers.Dense(embed_dim)

    def call(self,x):
        x = self.fc(x)
        x = tf.nn.relu(x)
        return x
    
    # import / export
    def importWeights(self,weights):
        self.set_weights(weights)
    
    def exportWeights(self):
        return self.get_weights()
    
# decoder using the attention
class Decoder_B2(tf.keras.Model):
    def __init__(self, embed_dim, units, vocab_size):
        super(Decoder_B2, self).__init__()
        self.units = units

        self.embedding = tf.keras.layers.Embedding(vocab_size, embed_dim)
        self.gru = tf.keras.layers.GRU(self.units,return_sequences=True,return_state=True,recurrent_initializer='glorot_uniform')
        self.fc1 = tf.keras.layers.Dense(self.units)
        self.fc2 = tf.keras.layers.Dense(vocab_size)

        self.attention = Attention_B2(self.units)

    def call(self,x,features,hidden):
        ctx_vec, attn_weights = self.attention(features,hidden)
        x = self.embedding(x)
        x = tf.concat([tf.expand_dims(ctx_vec,1),x],axis=-1)
        output, state = self.gru(x)
        x = self.fc1(output)
        x = tf.reshape(x,(-1,x.shape[2]))
        x = self.fc2(x)
        return x, state, attn_weights
    
    def reset_state(self,batch_size):
        return tf.zeros((batch_size,self.units))
    
    # import / export
    def importWeights(self,weights):
        self.set_weights(weights)
    
    def exportWeights(self):
        return self.get_weights()






# Image captioning attention model
class ImgCapAttnModel():
    # initialization process - assume the following format
    # imgs: [N, (H*W), C] - one hot encoded images/sprites sequenced py pixel then channel
    # captions: [N,[c per img]] - text captions
    def __init__(self,imgs_in,captions,batch_size=32,embed_dim=256,units=512,debug=False):
        self.batch_size = batch_size
        self.debug = debug
        self.embed_dim = embed_dim
        self.units = units

        self.VOCAB = ["<pad>","<start>","<end>","<unk>"]
        self.seq_len = 0

        # if the input images are in the form (n,w,h,c), convert to (n,w*h,c)
        imgs = imgs_in.copy()
        if len(imgs.shape) == 4:
            print("> Reshaping images to (n,w*h,c)")
            imgs = np.reshape(imgs,(imgs.shape[0],imgs.shape[1]*imgs.shape[2],imgs.shape[3]))
        
        self._tokenizeCaptions(captions)                            # tokenize the captions
        _, dat_size = self._makeDataset(imgs,captions,batch_size=batch_size)      # make the dataset

        # make the sub-models
        self.encoder = Encoder_B2(embed_dim)
        self.decoder = Decoder_B2(embed_dim,units,len(self.VOCAB))
        self.optimizer = tf.keras.optimizers.Adam()
        self.loss_object = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True,reduction='none')

        # make other network parameters
        self.num_steps = dat_size // batch_size
        self.features_shape = imgs.shape[2]  # channels
        self.attn_feat_shape = imgs.shape[1]  # image dimension area







    ######    CAPTION TOKENIZATION    ######
    
    # creates a vocab from the list of captions
    def _makeVocab(self, captions, stopwords=[], min_freq=1):
        # convert 1-1 captions to 1-N captions
        cap_set = captions.copy()
        if type(cap_set[0]) == np.str_ or type(cap_set[0]) == str:
            cap_set = np.array([[c] for c in cap_set])

        # print(cap_set)

        # preprocess the descriptions
        proc_desc = []
        self.seq_len = 0
        vocab = ["<pad>","<start>","<end>","<unk>"]
        print("> Preprocessing descriptions for tokenization")
        with tqdm(total=len(cap_set)) as pbar:
            for desc_set in cap_set:
                for desc in desc_set:
                    # remove punctuation with regex
                    desc2 = re.sub('[\.\?\,]','',desc)
                    desc2 = re.sub('[\-]',' ',desc2)

                    # add start and end tokens
                    desc3 = "<start> " + desc2 + " <end>"

                    # add to vocab for tokenization
                    words = desc3.split()
                    vocab.extend(words)

                    # set the longest caption sequence
                    if len(words) > self.seq_len:
                        self.seq_len = len(words)
                    
                    proc_desc.append(desc3)
                    pbar.update(1)

        # create the vocab
        vocab, cts = np.unique(vocab, return_counts=True)
        FULL_VOCAB = ["<pad>","<start>","<end>","<unk>"]
        for v,c in zip(vocab,cts):
            if v in FULL_VOCAB:  #skip, already added
                continue
            if v in stopwords:   #skip, stopword
                continue
            if c < min_freq:     #skip, not frequent enough
                continue

            FULL_VOCAB.append(v)

        # print
        if self.debug:
            print(f"Vocab size: {len(FULL_VOCAB)}")
            print(f"Vocab (1st 10): {FULL_VOCAB[:10]}")
            print(f"Longest description: {self.seq_len}")

        # set the vocab
        self.VOCAB = FULL_VOCAB.copy()
        return FULL_VOCAB, self.seq_len

    # tokenzies a description based on the vocab
    def tok(self, desc, add_start_end=True):
        desc_tok = []
        words = desc.split()
        end = len(words) if len(words) < self.seq_len else self.seq_len

        # add start token
        if add_start_end:
            desc_tok.append(self.VOCAB.index("<start>"))
        # add vocab index
        for i in range(self.seq_len):
            # add end if self.seq_len
            if i == end and add_start_end:
                desc_tok.append(self.VOCAB.index("<end>"))
                continue

            # add the word or padding
            if i < len(desc.split()):
                desc_tok.append(self.VOCAB.index(words[i]) if words[i] in self.VOCAB else self.VOCAB.index("<unk>"))
            else:
                desc_tok.append(0)  # assume <pad> token is 0
        return desc_tok
    

    # untokenizes a description based on the vocab
    def untok(self, toks):
        desc = ""
        for t in toks:
            if t == 0:
                continue
            desc += self.VOCAB[t] + " "
        return desc.strip()
    
    # tokenizes the captions passed
    def _tokenizeCaptions(self, captions, stop_words=[], min_freq=1, debug=False):
        # convert 1-1 captions to 1-N captions
        cap_set = captions.copy()
        if type(cap_set[0]) == np.str_ or type(cap_set[0]) == str:
            cap_set = np.array([[c] for c in cap_set])

        # create the vocab if not already
        if self.VOCAB == ["<pad>","<start>","<end>","<unk>"]:
            print(f"> Creating vocab from captions")
            self._makeVocab(cap_set,stopwords=stop_words,min_freq=min_freq)

        # tokenize the captions
        print("> Tokenizing captions")
        self.TOK_CAP = []
        with tqdm(total=len(cap_set)) as pbar:
            for cs in cap_set:
                self.TOK_CAP.append([self.tok(cap) for cap in cs])
                pbar.update(1)
        return self.TOK_CAP






    ######    DATASET PREPROCESSING    ######

    # preprocesses the PICO-8 
    def _makeDataset(self, imgs, captions=None, buffer_size=1024, batch_size=32):
        # check if the tokenized captions are already made
        if self.TOK_CAP == []:
            if captions == None:
                raise Exception("No captions passed to preprocess the dataset")
            print("> Tokenizing captions")
            self._tokenizeCaptions(captions)
        
        # create the dataset
        x_dat = []
        y_dat = []

        # assume the format is img: [n,h*w,(c)] and cap: [n,[c per img]]
        print("> Creating dataset")
        with tqdm(total=len(imgs)) as pbar:
            for img, cap_set in zip(imgs,self.TOK_CAP):
                # assign the sprite to each caption in the set
                for cap in cap_set:
                    x_dat += [img]
                    y_dat += [cap]
                pbar.update(1)

        # create a tensorflow dataset
        x_dat = np.array(x_dat)
        y_dat = np.array(y_dat)

        dataset = tf.data.Dataset.from_tensor_slices((x_dat,y_dat))
        dataset = dataset.shuffle(buffer_size=buffer_size).batch(batch_size)
        dataset = dataset.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)

        # assign the dataset
        self.TF_DAT = dataset
        return dataset, len(x_dat)




    ######    MODEL TRAINING    ######

    # set up the loss function
    def loss(self, real, pred):
        mask = tf.math.logical_not(tf.math.equal(real, 0))
        loss_ = self.loss_object(real, pred)

        mask = tf.cast(mask, dtype=loss_.dtype)
        loss_ *= mask

        return tf.reduce_mean(loss_)
    

    # set up the training step
    @tf.function
    def train_step(self, img_tensor, target):
        loss = 0

        # initializing the hidden state for each batch
        # because the captions are not related from image to image
        hidden = self.decoder.reset_state(batch_size=target.shape[0])
        dec_input = tf.expand_dims([self.VOCAB.index('<start>')] * target.shape[0], 1)

        with tf.GradientTape() as tape:
            features = self.encoder(img_tensor)
            for i in range(1, target.shape[1]):
                predictions, hidden, _ = self.decoder(dec_input, features, hidden)   # passing the features through the decoder
                loss += self.loss(target[:, i], predictions)
                dec_input = tf.expand_dims(target[:, i], 1)    # using teacher forcing

        total_loss = (loss / int(target.shape[1]))

        trainable_variables = self.encoder.trainable_variables + self.decoder.trainable_variables
        gradients = tape.gradient(loss, trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, trainable_variables))

        return loss, total_loss
    

    # train the model from scratch
    def _TRAIN(self,EPOCHS,loss_plot_path=None):
        self.loss_plt = []
        
        with tqdm(total=EPOCHS) as pbar:
            for e in range(EPOCHS):
                start = time.time()
                total_loss = 0

                # go through each batch
                for (batch, (img_tensor, target)) in enumerate(self.TF_DAT):
                    batch_loss, t_loss = self.train_step(img_tensor, target)
                    total_loss += t_loss

                pbar.set_description(f"Epoch:{e+1} +=+ Total Loss:{batch_loss.numpy() / int(target.shape[1]):.4f} +=+ TIME: {(time.time()-start):.2f} sec")
                self.loss_plt += [total_loss / self.num_steps]

            
                pbar.update(1)

        # save the loss plot if a path is passed
        if loss_plot_path != None:
            plt.plot(self.loss_plt)
            plt.title('Loss Plot')
            plt.xlabel('Epochs')
            plt.ylabel('Loss')
            plt.legend()
            plt.savefig(loss_plot_path)
            plt.close()








    #####    MODEL TESTING    #####

    # predict a caption from an image - also returns the attention layers for each word
    def _EVALUATE(self, image):
        attention_plot = np.zeros((self.seq_len,self.attn_feat_shape))

        hidden = self.decoder.reset_state(batch_size=1)   # reset the hidden state

        # turn the image into (w*h,c) if it isn't already
        if len(image.shape) == 3:
            img_tensor_val = tf.reshape(image,(1,image.shape[0]*image.shape[1],image.shape[2]))
        else:
            img_tensor_val = tf.expand_dims(image,0)
        features = self.encoder(img_tensor_val)

        # begin the sequence
        dec_input = tf.expand_dims([self.VOCAB.index('<start>')],0)
        pred_seq = []

        # go through each word in the sequence
        for i in range(self.seq_len):
            predictions, hidden, attention_weights = self.decoder(dec_input,features,hidden)

            attention_plot[i] = tf.reshape(attention_weights,(-1,)).numpy()

            predicted_id = tf.random.categorical(predictions,1)[0][0].numpy()
            pred_seq.append(self.VOCAB[predicted_id])

            if self.VOCAB[predicted_id] == '<end>':
                return pred_seq, attention_plot

            dec_input = tf.expand_dims([predicted_id],0)

        attention_plot = attention_plot[:len(pred_seq),:]
        return pred_seq, attention_plot








    #####    MODEL SAVING + LOADING    #####

      
    # export the model (somehow idk) - saves both the encoder and decoder to a folder to import later
    def _EXPORT(self,model_dir):
        # create the directory if it doesn't exist
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        # save the encoder and decoder - (i love copilot)
        print(f"> Saving model to [{model_dir}/encoder] and [{model_dir}/decoder]")
        self.encoder.save_weights(os.path.join(model_dir,"encoder"))
        self.decoder.save_weights(os.path.join(model_dir,"decoder"))

        # export the vocab
        print(f"> Exporting vocab to [{os.path.join(model_dir,'vocab.txt')}]")
        with open(os.path.join(model_dir,"vocab.txt"),"w") as f:
            f.write("\n".join(self.VOCAB))

    # import the model from a directory
    def _IMPORT(self,model_dir):
        # load the encoder and decoder
        self.encoder.load_weights(os.path.join(model_dir,"encoder"))
        self.decoder.load_weights(os.path.join(model_dir,"decoder"))

        # load the vocab
        with open(os.path.join(model_dir,"vocab.txt"),"r") as f:
            self.VOCAB = f.read().split("\n")




########        OTHER HELPFUL FUNCTIONS        ########

# plot the attention weights onto the image
def plot_attention(image,result,attention_plot):
    spr = image
    fig = plt.figure(figsize=(20,10))
    colormap = ListedColormap(PICO_PALETTE,N=len(PICO_PALETTE))

    # shows values closer to 0 as black and values closer to 1 as transparent (or image color behind it)
    alpha_cmap = LinearSegmentedColormap.from_list('rb_cmap',[colorConverter.to_rgba('black',alpha = 1),colorConverter.to_rgba('black',alpha = 0)])

    len_result = len(result)
    col = 8
    for l in range(len_result):
        temp_att = np.resize(attention_plot[l],(8,8))
        ax = fig.add_subplot(int(len(result) / col) + 1, col, l + 1)
        ax.set_title(result[l])
        ax.imshow(spr.squeeze(),cmap=colormap,vmin=0,vmax=len(PICO_PALETTE)-1)
        ax.imshow(temp_att,cmap=alpha_cmap)     # 0 - not highlighteed, 1 - highlighted; color shown means attention
        ax.axis('off')

    plt.tight_layout()
    return fig




########        MAIN FUNCTION        ########

# test the attention model functions with the pico shape dataset

# TESTS = []
TESTS = ['train', 'export', 'eval']
# TESTS = ['import', 'eval']

if __name__ == '__main__':
    # import from .npz file
    shape_data = np.load("../data/rip_data/shapes.npz")
    labels = shape_data['shape_labels']
    images = shape_data['shape_imgs_1h']

    # create the model
    test_model = ImgCapAttnModel(images,labels, batch_size=16)

    # print(test_model.VOCAB)
    # print(test_model.TOK_CAP)

    # train the model
    if 'train' in TESTS:
        test_model._TRAIN(20)

    # save the model
    if 'export' in TESTS:
        test_model._EXPORT("../models/attention/shape_attn_model")

    # load the model
    if 'import' in TESTS:
        test_model._IMPORT("../models/attention/shape_attn_model")

    # print(test_model.VOCAB)
    # print(test_model.TOK_CAP)

    # evaluate the model
    if 'eval' in TESTS:
        print("real: ",labels[0])
        print("pred: ", test_model._EVALUATE(images[0])[0])



