from utilFuncs.dataUtils import *


def loadTokenizerAndSeq2SeqLM(tokenizer_repo, model_repo, use_pretrained = False, DEVICE = DEVICE):

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_repo)

    if (use_pretrained):
        model = AutoModelForSeq2SeqLM.from_pretrained(model_repo)
    else:
        config = AutoConfig.from_pretrained(model_repo)
        model = AutoModelForSeq2SeqLM.from_config(config)

    model.to(DEVICE)

    return tokenizer, model


def encode_str(text, text_target,
               tokenizer, add_lang_token, target_lang,
               MAX_SEQ_LEN,
               LANG_TOKEN_MAPPING = LANG_TOKEN_MAPPING,
               DEVICE = DEVICE):

    if (add_lang_token):
        target_lang_token = LANG_TOKEN_MAPPING[target_lang]
        text = target_lang_token + text

    tokenizerOutp = tokenizer(
        text=text,
        text_target=text_target,
        return_tensors='pt',
        padding='max_length',
        truncation=True,
        max_length=MAX_SEQ_LEN).to(DEVICE)

    return (tokenizerOutp['input_ids'][0], tokenizerOutp['labels'][0], tokenizerOutp['attention_mask'][0])

def format_translation_data(translations,
                            tokenizer, set_tokenizer_lang, add_lang_token,
                            MAX_SEQ_LEN,
                            input_lang, target_lang, random_lang,
                            LANGS = LANGS):

    if (random_lang):
        input_lang, target_lang = np.random.choice(LANGS, size=len(LANGS), replace=False)

    assert len(translations.keys()) != 0

    if (len(translations.keys()) == 1):
        input_text = translations[input_lang]
        target_text = ""
    else:
        input_text = translations[input_lang]
        target_text = translations[target_lang]

    if input_text is None or target_text is None:
        return None

    if (set_tokenizer_lang):
        tokenizer.src_lang = input_lang
        tokenizer.tgt_lang = target_lang

    input_token_ids, target_token_ids, attention_mask = encode_str(
        input_text, target_text,
        tokenizer, add_lang_token, target_lang,
        MAX_SEQ_LEN,
    )

    return input_token_ids, target_token_ids, attention_mask


def transform_batch(batch,
                    tokenizer, set_tokenizer_lang, add_lang_token,
                    MAX_SEQ_LEN,
                    input_lang, target_lang, random_lang,
                    DEVICE = DEVICE):

    inputs = []
    targets = []
    attentionMask = []

    for translation_set in batch['translation']:
        formatted_data = format_translation_data(
            translation_set,
            tokenizer, set_tokenizer_lang, add_lang_token,
            MAX_SEQ_LEN,
            input_lang, target_lang, random_lang
        )

        if (formatted_data is None):
            continue

        input_ids, target_ids, attention_mask = formatted_data

        inputs.append(input_ids.unsqueeze(0))
        targets.append(target_ids.unsqueeze(0))
        attentionMask.append(attention_mask.unsqueeze(0))

    batch_input_ids = torch.cat(inputs).to(DEVICE)
    batch_target_ids = torch.cat(targets).to(DEVICE)
    attentionMask = torch.cat(attentionMask).to(DEVICE)

    return batch_input_ids, batch_target_ids, attentionMask


def get_data_generator(dataset,
                       tokenizer, set_tokenizer_lang, add_lang_token,
                       MAX_SEQ_LEN,
                       input_lang = None, target_lang = None, random_lang = False,
                       batch_size = 16,
                       shuffle = True):

    assert (((input_lang is not None) & (target_lang is not None) & (not (random_lang)))
            | ((input_lang is None) & (target_lang is None) & (random_lang)))

    if (shuffle):
        dataset = dataset.shuffle()

    for i in range(0, len(dataset), batch_size):
        raw_batch = dataset[i : i + batch_size]
        yield transform_batch(raw_batch,
                              tokenizer, set_tokenizer_lang, add_lang_token,
                              MAX_SEQ_LEN,
                              input_lang, target_lang, random_lang)


def eval_model(model, eval_dataset,
               tokenizer, set_tokenizer_lang, add_lang_token,
               MAX_SEQ_LEN,
               input_lang, target_lang, random_lang,
               batch_size, max_iters=8):

    model.eval()
    eval_generator = get_data_generator(eval_dataset,
                                        tokenizer, set_tokenizer_lang, add_lang_token,
                                        MAX_SEQ_LEN,
                                        input_lang, target_lang, random_lang,
                                        batch_size = batch_size
                                        )
    eval_losses = []
    for i, (input_batch, label_batch, attention_mask_batch) in enumerate(eval_generator):
        if i >= max_iters:
            break

        model_out = model(
            input_ids=input_batch,
            labels=label_batch,
            attention_mask=attention_mask_batch
        )
        eval_losses.append(model_out.loss.item())

    return np.mean(eval_losses)


