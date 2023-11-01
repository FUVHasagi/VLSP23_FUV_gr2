from utilFuncs.libsImport import *

CUR_DIR = os.getcwd()
print('Current directory: %s' % (CUR_DIR))

DEVICE = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
print("Using device: %s" % (DEVICE))

BLEU = bleu = evaluate.load("bleu")
SACREBLEU = evaluate.load("sacrebleu")

NP_SEED = 14

ALL_EMOJI = list(emoji.EMOJI_DATA.keys())
ALL_EMOJI.append("♡")
ALL_EMOJI.append("★")
ALL_EMOJI.append("=)")  # TODO: HANDLE LONGER CASE =))))))
ALL_EMOJI.append(":)")  # TODO: HANDLE LONGER CASE :))))))
ALL_EMOJI.append("^ _ ^")
# ALL_EMOJI.append("^^")
ALL_EMOJI.append("⚘")
ALL_EMOJI.append("☆")
ALL_EMOJI.append("◆")
ALL_EMOJI.append("·")
ALL_EMOJI.append("•")
ALL_EMOJI.append("●")
ALL_EMOJI.append("⊡")
ALL_EMOJI.append("▼")
ALL_EMOJI.append("…")

FONT_ERRORS = ["�", ""]

ALL_NUM = '0123456789'

VI_ALL = 'AĂÂBCDĐEÊGHIKLMNOÔƠPQRSTUƯVXYÁÀẢÃẠẮẰẲẴẶẤẦẨẪẬÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴaăâbcdđeêghiklmnoôơpqrstuưvxyáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ'
EXTRA_LETTER = 'fjwzFJWZ'
VI_ALL = VI_ALL + EXTRA_LETTER + ALL_NUM

SPECIAL_SPACING = [' ', '​', '﻿']

LANG_TOKEN_MAPPING = {
    'vi': '<|__vi__|> ',
    'lo': '<|__lo__|> ',
}

LANGS = list(LANG_TOKEN_MAPPING.keys())