def add_lang_tokens_to_tokenizer(tokenizer, model, LANG_TOKEN_MAPPING = LANG_TOKEN_MAPPING):

    special_tokens_dict = {
        'additional_special_tokens': list(LANG_TOKEN_MAPPING.values())
    }

    tokenizer.add_special_tokens(special_tokens_dict)
    model.resize_token_embeddings(len(tokenizer))

    pass


def train(model,
          tokenizer, set_tokenizer_lang, add_lang_token,
          MAX_SEQ_LEN,
          input_lang, target_lang, random_lang,
          batch_size,
          optimizer, scheduler,
          n_epochs, n_batches,
          train_dataset, eval_dataset,
          print_freq, checkpoint_freq,
          model_checkpoint, model_path):

    losses = []
    valLosses = [1e18]

    for epoch_idx in range(n_epochs):
        # Randomize data order
        data_generator = get_data_generator(train_dataset,
                                            tokenizer, set_tokenizer_lang, add_lang_token,
                                            MAX_SEQ_LEN,
                                            input_lang, target_lang, random_lang,
                                            batch_size = batch_size)

        for batch_idx, (input_batch, label_batch, attention_mask_batch) \
                in tqdm_notebook(enumerate(data_generator), total=n_batches):

            model.train()
            optimizer.zero_grad()

            # Forward pass
            model_out = model(
                input_ids=input_batch,
                labels=label_batch,
                attention_mask=attention_mask_batch)

            # Calculate loss and update weights
            loss = model_out.loss
            losses.append(loss.item())
            loss.backward()
            optimizer.step()
            scheduler.step()

            # Print training update info
            if (batch_idx + 1) % print_freq == 0:
                avg_loss = np.mean(losses[-print_freq:])
                print('Epoch: {} | Step: {}/{} | Avg. loss: {:.3f} | lr: {}'.format(
                    epoch_idx + 1, batch_idx + 1, n_batches, avg_loss, scheduler.get_last_lr()[0]))

            if (batch_idx + 1) % checkpoint_freq == 0:
                eval_loss = eval_model(model, eval_dataset)
                valLosses.append(eval_loss)
                print('Eval loss {:.3f}'.format(eval_loss))
                if (eval_loss <= min(valLosses)):
                    print('Saving checkpoint...')
                    torch.save(model.state_dict(), model_checkpoint)

        valLosses.pop(0)
        torch.save(model.state_dict(), model_path.format(epoch_idx + 1))

    return losses, valLosses


def plotLoss(losses, smoothing_window_size):

    assert smoothing_window_size >= 1
    assert len(losses) > smoothing_window_size

    smoothed_losses = []
    for i in range(len(losses) - smoothing_window_size):
        smoothed_losses.append(np.mean(losses[i:i + smoothing_window_size]))

    plt.plot(smoothed_losses)


def inference(model, inference_dataset,
              tokenizer, set_tokenizer_lang, add_lang_token,
              MAX_SEQ_LEN,
              input_lang, target_lang, random_lang,
              batch_size,
              num_beams = 1, num_return_sequences = 1,
              forced_bos = False):

    model.eval()
    inference_generator = get_data_generator(inference_dataset,
                                             tokenizer, set_tokenizer_lang, add_lang_token,
                                             MAX_SEQ_LEN,
                                             input_lang, target_lang, random_lang,
                                             batch_size = batch_size,
                                             shuffle = False
                                             )

    outputSentenceList = []
    for i, (input_batch, _, attention_mask_batch) in enumerate(inference_generator):
        if (not(forced_bos)):
            sentence = model.generate(
                input_batch,
                num_beams=num_beams, num_return_sequences=num_return_sequences,
                max_new_tokens=MAX_SEQ_LEN
            )
        else:
            sentence = model.generate(
                input_batch,
                num_beams = num_beams, num_return_sequences = num_return_sequences,
                max_new_tokens = MAX_SEQ_LEN,
                forced_bos_token_id = tokenizer.get_lang_id(target_lang)
            )
        sentence = tokenizer.batch_decode(
            sentence, skip_special_tokens = True
        )
        outputSentenceList = outputSentenceList + sentence

    print('Inference process finished with %d sentences' % (len(outputSentenceList)))

    return outputSentenceList



